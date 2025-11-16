import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict


class Watcher(ABC):
    @property
    def logger(self) -> Logger:
        return self.__logger

    def __init__(self, logger_name: str):
        self.__logger = logging.getLogger(logger_name)

    @abstractmethod
    def watch(self) -> Dict[str, float]:
        raise NotImplementedError("Subclasses must implement this method")
