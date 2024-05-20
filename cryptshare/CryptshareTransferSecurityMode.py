import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)


class SecurityMode(Enum):
    NONE = (auto(),)
    GENERATED = (auto(),)
    MANUAL = auto()


class CryptshareTransferSecurityMode:
    _passwordMode: SecurityMode = SecurityMode.GENERATED
    _password: str = ""
    name: str = "ONE_TIME_PASSWORD"

    def __init__(self, password: str = "", mode: SecurityMode = SecurityMode.GENERATED):
        logger.debug("Initialising SecurityMode")
        self._password = password
        self._passwordMode = mode

    def data(self):
        logger.debug("Returning SecurityMode data")
        config = {}
        if self._passwordMode == SecurityMode.NONE:
            logger.debug("Setting SecurityMode to NONE")
            config = {"passwordMode": "NONE"}
        elif self._passwordMode == SecurityMode.GENERATED and self._password == "":
            logger.debug("Setting SecurityMode to GENERATED")
            config = {"passwordMode": "GENERATED"}
        elif self._passwordMode == SecurityMode.GENERATED:
            logger.debug("Setting SecurityMode to GENERATED with password")
            config = {"passwordMode": "GENERATED", "password": self._password}
        elif self._passwordMode == SecurityMode.MANUAL:
            logger.debug("Setting SecurityMode to MANUAL with password")
            config = {"passwordMode": "MANUAL", "password": self._password}
        return {"name": self.name, "config": config}

    @property
    def mode(self):
        return self._passwordMode
