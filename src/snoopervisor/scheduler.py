"""Scheduler for running watchers and sending notifications."""

import logging
from datetime import datetime, timedelta
from time import sleep
from typing import Callable, Dict, List, Tuple

import pycron

from snoopervisor.config import settings
from snoopervisor.notifiers.notifier import Notifier
from snoopervisor.notifiers.slack_notifier import SlackNotifier
from snoopervisor.watchers.cpu_watcher import CPUWatcher
from snoopervisor.watchers.memory_watcher import MemoryWatcher, memory_watcher_formatter
from snoopervisor.watchers.watcher import Watcher


def noop_formatter(usage: float) -> float:
    """No operation formatter, returns the usage as is."""
    return usage


class Scheduler:
    # pylint: disable=too-few-public-methods, too-many-positional-arguments, too-many-arguments
    """Scheduler for running watchers and sending notifications."""

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__ignore_users = settings.users.ignore or set()

        self.__notifiers = self.__get_notifiers()
        self.__watchers = self.__get_watchers()

    def __get_notifiers(
        self,
    ) -> List[Notifier]:
        notifiers: List[Notifier] = []

        if settings.notifiers.slack.enabled:
            self.__logger.debug("Adding SlackNotifier to scheduler.")

            notifiers.append(SlackNotifier())

        return notifiers

    def __get_watchers(
        self,
    ) -> List[Tuple[str, Watcher, str, Callable[[float], float]]]:
        watchers: List[Tuple[str, Watcher, str, Callable[[float], float]]] = []

        if settings.watchers.cpu.enabled:
            self.__logger.debug("Adding CPUWatcher to scheduler.")

            watchers.append(
                (settings.watchers.cpu.schedule, CPUWatcher(), "%", noop_formatter)
            )

        if settings.watchers.memory.enabled:
            self.__logger.debug("Adding MemoryWatcher to scheduler.")

            watchers.append(
                (
                    settings.watchers.memory.schedule,
                    MemoryWatcher(),
                    "GB",
                    memory_watcher_formatter,
                )
            )

        return watchers

    def __notify(
        self,
        watcher_name: str,
        user: str,
        previous_usage: float | None,
        current_usage: float | None,
        unit: str,
        formatter: Callable[[float], float],
    ):
        for notifier in self.__notifiers:
            notifier.notify(
                watcher_name,
                user,
                previous_usage,
                current_usage,
                unit,
                formatter,
            )

    def __notify_for_users(
        self,
        previous_exceeded: Dict[str, float],
        current_exceeded: Dict[str, float],
        watcher_name: str,
        unit: str,
        formatter: Callable[[float], float],
    ):
        # Users from the current group who were not in the previous group are new
        new_users = current_exceeded.keys() - previous_exceeded.keys()
        # Users from the previous group who are not in the current group have finished
        finished_users = previous_exceeded.keys() - current_exceeded.keys()
        # Users who are in both groups have continued
        continued_users = current_exceeded.keys() & previous_exceeded.keys()

        for user in continued_users:
            current_usage = current_exceeded[user]
            previous_usage = previous_exceeded[user]

            if current_usage > previous_usage + (previous_usage * 0.1):
                self.__notify(
                    watcher_name,
                    user,
                    previous_usage,
                    current_usage,
                    unit,
                    formatter,
                )

        for user in new_users:
            current_usage = current_exceeded[user]
            self.__notify(
                watcher_name,
                user,
                None,
                current_usage,
                unit,
                formatter,
            )

        for user in finished_users:
            previous_usage = previous_exceeded[user]
            self.__notify(
                watcher_name,
                user,
                previous_usage,
                None,
                unit,
                formatter,
            )

    def start(self):
        """Starts the scheduler loop."""
        self.__logger.info("Scheduler started.")

        watchers = self.__watchers
        previous_exceeded_threshold: Dict[str, Dict[str, float]] = {}

        while True:
            start_run_time = datetime.now()

            for schedule, watcher, unit, formatter in watchers:
                if pycron.is_now(schedule):
                    self.__logger.info(
                        "Schedule matched for %s at %s with schedule '%s'",
                        watcher.__class__.__name__,
                        start_run_time,
                        schedule,
                    )
                    exceeded_threshold = watcher.watch()
                    exceeded_threshold = {
                        user: usage
                        for user, usage in exceeded_threshold.items()
                        if user not in self.__ignore_users
                    }

                    watcher_name = watcher.__class__.__name__
                    if watcher_name not in previous_exceeded_threshold:
                        previous_exceeded_threshold[watcher_name] = {}

                    self.__notify_for_users(
                        previous_exceeded_threshold[watcher_name],
                        exceeded_threshold,
                        watcher_name,
                        unit,
                        formatter,
                    )

                    previous_exceeded_threshold[watcher_name] = exceeded_threshold

            next_run_time = start_run_time + timedelta(minutes=1)

            # Sleep if we have time before the next minute
            if next_run_time > datetime.now():
                sleep((next_run_time - datetime.now()).total_seconds())
