import logging
import os
import re
from datetime import datetime, timedelta
import questionary

logger = logging.getLogger(__name__)


def verify_sender(cryptshare_client, sender_email):
    """
    This function is used to verify the sender email address.

    :param cryptshare_client: The Cryptshare client instance.
    :param sender_email: The sender email address.
    :return: None

    The function checks if the sender email address is already verified. If not, it requests a verification code and verifies the sender email address.
    """
    verification = cryptshare_client.get_verification()
    if verification["verified"] is True:
        print(f"Sender {sender_email} is verified until {verification['validUntil']}.")
    else:
        cryptshare_client.request_code()
        verification_code = questionary.text(
            f"Please enter the verification code sent to your email address ({sender_email}):\n"
        ).ask()
        cryptshare_client.verify_code(verification_code.strip())
        if cryptshare_client.is_verified() is not True:
            print("Verification failed.")
    return verification


def is_valid_email_or_blank(email):
    if email is None or email == "":
        return True
    # Make a regular expression for validating an Email
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    if re.fullmatch(regex, email):
        return True
    return False


def is_valid_email(email):
    if email is None or email == "":
        return False
    return is_valid_email_or_blank(email)


def is_valid_server(server):
    if server is None or server == "":
        return False
    # Make a regular expression for validating a URL
    regex = r"(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}"

    if re.fullmatch(regex, server):
        return True
    return False

def is_valid_tracking_id(tracking_id: str):
    if tracking_id is None or tracking_id == "":
        return True
    # Regular expression for validating a tracking id
    regex =r"[0-9]{8}-[0-9]{6}-.{8}"
    if re.fullmatch(regex, tracking_id):
        return True
    return False

def is_valid_transfer_id(transfer_id: str):
    if transfer_id is None or transfer_id == "":
        return False
    # Regular expression for validating a transfer id
    regex =r"[0-z]{10}"
    if re.fullmatch(regex, transfer_id):
        return True
    return False

def clean_expiration(date_string_value, default_days=2):
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

    if type(date_string_value) is datetime:
        return date_string_value

    # Handle various formats of expiration dates
    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%YT%H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S%z")
    except ValueError:
        pass
    else:
        return date_value

    try:
        date_value = datetime.strptime(date_string_value, "%d.%m.%Y %H:%M:%S %z")
    except ValueError:
        pass
    else:
        return date_value

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
    raise ValueError(f"Invalid expiration date: {date_string_value}")


def is_valid_expiration(date_string_value):
    if date_string_value is None or date_string_value == "":
        return False
    try:
        clean_expiration(date_string_value)
    except ValueError:
        return False
    return True


def clean_string_list(string_list):
    """
    This function is used to clean and standardize the input string list.

    :param string_list: The input string list. It can be a list or a string seperated by spaces.
    :return: The cleaned string list as a list of strings.

    The function handles various formats of string lists and also removes duplicates.
    """

    if string_list is None or string_list == "":
        return []
    try:
        string_list = string_list.split(" ")
    except AttributeError:
        pass
    except Exception as e:
        print(type(e))
        print(e)
    if type(string_list) is not list:
        string_list = [string_list]

    # remove duplicates
    string_list = list(dict.fromkeys(string_list))
    return string_list


def twilio_sms_is_configured():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", None)
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", None)
    sender_phone = os.getenv("TWILIO_SENDER_PHONE", None)

    if account_sid is None or auth_token is None or sender_phone is None:
        logger.debug("Twilio SMS is not configured.")
        return False
    logger.debug("Twilio SMS is configured.")
    return True


def send_password_with_twilio(tracking_id, password, recipient_sms, recipient_email=None):
    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure

    if not twilio_sms_is_configured():
        return

    account_sid = os.getenv("TWILIO_ACCOUNT_SID", None)
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", None)
    sender_phone = os.getenv("TWILIO_SENDER_PHONE", None)
    # Twilio trail accounts can only send SMS from and to verified numbers

    message = f"To access your Cryptshare Transfer {tracking_id} the password is {password}"
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
