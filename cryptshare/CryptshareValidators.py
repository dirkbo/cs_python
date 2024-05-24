import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CryptshareValidators:
    """Collection of validators for cryptshare related data."""

    @staticmethod
    def is_valid_email_or_blank(email: str) -> bool:
        """Checks if the email is valid or blank
        :param email: The email to validate
        :return: True if the email is valid or blank, False otherwise
        """
        if email is None or email == "":
            logger.debug("Valid E-Mail: Email is blank, ")
            return True
        # Make a regular expression for validating an Email
        email_regex = re.compile(
            r"((?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:["
            r"\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9]("
            r"?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]["
            r"0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:["
            r"\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)]))"
        )

        if re.fullmatch(email_regex, email):
            logger.debug(f"Valid E-Mail: {email}")
            return True
        logger.debug(f"Invalid E-Mail: {email}")
        return False

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Checks if the email is valid
        :param email: The email to validate
        :return: True if the email is valid, False otherwise
        """
        if email is None or email == "":
            logger.debug("Invalid E-Mail: Email is blank, ")
            return False
        return CryptshareValidators.is_valid_email_or_blank(email)

    @staticmethod
    def is_valid_server_url(server: str) -> bool:
        """Checks if the server is valid
        :param server: The server to validate
        :return: True if the server is valid, False otherwise
        """
        if server is None or server == "":
            logger.debug("Invalid Cryptshare Server: Server is blank, ")
            return False
        # Make a regular expression for validating a URL
        regex = r"(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}(:\d{1,5})?"

        if re.fullmatch(regex, server):
            logger.debug(f"Valid Cryptshare Server: {server}")
            return True
        logger.debug(f"Invalid Cryptshare Server: {server}")
        return False

    @staticmethod
    def is_valid_tracking_id_or_blank(tracking_id: str) -> bool:
        """Checks if the tracking id is valid or blank
        :param tracking_id: The tracking id to validate
        :return: True if the tracking id is valid, False otherwise
        """
        if tracking_id is None or tracking_id == "":
            logger.debug("Valid Tracking ID: Tracking ID is blank")
            return True

        # Regular expression for validating a tracking id
        regex = r"[0-9]{8}-[0-9]{6}-.{8}"
        if not re.fullmatch(regex, tracking_id):
            logger.debug(f"Valid Tracking ID: {tracking_id}")
            return False

        # First parts of the tracking ID has to be a valid datetime
        part1 = tracking_id.split("-")[0]
        part2 = tracking_id.split("-")[1]
        tracking_id_timestamp = f"{part1}-{part2}"

        try:
            datetime.strptime(tracking_id_timestamp, "%Y%m%d-%H%M%S")
        except ValueError:
            logger.debug(f"Invalid Tracking ID: {tracking_id}")
            return False

        logger.debug(f"Valid Tracking ID: {tracking_id}")
        return True

    @staticmethod
    def is_valid_tracking_id(tracking_id: str) -> bool:
        """Checks if the tracking id is valid
        :param tracking_id: The tracking id to validate
        :return: True if the tracking id is valid, False otherwise
        """
        if tracking_id is None or tracking_id == "":
            logger.debug("Invalid Tracking ID: Tracking ID is blank ")
            return False
        return CryptshareValidators.is_valid_tracking_id_or_blank(tracking_id)

    @staticmethod
    def is_valid_transfer_id(transfer_id: str) -> bool:
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

    @staticmethod
    def is_valid_verification_code(verification_code: str) -> bool:
        """Checks if the verification code is valid
        :param verification_code: The verification code to validate
        :return: True if the verification code is valid, False otherwise
        """
        if verification_code is None or verification_code == "":
            logger.debug("Invalid Verification Code: Verification Code is blank, ")
            return False
        # Regular expression for validating a verification code
        regex = r"[0-z]{10}"
        if re.fullmatch(regex, verification_code):
            logger.debug(f"Valid Verification Code: {verification_code}")
            return True
        logger.debug(f"Invalid Verification Code: {verification_code}")
        return False
