import logging

logger = logging.getLogger(__name__)


class NotificationMessage:
    def __init__(self, body: str = None, subject: str = None) -> None:
        logger.debug("Initialising NotificationMessage")
        self.body = body if body else ""
        self.subject = subject if subject else ""

    def data(self) -> dict:
        logger.debug("Returning NotificationMessage data")
        return {"body": self.body, "subject": self.subject}
