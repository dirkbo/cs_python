import logging
import os
from datetime import datetime, timedelta

import questionary
from dateutil import parser as date_parser

from cryptshare import CryptshareClient, CryptshareSender
from cryptshare.CryptshareValidators import CryptshareValidators

logger = logging.getLogger(__name__)


class QuestionaryCryptshareSender(CryptshareSender):
    def verify_sender_email_verification(self, cryptshare_client: CryptshareClient) -> bool:
        """
        Perform an email verification of the sender. Requires User Input.
        Overwritten from CryptshareSender to use questionary for user input.

        :param cryptshare_client: The Cryptshare client instance.
        :return: bool, True if the sender is verified, False otherwise
        """
        cryptshare_client.request_code()
        verification_code = questionary.text(
            f"Please enter the verification code sent to your email address ({self._email}):\n"
        ).ask()
        cryptshare_client.verify_code(verification_code.strip())
        verification = cryptshare_client.get_verification()
        if verification.get("verified") is not True:
            print("Verification failed.")
            return False
        print(f"Sender {self._email} is verified until {verification['validUntil']}.")
        return True


def clean_expiration(date_string_value: [str, datetime], default_days=2) -> datetime:
    """
    This function is used to clean and standardize the expiration date values.

    :param date_string_value: The input date value as a string. It can be in various formats.
    :param default_days: The default number of days to add to the current date if the input date value is empty.
    :return: The cleaned date value as a datetime object.

    The function handles various formats of expiration dates and also relative expiration dates like "tomorrow", "2d" (2 days), "3w" (3 weeks), "4m" (4 months).
    """

    now = datetime.now()
    date_value = None

    # Handle empty expiration dates
    if date_string_value is None or date_string_value == "":
        return now + timedelta(days=default_days)  # "2028-10-09T11:51:46+02:00"

    # Handle datetime objects by returning them directly
    if type(date_string_value) is datetime:
        return date_string_value

    # Handle relative expiration dates
    if date_string_value == "tomorrow":
        return now + timedelta(days=1)

    if date_string_value.endswith("d"):
        days = int(date_string_value[:-1])
        return now + timedelta(days=days)

    if date_string_value.endswith("w"):
        weeks = int(date_string_value[:-1])
        return now + timedelta(weeks=weeks)

    if date_string_value.endswith("m"):
        months = int(date_string_value[:-1])
        return now + timedelta(weeks=months * 4)

    # Handle various formats of expiration dates
    try:
        date_value = date_parser.parse(date_string_value)
    except ValueError:
        pass
    else:
        return date_value

    raise ValueError(f"Invalid expiration date: {date_string_value}")


def is_valid_expiration(date_string_value: str) -> bool:
    if date_string_value is None or date_string_value == "":
        return False
    try:
        clean_expiration(date_string_value)
    except ValueError:
        return False
    return True


def is_valid_multiple_emails(email_list: str) -> bool:
    if email_list is None or email_list == "":
        return True
    emails = email_list.split(" ")
    for email in emails:
        if not CryptshareValidators.is_valid_email(email):
            return False
    return True


def clean_string_list(string_list: [list, str]) -> list[str]:
    """
    This function is used to clean and standardize the input string list.

    :param string_list: The input string list. It can be a list or a string seperated by spaces.
    :return: The cleaned string list as a list of strings.

    The function handles various formats of string lists and also removes duplicates.
    """

    if string_list is None or string_list == "":
        return []

    if type(string_list) is str:
        string_list = string_list.split(" ")
    else:
        try:
            string_list = [str(item) for item in string_list]
        except TypeError:
            return list()

    if type(string_list) is not list[str]:
        string_list = list(string_list)

    # remove duplicates
    string_list = list(dict.fromkeys(string_list))
    return string_list


def twilio_sms_is_configured() -> bool:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", None)
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", None)
    sender_phone = os.getenv("TWILIO_SENDER_PHONE", None)

    if account_sid is None or auth_token is None or sender_phone is None:
        logger.debug("Twilio SMS is not configured.")
        return False
    logger.debug("Twilio SMS is configured.")
    return True


def send_password_with_twilio(tracking_id: str, password: str, recipient_sms: str, recipient_email: str = None) -> None:
    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure

    if not twilio_sms_is_configured():
        logger.info(f"Twilio SMS is not configured. SMS not sent to {recipient_sms}.")
        return

    account_sid = os.getenv("TWILIO_ACCOUNT_SID", None)
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", None)
    sender_phone = os.getenv("TWILIO_SENDER_PHONE", None)
    # Twilio trail accounts can only send SMS from and to verified numbers

    message = f'To access your Cryptshare Transfer "{tracking_id}" the password is "{password}"'
    if recipient_email is not None:
        message = (
            f"To access the Cryptshare transfer {tracking_id} sent to {recipient_email}, the password is {password}"
        )

    from twilio.rest import Client

    client = Client(account_sid, auth_token)
    try:
        client.api.account.messages.create(to=recipient_sms, from_=sender_phone, body=message)
    except Exception as e:
        logger.error(f"Twilio SMS failed: {e}")
    else:
        logger.debug(f"Password SMS sent to {recipient_sms}.")
