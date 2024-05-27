import logging

logger = logging.getLogger(__name__)


class CryptshareHeader:
    _general = {
        "X-CS-MajorApiVersion": "1",
        "X-CS-MinimumMinorApiVersion": "9",
        "X-CS-ProductKey": "api.rest",
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
    def request_header(self):
        """Headers needed to access generic api endpoints using request"""
        return self._general

    def extra_header(self, other: dict):
        logger.info(f"Adding additional other header {other}")
        logger.debug(f"Current headers: {self._general | other}")
        return self._general | other

    def overwrite_header(self, other: dict):
        logger.info(f"Temporary overwriting headers with {other}")
        temp_headers = self._general.copy()
        temp_headers.update(other)
        logger.debug(f"Temporary headers: {temp_headers}")
        return temp_headers
