import logging
import re

logger = logging.getLogger(__name__)


class CryptshareValidators:
    @staticmethod
    def is_valid_email_or_blank(email):
        """Checks if the email is valid or blank
        :param email: The email to validate
        :return: True if the email is valid or blank, False otherwise
        """
        if email is None or email == "":
            logger.debug("Valid E-Mail: Email is blank, ")
            return True
        # Make a regular expression for validating an Email
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        if re.fullmatch(regex, email):
            logger.debug(f"Valid E-Mail: {email}")
            return True
        logger.debug(f"Invalid E-Mail: {email}")
        return False

    @staticmethod
    def is_valid_email(email):
        """Checks if the email is valid
        :param email: The email to validate
        :return: True if the email is valid, False otherwise
        """
        if email is None or email == "":
            logger.debug("Invalid E-Mail: Email is blank, ")
            return False
        return CryptshareValidators.is_valid_email_or_blank(email)

    @staticmethod
    def is_valid_server_url(server):
        """Checks if the server is valid
        :param server: The server to validate
        :return: True if the server is valid, False otherwise
        """
        if server is None or server == "":
            logger.debug("Invalid Cryptshare Server: Server is blank, ")
            return False
        # Make a regular expression for validating a URL
        regex = r"(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}"

        if re.fullmatch(regex, server):
            logger.debug(f"Valid Cryptshare Server: {server}")
            return True
        logger.debug(f"Invalid Cryptshare Server: {server}")
        return False

    @staticmethod
    def is_valid_tracking_id_or_blank(tracking_id: str):
        """Checks if the tracking id is valid or blank
        :param tracking_id: The tracking id to validate
        :return: True if the tracking id is valid, False otherwise
        """
        if tracking_id is None or tracking_id == "":
            logger.debug("Valid Tracking ID: Tracking ID is blank")
            return True
        # Regular expression for validating a tracking id
        regex = r"[0-9]{8}-[0-9]{6}-.{8}"
        if re.fullmatch(regex, tracking_id):
            logger.debug(f"Valid Tracking ID: {tracking_id}")
            return True
        logger.debug(f"Invalid Tracking ID: {tracking_id}")
        return False

    @staticmethod
    def is_valid_tracking_id(tracking_id: str):
        """Checks if the tracking id is valid
        :param tracking_id: The tracking id to validate
        :return: True if the tracking id is valid, False otherwise
        """
        if tracking_id is None or tracking_id == "":
            logger.debug("Invalid Tracking ID: Tracking ID is blank ")
            return False
        return CryptshareValidators.is_valid_tracking_id_or_blank(tracking_id)

    @staticmethod
    def is_valid_transfer_id(transfer_id: str):
        """Checks if the transfer id is valid
        :param transfer_id: The transfer id to validate
        :return: True if the transfer id is valid, False otherwise
        """
        if transfer_id is None or transfer_id == "":
            logger.debug("Invalid Transfer ID: Transfer ID is blank, ")
            return False
        # Regular expression for validating a transfer id
        regex = r"[0-z]{10}"
        if re.fullmatch(regex, transfer_id):
            logger.debug(f"Valid Transfer ID: {transfer_id}")
            return True
        logger.debug(f"Invalid Transfer ID: {transfer_id}")
        return False