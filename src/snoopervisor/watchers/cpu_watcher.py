from typing import Dict

import psutil

from snoopervisor.config import settings
from snoopervisor.watchers.watcher import Watcher


class CPUWatcher(Watcher):
    def __init__(self):
        super().__init__(__name__)
        self.__ignore_users = settings.users.ignore or set()

    def watch(self) -> Dict[str, float]:
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

            try:
                cpu_usage_by_username[username] += process.cpu_percent(interval=0.1)
            except psutil.NoSuchProcess:
                # Skip processes that no longer exist
                continue

        self.logger.info(f"CPU usage by username: {cpu_usage_by_username}")

        threshold_exceeded = {
            username: usage
            for username, usage in cpu_usage_by_username.items()
            if usage > settings.watchers.cpu.threshold
        }

        self.logger.warning(
            f"Users exceeding CPU threshold of {settings.watchers.cpu.threshold}%: {threshold_exceeded}"
        )

        return threshold_exceeded
