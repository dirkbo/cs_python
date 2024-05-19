import logging

from cryptshare import CryptshareClient

logger = logging.getLogger(__name__)


class CryptshareSender:
    _name: str = ""
    _phone: str = ""
    _email: str = ""

    def __init__(self, name: str, phone: str, email: str):
        logger.debug("Initialising Sender")
        self._name = name
        self._phone = phone
        self._email = email

    def data(self) -> dict:
        logger.debug("Returning Sender data as dictionary")
        return {"name": self._name, "phone": self._phone, "email": self._email}

    def verify_sender_email_verification(self, cryptshare_client: CryptshareClient):
        """Perform an email verification of the sender. Requires User Input."""
        cryptshare_client.request_code()
        verification_code = input(f"Please enter the verification code sent to your email address ({self._email}):\n")
        cryptshare_client.verify_code(verification_code.strip())
        verification = cryptshare_client.get_verification()
        if verification.get("verified") is not True:
            print("Verification failed.")
            return False
        print(f"Sender {self._email} is verified until {verification['validUntil']}.")
        return True

    def setup_and_verify_sender(
        self,
        cryptshare_client: CryptshareClient,
        email: str = None,
        phone: str = None,
        name: str = None,
        no_user_input: bool = False,
    ) -> bool:
        logger.debug("Verifying sender")
        """
            This function is used to verify the sender email address.

            :param cryptshare_client: The Cryptshare client instance.
            :param sender_email: The sender email address.
            :return: bool, True if the sender is verified, False otherwise

            The function checks if the sender email address is already verified. If not, it requests a verification code and verifies the sender email address.
            """
        if name:
            self._name = name
        if phone:
            self._phone = phone
        if email:
            self._email = email
        cryptshare_client.set_email(self._email)

        verification = cryptshare_client.get_verification()
        if verification["verified"] is True:
            logger.info(f"Sender {email} is verified until {verification['validUntil']}.")
            return True

        if no_user_input:
            logger.warning("Verification failed.")
            return False

        return self.verify_sender_email_verification(cryptshare_client)
