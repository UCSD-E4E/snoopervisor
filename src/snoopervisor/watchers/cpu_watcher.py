"""Watches CPU usage per username."""

from typing import Dict

import psutil

from snoopervisor.config import settings
from snoopervisor.watchers.watcher import Watcher


class CPUWatcher(Watcher):
    """Watches CPU usage per username."""

    def __init__(self):
        super().__init__(__name__)
        self.__ignore_users = settings.users.ignore or set()

    def watch(self) -> Dict[str, float]:
        """Watches CPU usage per username."""
        # pylint: disable=R0801
        ignore_users = self.__ignore_users
        self.logger.info("Watching CPU usage...")

        pids = psutil.pids()

        cpu_usage_by_username = {}
        for pid in pids:
            if psutil.pid_exists(pid) is False:
                continue

            process = psutil.Process(pid)
            username = process.username()

            # Skip ignored users
            if username in ignore_users:
                continue

            if username not in cpu_usage_by_username:
                cpu_usage_by_username[username] = 0.0

            # It may have been a bit since we last checked if the process exists,
            # so we handle the potential exception here.
            # We don't need to take an action if it no longer exists.
            try:
                cpu_usage_by_username[username] += process.cpu_percent(interval=0.1)
            except psutil.NoSuchProcess:
                # Skip processes that no longer exist
                continue

        self.logger.info("CPU usage by username: %s", cpu_usage_by_username)

        threshold_exceeded = {
            username: usage
            for username, usage in cpu_usage_by_username.items()
            if usage > settings.watchers.cpu.threshold
        }

        self.logger.warning(
            "Users exceeding CPU threshold of %s%%: %s",
            settings.watchers.cpu.threshold,
            threshold_exceeded,
        )

        return threshold_exceeded
