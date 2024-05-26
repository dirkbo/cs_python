import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)


class OneTimePaswordSecurityModes(Enum):
    NONE = (auto(),)
    GENERATED = (auto(),)
    MANUAL = auto()


class QuickSecurityModes(Enum):
    GENERATED = (auto(),)
    MANUAL = auto()
    # ToDO: Implement QUICK, when Supported by the Cryptshare API


class CryptshareTransferSecurityMode:
    _passwordMode: OneTimePaswordSecurityModes = OneTimePaswordSecurityModes.GENERATED
    _password: str = ""
    name: str = "ONE_TIME_PASSWORD"

    def __init__(
        self, password: str = "", mode: OneTimePaswordSecurityModes = OneTimePaswordSecurityModes.GENERATED
    ) -> None:
        logger.debug("Initialising SecurityMode")
        self._password = password
        self._passwordMode = mode

    def data(self) -> dict:
        logger.debug("Returning SecurityMode data")
        config = {}
        if self._passwordMode == OneTimePaswordSecurityModes.NONE:
            logger.debug("Setting SecurityMode to NONE")
            config = {"passwordMode": "NONE"}
        elif self._passwordMode == OneTimePaswordSecurityModes.GENERATED and self._password == "":
            logger.debug("Setting SecurityMode to GENERATED")
            config = {"passwordMode": "GENERATED"}
        elif self._passwordMode == OneTimePaswordSecurityModes.GENERATED:
            logger.debug("Setting SecurityMode to GENERATED with password")
            config = {"passwordMode": "GENERATED", "password": self._password}
        elif self._passwordMode == OneTimePaswordSecurityModes.MANUAL:
            logger.debug("Setting SecurityMode to MANUAL with password")
            config = {"passwordMode": "MANUAL", "password": self._password}
        return {"name": self.name, "config": config}

    @property
    def mode(self):
        return self._passwordMode
