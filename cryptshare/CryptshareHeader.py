import logging

logger = logging.getLogger(__name__)


class CryptshareHeader:
    _general = {
        "X-CS-MajorApiVersion": "1",
        "X-CS-MinimumMinorApiVersion": "9",
        "X-CS-ProductKey": "api.rest",
    }
    _cors = {
        "Origin": "",
    }

    @property
    def client_id(self) -> str:
        return self._general.get("X-CS-ClientId", None)

    @client_id.setter
    def client_id(self, client_id: str) -> None:
        logger.debug(f"Setting client_id to {client_id}")
        self._general.update({"X-CS-ClientId": client_id})

    @property
    def verification_token(self) -> str:
        return self._general.get("X-CS-VerificationToken", None)

    @verification_token.setter
    def verification_token(self, token: str) -> None:
        logger.debug(f"Setting verification token to {token}")
        self._general.update({"X-CS-VerificationToken": token})

    @property
    def origin(self) -> str:
        return self._cors.get("Origin", None)

    @origin.setter
    def origin(self, origin):
        logger.debug(f"Setting origin to {origin}")
        self._cors.update(({"Origin": origin}))

    @property
    def request_header_cors(self):
        """Headers needed to access endpoint product key / Cors"""
        return self._cors | self._general

    @property
    def request_header(self):
        """Headers needed to access generic api endpoints using request"""
        return self._general

    def extra_header(self, other: dict):
        logger.info(f"Adding additional other header {other}")
        logger.debug(f"Current headers: {self._general | other}")
        return self._general | other
