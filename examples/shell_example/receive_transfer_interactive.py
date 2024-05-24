import questionary
from helpers import ExtendedCryptshareValidators

from examples.shell_example.receive_transfer import receive_transfer


def receive_transfer_interactive(default_server_url):
    dl_server = questionary.text(
        "From which server do you want to download a Transfer?",
        default=default_server_url,
        validate=ExtendedCryptshareValidators.is_valid_server_url,
    ).ask()
    if dl_server == "":
        dl_server = default_server_url
    print(f"Downloading from {dl_server}")

    recipient_transfer_id = questionary.text(
        f"Which transfer ID did you receive from {default_server_url}?\n",
        default="",
        validate=ExtendedCryptshareValidators.is_valid_transfer_id,
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
