"""Main entry point for Snoopervisor."""

import logging

from snoopervisor.scheduler import Scheduler


def __create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


def main():
    """Main entry point for Snoopervisor."""

    logger = __create_logger("snoopervisor")
    logger.info("Starting Snoopervisor...")

    scheduler = Scheduler()

    # This is blocking.
    scheduler.start()
