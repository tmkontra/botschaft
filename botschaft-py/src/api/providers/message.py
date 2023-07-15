from api.logger import get_logger
from api.model import Provider


logger = get_logger(__name__)


class Message:
    provider: Provider

    def log_message(self, contents: str, destination: str = None):
        if destination:
            to = f" to {destination}"
        else:
            to = ""
        logger.info(f"{self.provider}: Sending {contents}{to}")

    def log_sent(self, contents: str, destination: str = None, extra_info: str = None):
        if destination:
            to = f" to {destination}"
        else:
            to = ""
        if extra_info:
            extra = f", {extra_info}"
        else:
            extra = ""
        logger.info(f"{self.provider}: Sent {contents}{to}{extra}")
