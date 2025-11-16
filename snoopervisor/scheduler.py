import logging
from datetime import datetime, timedelta
from time import sleep
from typing import Callable, Dict, List, Tuple

import pycron

from snoopervisor.config import settings
from snoopervisor.watchers.cpu_watcher import CPUWatcher
from snoopervisor.watchers.memory_watcher import MemoryWatcher, memory_watcher_formatter
from snoopervisor.watchers.watcher import Watcher


def noop_formatter(usage: float) -> float:
    return usage


class Scheduler:
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__ignore_users = settings.users.ignore or set()

    def __get_watchers(self) -> List[Tuple[str, Watcher]]:
        watchers: List[Tuple[str, Watcher]] = []

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

    def __report(
        self,
        watcher_name: str,
        user: str,
        previous_usage: float | None,
        current_usage: float | None,
        unit: str,
        formatter: Callable[[float], float],
    ):
        pass

    def __report_for_users(
        self,
        previous_exceeded: Dict[str, float],
        current_exceeded: Dict[str, float],
        watcher_name: str,
        unit: str,
        formatter: Callable[[float], float],
    ):
        new_users = current_exceeded.keys() - previous_exceeded.keys()
        finished_users = previous_exceeded.keys() - current_exceeded.keys()
        continued_users = current_exceeded.keys() & previous_exceeded.keys()

        for user in continued_users:
            current_usage = current_exceeded[user]
            previous_usage = previous_exceeded[user]

            if current_usage > previous_usage + (previous_usage * 0.1):
                self.__report(
                    watcher_name,
                    user,
                    previous_usage,
                    current_usage,
                    unit,
                    formatter,
                )

        for user in new_users:
            current_usage = current_exceeded[user]
            self.__report(
                watcher_name,
                user,
                None,
                current_usage,
                unit,
                formatter,
            )

        for user in finished_users:
            previous_usage = previous_exceeded[user]
            self.__report(
                watcher_name,
                user,
                previous_usage,
                None,
                unit,
                formatter,
            )

    def start(self):
        self.__logger.info("Scheduler started.")

        watchers = self.__get_watchers()
        previous_exceeded_threshold: Dict[str, Dict[str, float]] = {}

        while True:
            start_run_time = datetime.now()

            for schedule, watcher, unit, formatter in watchers:
                if pycron.is_now(schedule):
                    self.__logger.info(
                        f"Schedule matched for {watcher.__class__.__name__} at {start_run_time} with schedule '{schedule}'"
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

                    self.__report_for_users(
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
