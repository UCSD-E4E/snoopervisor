"""Abstract base class for notifiers."""

import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable


class Notifier(ABC):
    """Abstract base class for notifiers."""

    # pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

    @property
    def logger(self) -> Logger:
        """Returns the logger instance for the notifier."""
        return self.__logger

    def __init__(self, logger_name: str):
        self.__logger = logging.getLogger(logger_name)

    @abstractmethod
    def notify(
        self,
        watcher_name: str,
        user: str,
        previous_usage: float | None,
        current_usage: float | None,
        unit: str,
        formatter: Callable[[float], float],
    ):
        """Sends a notification."""
        raise NotImplementedError("Subclasses must implement this method")
