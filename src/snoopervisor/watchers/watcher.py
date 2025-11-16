"""Watcher base class for resource monitoring."""

import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict


class Watcher(ABC):
    """Abstract base class for resource watchers."""

    @property
    def logger(self) -> Logger:
        """Returns the logger instance for the watcher."""
        return self.__logger

    def __init__(self, logger_name: str):
        self.__logger = logging.getLogger(logger_name)

    @abstractmethod
    def watch(self) -> Dict[str, float]:
        """Watches a specific resource and returns usage data."""

        raise NotImplementedError("Subclasses must implement this method")
