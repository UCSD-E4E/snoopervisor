"""Watches Memory usage per username."""

from typing import Dict

import psutil

from snoopervisor.config import settings
from snoopervisor.watchers.watcher import Watcher


def memory_watcher_formatter(usage_in_bytes: float) -> float:
    """Convert memory usage from bytes to gigabytes."""
    return round(usage_in_bytes / (1024**3), 2)


class MemoryWatcher(Watcher):
    # pylint: disable=too-few-public-methods
    """Watches Memory usage per username."""

    def __init__(self):
        super().__init__(__name__)

    def watch(self) -> Dict[str, float]:
        # pylint: disable=R0801
        self.logger.info("Watching Memory usage...")

        pids = psutil.pids()

        memory_usage_by_username = {}
        for pid in pids:
            if psutil.pid_exists(pid) is False:
                continue

            process = psutil.Process(pid)
            username = process.username()

            if username not in memory_usage_by_username:
                memory_usage_by_username[username] = 0.0

            memory_info = process.memory_info()

            # Measured in bytes.
            memory_usage_by_username[username] += memory_info.rss  # Resident Set Size

        self.logger.info("Memory usage by username: %s", memory_usage_by_username)

        threshold_exceeded = {
            username: usage
            for username, usage in memory_usage_by_username.items()
            if usage > settings.watchers.memory.threshold
        }

        self.logger.warning(
            "Users exceeding Memory threshold of %s bytes: %s",
            settings.watchers.memory.threshold,
            threshold_exceeded,
        )

        return threshold_exceeded
