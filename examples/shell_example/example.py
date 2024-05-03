import argparse
import os
import sys
import inspect

# To work from exapmples folder, parentfolder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, parentdir)

import requests
from tqdm import tqdm

from cryptshare.Client import Client as CryptshareClient
from cryptshare.NotificationMessage import NotificationMessage
from cryptshare.SecurityMode import SecurityMode
from cryptshare.Sender import Sender as CryptshareSender
from cryptshare.TransferSettings import TransferSettings
from cryptshare.helpers import clean_string_list, clean_expiration


def parse_args():
    parser = argparse.ArgumentParser(description="Send and receive files using Cryptshare.")
    parser.add_argument(
        "-m", "--mode", help="send or receive files", choices=["send", "receive", "interactive"], required=False
    )
    parser.add_argument("-s", "--server", help="Cryptshare Server URL", required=False)
    # Receive a Transfer
    parser.add_argument("-t", "--transfer", help="Tracking ID of the Transfer to RECEIVE", required=False)
    parser.add_argument("-p", "--password", help="Password of the Transfer to RECEIVE", required=False)
    # Send a Transfer
    parser.add_argument("-e", "--email", help="Email address to SEND from.")
    parser.add_argument("-n", "--name", help="Name of the Sender to SEND from.")
    parser.add_argument("--phone", help="Phone number of the sender to SEND from.")
    parser.add_argument("-f", "--file", help="Path of a file or a folder of files to SEND.", action="append")
    parser.add_argument("--to", help="A Recipient email address to SEND to.", action="append")
    parser.add_argument("--cc", help="A CC email address(es) to SEND to.", action="append")
    parser.add_argument("--bcc", help="A BCC email address(es) to SEND to.", action="append")
    parser.add_argument("--subject", help="Subject of the Transfer to SEND.")
    parser.add_argument("--message", help="Custom notification Message of the Transfer to SEND.")
    parser.add_argument("--expiration", help="Expiration of the Transfer to SEND.")
    args = parser.parse_args()
    return args


def interactive_user_choice():
    mode = input("Do you want to send or receive files? (send/receive/exit)?\n").lower()
    if mode == "cancel" or mode == "abort" or mode == "exit":
        return False
    return mode


