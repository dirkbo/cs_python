import logging

logger = logging.getLogger(__name__)


class Header:
    general = {
        "X-CS-MajorApiVersion": "1",
        "X-CS-MinimumMinorApiVersion": "8",
        "X-CS-ProductKey": "api.rest",
    }

    def set_client_id(self, client_id):
        logger.debug(f"Setting client_id to {client_id}")
        self.general.update({"X-CS-ClientId": client_id})

    def set_verification(self, token):
        logger.debug(f"Setting verification token to {token}")
        self.general.update({"X-CS-VerificationToken": token})

    def set_origin(self, origin):
        logger.debug(f"Setting origin to {origin}")
        self.general.update(({"Origin": origin}))

    def other_header(self, other):
        logger.debug(f"Adding other header {other}")
        new_header = self.general.copy()
        new_header.update(other)
        return new_header
