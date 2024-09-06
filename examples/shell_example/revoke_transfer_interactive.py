import questionary
from helpers import ShellCryptshareSender, ShellCryptshareValidators
from revoke_transfer import revoke_transfer

from cryptshare import CryptshareClient


def revoke_transfer_interactive(default_server_url, default_sender_email):
    send_server = questionary.text(
        "Which server do you want to use to revoke a sent Transfer?\n",
        default=default_server_url,
        validate=ShellCryptshareValidators.is_valid_server_url,
    ).ask()
    if send_server == "":
        send_server = default_server_url
    print(f"Revoking transfer from {send_server}")
    client = CryptshareClient(default_server_url)

    if default_sender_email is None or not ShellCryptshareValidators.is_valid_email_or_blank(default_sender_email):
        default_sender_email = ""
    sender_email = questionary.text(
        "For which email do you want to revoke a sent transfer?\n",
        default=default_sender_email,
        validate=ShellCryptshareValidators.is_valid_email_or_blank,
    ).ask()
    if sender_email == "":
        sender_email = default_sender_email
    transfer_transfer_id = questionary.text(
        "Which transfer ID do you want to revoke?\n",
        validate=ShellCryptshareValidators.is_valid_tracking_id,
    ).ask()

    sender = ShellCryptshareSender(email=sender_email, name="REST-API Sender", phone="0")
    sender.setup_and_verify_sender(client)
    revoke_transfer(client, transfer_transfer_id)
