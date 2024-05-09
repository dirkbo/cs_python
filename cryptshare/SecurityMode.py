import logging

logger = logging.getLogger(__name__)


class SecurityMode:
    def __init__(self, password="", mode="GENERATED"):
        logger.debug("Initialising SecurityMode")
        if mode == "NONE":
            logger.debug("Setting SecurityMode to NONE")
            self.config = {"passwordMode": "NONE"}
        elif mode == "GENERATED" and password == "":
            logger.debug("Setting SecurityMode to GENERATED")
            self.config = {"passwordMode": "GENERATED"}
        elif mode == "GENERATED":
            logger.debug("Setting SecurityMode to GENERATED with password")
            self.config = {"passwordMode": "GENERATED", "password": password}
        elif mode == "MANUAL":
            logger.debug("Setting SecurityMode to MANUAL with password")
            self.config = {"passwordMode": "MANUAL", "password": password}
        self.name = "ONE_TIME_PASSWORD"

    def data(self):
        logger.debug("Returning SecurityMode data")
        return {"name": self.name, "config": self.config}
