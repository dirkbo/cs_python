import logging

logger = logging.getLogger(__name__)


class NotificationMessage:
    def __init__(self, body, subject):
        logger.debug("Initialising NotificationMessage")
        self.body = body
        self.subject = subject

    def data(self):
        logger.debug("Returning NotificationMessage data")
        return {"body": self.body, "subject": self.subject}
