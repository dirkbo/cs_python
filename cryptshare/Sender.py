import logging

logger = logging.getLogger(__name__)


class Sender:
    def __init__(self, name, phone):
        logger.debug("Initialising Sender")
        self.name = name
        self.phone = phone

    def data(self):
        logger.debug("Returning Sender data")
        return {"name": self.name, "phone": self.phone}
