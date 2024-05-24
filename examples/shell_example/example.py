import argparse
import inspect
import json
import logging
import logging.config
import os
import sys

import questionary
from dotenv import load_dotenv

# To work from examples folder, parent folder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, parentdir)

from helpers import QuestionaryCryptshareSender, clean_expiration
from receive_transfer import receive_transfer
from send_transfer import send_transfer
from send_transfer_interactive import send_transfer_interactive
from transfer_status import transfer_status

from cryptshare import CryptshareClient, CryptshareValidators

logger = logging.getLogger(__name__)
LOGGING_CONFIG_FILE = "examples/shell_example/logging_config.json"


def setup_logging():
    with open(LOGGING_CONFIG_FILE, "r") as f:
        config = json.load(f)
        logging.config.dictConfig(config)


def parse_args():
    parser = argparse.ArgumentParser(description="Send and receive files using Cryptshare.")
    requires_sender = os.getenv("CRYPTSHARE_SENDER_EMAIL", None) is None
    requires_server = os.getenv("CRYPTSHARE_SERVER", None) is None
    parser.add_argument(
        "-m",
        "--mode",
        help="send or receive files",
        choices=["send", "receive", "status", "interactive"],
        default="interactive",
    )
    parser.add_argument("-s", "--server", help="Cryptshare Server URL", required=requires_server)
    # Receive a Transfer
    parser.add_argument("-t", "--transfer", help="Transfer ID of the Transfer to RECEIVE", required=False)
    parser.add_argument("-p", "--password", help="Password of the Transfer to RECEIVE", required=False)
    # Send a Transfer
    parser.add_argument(
        "-e",
        "--sender_email",
        help="Sender Email address to SEND from or check STATUS of a transfer.",
        required=requires_sender,
    )
    parser.add_argument("-n", "--sender_name", help="Name of the Sender to SEND from.", required=requires_sender)
    parser.add_argument("--sender_phone", help="Phone number of the sender to SEND from.", required=requires_sender)
    parser.add_argument("-f", "--file", help="Path of a file or a folder of files to SEND.", action="append")
    parser.add_argument("--to", help="A Recipient email address to SEND to.", action="append")
    parser.add_argument("--cc", help="A CC email address(es) to SEND to.", action="append")
    parser.add_argument("--bcc", help="A BCC email address(es) to SEND to.", action="append")
    parser.add_argument("--subject", help="Subject of the Transfer to SEND.")
    parser.add_argument("--message", help="Custom notification Message of the Transfer to SEND.")
    parser.add_argument("--expiration", help="Expiration of the Transfer to SEND.")
    parser.add_argument("--sms_recipient", help="Recipient phone number to SEND SMS Password to.", action="append")
    # Check status of a sent Transfer
    parser.add_argument("--status", help="Tracking ID of the Transfer to check STATUS of.", required=False)
    args = parser.parse_args()
    return args


def interactive_user_choice():
    mode = (
        questionary.select(
            "Do you want to send or receive files?",
            choices=[
                questionary.Choice(title="Send a new Transfer", value="Send", shortcut_key="1"),
                questionary.Choice(title="Download a Transfer", value="Receive", shortcut_key="2"),
                questionary.Choice(title="Check the Status of a Transfer", value="Status", shortcut_key="3"),
                questionary.Choice(title="Quit", value="Exit", shortcut_key="q"),
            ],
            use_shortcuts=True,
        )
        .ask()
        .lower()
    )
    if mode == "cancel" or mode == "abort" or mode == "exit":
        return False
    return mode