def send_transfer(
    origin,
    send_server,
    sender_email,
    sender_name,
    sender_phone,
    transfer_password,
    expiration_date,
    files,
    recipients,
    cc="",
    bcc="",
    subject="",
    message="",
    cryptshare_client=None,
):
    if cryptshare_client is None:
        cryptshare_client = CryptshareClient(send_server)

    files = clean_string_list(files)
    recipients = clean_string_list(recipients)
    cc = clean_string_list(cc)
    bcc = clean_string_list(bcc)
    expiration_date = clean_expiration(expiration_date)

    transformed_recipients = []
    for recipient in recipients:
        transformed_recipients.append({"mail": recipient})
    transformed_cc_recipients = []
    for recipient in cc:
        transformed_cc_recipients.append({"mail": recipient})
    transformed_bcc_recipients = []
    for recipient in bcc:
        transformed_bcc_recipients.append({"mail": recipient})

    all_recipients = []
    all_recipients.extend(recipients)
    all_recipients.extend(cc)
    all_recipients.extend(bcc)
    # All recipients list needed for policy request

    print(f"Sending Transfer from {sender_email} using {send_server}")
    print(f" To Recipients: {recipients}")
    print(f" CC Recipients: {cc}")
    print(f" BCC Recipients: {bcc}")
    print(f" Files: {files}")

    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    cryptshare_client.set_email(sender_email)
    # request verification for sender if not verified already
    if cryptshare_client.is_verified() is False:
        cryptshare_client.request_code()
        verification_code = input(f"Please enter the verification code sent to your email address ({sender_email}):\n")
        cryptshare_client.verify_code(verification_code.strip())
        if cryptshare_client.is_verified() is False:
            print("Verification failed.")
            return

    # ToDo: show password rules to user, when asking for password
    transfer_security_mode = SecurityMode(password=transfer_password, mode="MANUAL")
    if transfer_password == "" or transfer_password is None:
        transfer_password = cryptshare_client.get_password().get("password")
        print(f"Generated Password to receive Files: {transfer_password}")
        transfer_security_mode = SecurityMode(password=transfer_password, mode="GENERATED")
    else:
        passwort_validated_response = cryptshare_client.validate_password(transfer_password)
        valid_password = passwort_validated_response.get("valid")
        if not valid_password:
            print("Passwort is not valid.")
            password_rules = cryptshare_client.get_password_rules()
            print(f"Passwort rules:\n{password_rules}")
            return

    policy_response = cryptshare_client.get_policy(all_recipients)
    valid_policy = policy_response.get("allowed")
    if not valid_policy:
        print("Policy not valid.")
        print(f"Policy response: {policy_response}")
        return

    #  Transfer definition
    sender = CryptshareSender(sender_name, sender_phone)
    notification = NotificationMessage(message, subject)
    subject = subject if subject != "" else None
    settings = TransferSettings(
        sender,
        notification_message=notification,
        subject=subject,
        send_download_notifications=True,
        security_mode=transfer_security_mode,
        expiration_date=expiration_date.astimezone().isoformat(),
    )

    #  Start of transfer on server side
    transfer = cryptshare_client.start_transfer(
        {
            "bcc": transformed_bcc_recipients,
            "cc": transformed_cc_recipients,
            "to": transformed_recipients,
        },
        settings,
    )
    for file in files:
        transfer.upload_file(file)

    # pre_transfer_info = transfer.get_transfer_settings()
    # print(f" Pre-Transfer info: \n{pre_transfer_info}")
    transfer.send_transfer()
    # post_transfer_info = transfer.get_transfer_status()
    # print(f" Post-Transfer info: \n{post_transfer_info}")
    # cryptshare_client.write_client_store()
    # ToDo: write client store to file results in an error when loading
    print("Transfer sent successfully.")


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
    transfer_password = input("What is the password for the transfer?\n")
    files = input(
        "Which files do you want to send? (separate multiple files with a space, default=example_files/test_file.txt)\n"
    )
    if files == "":
        files = "example_files/test_file.txt"
    recipients = input("Which email addresses do you want to send to? (separate multiple addresses with a space)\n")
    cc = input("Which email addresses do you want to cc? (separate multiple addresses with a space)\n")
    bcc = input("Which email addresses do you want to bcc? (separate multiple addresses with a space)\n")
    subject = input("What is the subject of the transfer? blank=default Cryptshare subject\n")
    message = input("What is the Notification message of the transfer? blank=default Cryptshare Notification message\n")

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


def download_transfer(origin, dl_server, recipient_transfer_id, password, save_path):
    cryptshare_client = CryptshareClient(dl_server)
    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    download = cryptshare_client.download(recipient_transfer_id, password)
    files_info = download.download_files_info()
    directory = os.path.join("transfers", save_path)
    print(f"Downloading Transfer {recipient_transfer_id} from {dl_server} to {directory}...")
    for file in files_info:
        response = requests.get(dl_server + file["href"], stream=True)
        full_path = os.path.join(directory, file["fileName"])
        if not os.path.exists(directory):
            os.makedirs(directory)
        print(f"Downloading {file['fileName']} to {full_path}")
        with open(full_path, "wb") as handle:
            for data in tqdm(
                response.iter_content(),
                desc=file["fileName"],
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                total=int(file["size"]),
            ):
                handle.write(data)

    print(f"Downloaded Transfer {recipient_transfer_id} to {directory} complete.")


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
    download_transfer(origin, dl_server, recipient_transfer_id, password, save_path)


def main():
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
        download_transfer(origin, default_server_url, recipient_transfer_id, password, save_path)
        return
    while True:
        mode = interactive_user_choice()
        if mode == "send":
            send_transfer_interactive(
                default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
            )
        elif mode == "receive":
            download_transfer_interactive(default_server_url, origin)
        if mode is False:
            break


if __name__ == "__main__":
    main()
