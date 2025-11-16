from typing import Callable

from snoopervisor.reporters.reporter import Reporter


class SlackReporter(Reporter):
    def __init__(self):
        super().__init__(__name__)

    def report(
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
        # Here you would add the actual code to send the message to Slack
