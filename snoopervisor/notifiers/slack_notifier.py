from typing import Callable

from slack_sdk import WebClient

from snoopervisor.config import settings
from snoopervisor.notifiers.notifier import Notifier


class SlackNotifier(Notifier):
    def __init__(self):
        super().__init__(__name__)

        self.__client = WebClient(token=settings.notifiers.slack.token)

    def notify(
        self,
        watcher_name: str,
        user: str,
        previous_usage: float | None,
        current_usage: float | None,
        unit: str,
        formatter: Callable[[float], float],
    ):
        message = f"Watcher: {watcher_name}\nUser: {user}\n"

        if previous_usage is not None:
            message += f"Previous Usage: {formatter(previous_usage)} {unit}\n"
        else:
            message += "Previous Usage: N/A\n"

        if current_usage is not None:
            message += f"Current Usage: {formatter(current_usage)} {unit}\n"
        else:
            message += "Current Usage: N/A\n"

        self.logger.info(f"Sending Slack notification:\n{message}")

        self.__client.chat_postMessage(
            channel=settings.notifiers.slack.channel, text=message
        )
