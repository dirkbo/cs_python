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

from receive_transfer import receive_transfer
from receive_transfer_interactive import receive_transfer_interactive
from send_transfer import send_transfer
from send_transfer_interactive import send_transfer_interactive
from status_transfer import status_transfer
from status_transfer_interactive import status_transfer_interactive

from cryptshare import CryptshareClient
from examples.shell_example.helpers import ShellCryptshareValidators

logger = logging.getLogger(__name__)
LOGGING_CONFIG_FILE = "examples/shell_example/logging_config.json"


def setup_logging() -> None:
    with open(LOGGING_CONFIG_FILE, "r") as f:
        config = json.load(f)
        logging.config.dictConfig(config)


def parse_args() -> argparse.Namespace:
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
    parser.add_argument("--transfer_id", help="Transfer ID of the Transfer ID to RECEIVE a Transfer", required=False)
    parser.add_argument("-p", "--password", help="Password of the Transfer to RECEIVE or SEND", required=False)
    parser.add_argument(
        "--zip", action="store_true", default=False, help="RECEIVE the Transfer as a .zip-File.", required=False
    )
    parser.add_argument(
        "--eml", action="store_true", default=False, help="RECEIVE the Transfer as a .eml-File.", required=False
    )
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
    parser.add_argument(
        "--no_password",
        help="SEND the Transfer without requiring the recipient to enter a password",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--generate_password",
        help="The password for the recipient to receive the SEND transfer will be generated",
        action="store_true",
        required=False,
    )
    # Check status of a sent Transfer
    parser.add_argument("--tracking_id", help="Tracking ID of the Transfer to check STATUS of", required=False)
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


def main() -> None:
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
        if inputs.generate_password:
            new_transfer_password = ""
        if inputs.no_password:
            new_transfer_password = "NO_PASSWORD_MODE"
        transfer_expiration = ShellCryptshareValidators.clean_expiration(inputs.expiration)
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
        recipient_transfer_id = inputs.transfer_id
        password = inputs.password
        save_path = recipient_transfer_id
        receive_transfer(
            default_server_url,
            recipient_transfer_id,
            password,
            save_path,
            download_zip=inputs.zip,
            download_eml=inputs.eml,
        )
        return
    elif inputs.mode == "status":
        client = CryptshareClient(default_server_url)
        client.set_sender(default_sender_email, default_sender_name, default_sender_phone)
        status_transfer(client, inputs.tracking_id)
        return
    while True:
        mode = interactive_user_choice()
        if mode == "send":
            send_transfer_interactive(
                default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
            )
        elif mode == "receive":
            receive_transfer_interactive(default_server_url)
        elif mode == "status":
            status_transfer_interactive(default_server_url, default_sender_email)
        if mode is False:
            break


if __name__ == "__main__":
    main()
