import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable


class Reporter(ABC):
    @property
    def logger(self) -> Logger:
        return self.__logger

    def __init__(self, logger_name: str):
        self.__logger = logging.getLogger(logger_name)

    @abstractmethod
    def report(
        self,
        watcher_name: str,
        user: str,
        previous_usage: float | None,
        current_usage: float | None,
        unit: str,
        formatter: Callable[[float], float],
    ):
        raise NotImplementedError("Subclasses must implement this method")