def transfer_status_interactive(default_server_url, default_sender_email):
    send_server = questionary.text(
        "Which server do you want to use to check a Transfer status?\n",
        default=default_server_url,
        validate=CryptshareValidators.is_valid_server_url,
    ).ask()
    if send_server == "":
        send_server = default_server_url
    print(f"Checking transfer status using {send_server}")
    client = CryptshareClient(default_server_url)

    if default_sender_email is None or not CryptshareValidators.is_valid_email_or_blank(default_sender_email):
        default_sender_email = ""
    sender_email = questionary.text(
        "For which email do you want to check transfer status?\n",
        default=default_sender_email,
        validate=CryptshareValidators.is_valid_email_or_blank,
    ).ask()
    if sender_email == "":
        sender_email = default_sender_email
    transfer_transfer_id = questionary.text(
        "Which transfer ID do you want to check the status of? (blank=all)\n",
        validate=CryptshareValidators.is_valid_tracking_id_or_blank,
    ).ask()

    sender = QuestionaryCryptshareSender(email=sender_email, name="REST-API Sender", phone="0")
    sender.setup_and_verify_sender(client)
    transfer_status(client, transfer_transfer_id)


def download_transfer_interactive(default_server_url, origin):
    dl_server = questionary.text(
        "From which server do you want to download a Transfer?",
        default=default_server_url,
        validate=CryptshareValidators.is_valid_server_url,
    ).ask()
    if dl_server == "":
        dl_server = default_server_url
    print(f"Downloading from {dl_server}")

    recipient_transfer_id = questionary.text(
        f"Which transfer ID did you receive from {default_server_url}?\n",
        default="",
        validate=CryptshareValidators.is_valid_transfer_id,
    ).ask()
    password = questionary.password(f"What is the PASSWORD for transfer {recipient_transfer_id}?\n").ask()

    default_path = recipient_transfer_id
    save_path = default_path
    user_path = questionary.path(
        "Where do you want to save the downloaded files?",
        default=default_path,
        only_directories=True,
    ).ask()
    if user_path != "":
        save_path = user_path
    receive_transfer(dl_server, recipient_transfer_id, password, save_path)


def main():
    load_dotenv()

    setup_logging()
    inputs = parse_args()

    default_server_url = os.getenv("CRYPTSHARE_SERVER", "http://localhost") if not inputs.server else inputs.server
    default_sender_email = os.getenv("CRYPTSHARE_SENDER_EMAIL", "") if not inputs.sender_email else inputs.sender_email
    default_sender_name = (
        os.getenv("CRYPTSHARE_SENDER_NAME", "REST-API Sender") if not inputs.sender_name else inputs.sender_name
    )
    default_sender_phone = os.getenv("CRYPTSHARE_SENDER_PHONE", "0") if not inputs.sender_phone else inputs.sender_phone
    origin = os.getenv("CRYPTSHARE_CORS_ORIGIN", "https://localhost")

    if inputs.mode == "send":
        new_transfer_password = inputs.password
        transfer_expiration = clean_expiration(inputs.expiration)
        send_transfer(
            origin,
            default_server_url,
            default_sender_email,
            default_sender_name,
            default_sender_phone,
            new_transfer_password,
            transfer_expiration,
            inputs.file,
            inputs.to,
            cc=inputs.cc,
            bcc=inputs.bcc,
            subject=inputs.subject,
            message=inputs.message,
            recipient_sms_phones=inputs.sms_recipient,
        )
        return
    elif inputs.mode == "receive":
        recipient_transfer_id = inputs.transfer
        password = inputs.password
        save_path = recipient_transfer_id
        receive_transfer(default_server_url, recipient_transfer_id, password, save_path)
        return
    elif inputs.mode == "status":
        client = CryptshareClient(default_server_url)
        client.set_sender(default_sender_email, default_sender_name, default_sender_phone)
        transfer_status(client, inputs.transfer)
        return
    while True:
        mode = interactive_user_choice()
        if mode == "send":
            send_transfer_interactive(
                default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
            )
        elif mode == "receive":
            download_transfer_interactive(default_server_url, origin)
        elif mode == "status":
            transfer_status_interactive(default_server_url, default_sender_email, origin)
        if mode is False:
            break


if __name__ == "__main__":
    main()
