import questionary
from helpers import ExtendedCryptshareValidators

from cryptshare import CryptshareClient
from examples.shell_example.helpers import QuestionaryCryptshareSender
from examples.shell_example.transfer_status import transfer_status


def status_transfer_interactive(default_server_url, default_sender_email):
    send_server = questionary.text(
        "Which server do you want to use to check a Transfer status?\n",
        default=default_server_url,
        validate=ExtendedCryptshareValidators.is_valid_server_url,
    ).ask()
    if send_server == "":
        send_server = default_server_url
    print(f"Checking transfer status using {send_server}")
    client = CryptshareClient(default_server_url)

    if default_sender_email is None or not ExtendedCryptshareValidators.is_valid_email_or_blank(default_sender_email):
        default_sender_email = ""
    sender_email = questionary.text(
        "For which email do you want to check transfer status?\n",
        default=default_sender_email,
        validate=ExtendedCryptshareValidators.is_valid_email_or_blank,
    ).ask()
    if sender_email == "":
        sender_email = default_sender_email
    transfer_transfer_id = questionary.text(
        "Which transfer ID do you want to check the status of? (blank=all)\n",
        validate=ExtendedCryptshareValidators.is_valid_tracking_id_or_blank,
    ).ask()

    sender = QuestionaryCryptshareSender(email=sender_email, name="REST-API Sender", phone="0")
    sender.setup_and_verify_sender(client)
    transfer_status(client, transfer_transfer_id)
