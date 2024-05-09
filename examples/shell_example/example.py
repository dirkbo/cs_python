import argparse
import json
import os
import inspect
import sys
import logging
import logging.config

# To work from examples folder, parent folder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, parentdir)

from transfer_status import transfer_status
from send_transfer import send_transfer
from receive_transfer import receive_transfer

logging.getLogger(__name__)
LOGGING_CONFIG_FILE = "examples/shell_example/logging_config.json"


def setup_logging():
    with open(LOGGING_CONFIG_FILE, "r") as f:
        config = json.load(f)
        logging.config.dictConfig(config)


def parse_args():
    parser = argparse.ArgumentParser(description="Send and receive files using Cryptshare.")
    parser.add_argument(
        "-m",
        "--mode",
        help="send or receive files",
        choices=["send", "receive", "status", "interactive"],
        required=False,
    )
    parser.add_argument("-s", "--server", help="Cryptshare Server URL", required=False)
    # Receive a Transfer
    parser.add_argument("-t", "--transfer", help="Transfer ID of the Transfer to RECEIVE", required=False)
    parser.add_argument("-p", "--password", help="Password of the Transfer to RECEIVE", required=False)
    # Send a Transfer
    parser.add_argument("-e", "--email", help="Sender Email address to SEND from or check STATUS of a transfer.")
    parser.add_argument("-n", "--name", help="Name of the Sender to SEND from.")
    parser.add_argument("--phone", help="Phone number of the sender to SEND from.")
    parser.add_argument("-f", "--file", help="Path of a file or a folder of files to SEND.", action="append")
    parser.add_argument("--to", help="A Recipient email address to SEND to.", action="append")
    parser.add_argument("--cc", help="A CC email address(es) to SEND to.", action="append")
    parser.add_argument("--bcc", help="A BCC email address(es) to SEND to.", action="append")
    parser.add_argument("--subject", help="Subject of the Transfer to SEND.")
    parser.add_argument("--message", help="Custom notification Message of the Transfer to SEND.")
    parser.add_argument("--expiration", help="Expiration of the Transfer to SEND.")
    # Check status of a sent Transfer
    parser.add_argument("--status", help="Tracking ID of the Transfer to check STATUS of.", required=False)
    args = parser.parse_args()
    return args


def interactive_user_choice():
    mode = input("Do you want to send or receive files? (send/receive/status/exit)?\n").lower()
    if mode == "cancel" or mode == "abort" or mode == "exit":
        return False
    return mode


def transfer_status_interactive(default_server_url, default_sender_email, origin):
    send_server = input(f"Which server do you want to use to check a Transfer status? (default={default_server_url})\n")
    if send_server == "":
        send_server = default_server_url
    print(f"Checking transfer status using {send_server}")
    sender_email = input(f"From which email do you want to send transfers? (default={default_sender_email})\n")
    if sender_email == "":
        sender_email = default_sender_email
    transfer_transfer_id = input("Which transfer ID do you want to check the status of? (blank=all)\n")
    transfer_status(origin, send_server, sender_email, transfer_transfer_id)


def send_transfer_interactive(
    default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
):
    send_server = input(f"Which server do you want to use to send a Transfer? (default={default_server_url})\n")
    if send_server == "":
        send_server = default_server_url
    print(f"Sending transfer using {send_server}")

    sender_email = input(f"From which email do you want to send transfers? (default={default_sender_email})\n")
    if sender_email == "":
        sender_email = default_sender_email
    sender_name = input(f"What is the name of the sender? (default={default_sender_name})\n")
    if sender_name == "":
        sender_name = default_sender_name
    sender_phone = input(f"What is the phone number of the sender? (default={default_sender_phone})\n")
    if sender_phone == "":
        sender_phone = default_sender_phone
    transfer_expiration = input("When should the transfer expire? (default=2d)\n")
    if transfer_expiration == "":
        transfer_expiration = "2d"
    transfer_password = input("What is the password for the transfer? (blank=Password will be generated)\n")
    files = input(
        "Which files do you want to send? (separate multiple files with a space, default=example_files/test_file.txt)\n"
    )
    if files == "":
        files = "examples/example_files/test_file.txt"
    recipients = input("Which email addresses do you want to send to? (separate multiple addresses with a space)\n")
    cc = input("Which email addresses do you want to cc? (separate multiple addresses with a space)\n")
    bcc = input("Which email addresses do you want to bcc? (separate multiple addresses with a space)\n")
    subject = input("What is the subject of the transfer? (blank=default Cryptshare subject)\n")
    message = input(
        "What is the Notification message of the transfer? (blank=default Cryptshare Notification message)\n"
    )

    send_transfer(
        origin,
        send_server,
        sender_email,
        sender_name,
        sender_phone,
        transfer_password,
        transfer_expiration,
        files,
        recipients,
        cc=cc,
        bcc=bcc,
        subject=subject,
        message=message,
    )


def download_transfer_interactive(default_server_url, origin):
    dl_server = input(f"From which server do you want to download a Transfer? (default={default_server_url}) \n")
    if dl_server == "":
        dl_server = default_server_url
    print(f"Downloading from {dl_server}")

    recipient_transfer_id = input(f"Which transfer ID did you receive from {default_server_url}?\n")
    password = input(f"What is the PASSWORD for transfer {recipient_transfer_id}?\n")

    default_path = recipient_transfer_id
    save_path = default_path
    user_path = input(f"Where do you want to save the downloaded files? (default=transfers/{default_path})")
    if user_path != "":
        save_path = user_path
    receive_transfer(origin, dl_server, recipient_transfer_id, password, save_path)


def main():
    setup_logging()
    inputs = parse_args()
    default_server_url = os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com")
    default_sender_email = os.getenv("CRYPTSHARE_SENDER_EMAIL", None)
    default_sender_name = os.getenv("CRYPTSHARE_SENDER_NAME", "REST-API Sender")
    default_sender_phone = os.getenv("CRYPTSHARE_SENDER_PHONE", "0")
    origin = os.getenv("CRYPTSHARE_CORS_ORIGIN", "https://localhost")
    if inputs.server:
        default_server_url = inputs.server
    if inputs.email:
        default_sender_email = inputs.email
    if inputs.name:
        default_sender_name = inputs.name
    if inputs.phone:
        default_sender_phone = inputs.phone

    if inputs.mode == "send":
        new_transfer_password = inputs.password
        send_transfer(
            origin,
            default_server_url,
            default_sender_email,
            default_sender_name,
            default_sender_phone,
            new_transfer_password,
            inputs.expiration,
            inputs.file,
            inputs.to,
            cc=inputs.cc,
            bcc=inputs.bcc,
            subject=inputs.subject,
            message=inputs.message,
        )
        return
    elif inputs.mode == "receive":
        recipient_transfer_id = inputs.transfer
        password = inputs.password
        save_path = recipient_transfer_id
        receive_transfer(origin, default_server_url, recipient_transfer_id, password, save_path)
        return
    elif inputs.mode == "status":
        transfer_status(default_server_url, default_sender_email, inputs.status)
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
