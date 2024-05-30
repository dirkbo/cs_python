import logging

logger = logging.getLogger(__name__)


class CryptshareHeader:
    _general: dict = dict()

    def __init__(self, target_api_version: str, product_key: str = "api.rest") -> None:
        major_api_version, minimum_minor_api_version = target_api_version.split(".")
        self._general = dict(
            {
                "X-CS-MajorApiVersion": major_api_version,
                "X-CS-MinimumMinorApiVersion": minimum_minor_api_version,
                "X-CS-ProductKey": product_key,
            }
        )

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

    def update_header(self, other_dict: dict) -> None:
        logger.debug(f"Updating header with {other_dict}")
        self._general.update(other_dict)

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
