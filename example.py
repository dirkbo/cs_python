from cryptshare.Client import Client as CryptshareClient
from tqdm import tqdm
import requests
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Send and receive files using Cryptshare.")
    parser.add_argument(
        "-m", "--mode", help="send or receive files", choices=["send", "receive", "interactive"], required=False
    )
    parser.add_argument("-s", "--server", help="Cryptshare Server URL", required=False)
    # Receive a Transfer
    parser.add_argument("-t", "--transfer", help="Tracking ID of the Transfer", required=False)
    parser.add_argument("-p", "--password", help="Password of the Transfer", required=False)
    # Send a Transfer
    # ToDO: Implement sending a Transfer
    args = parser.parse_args()
    return args


def interactive_user_choice():
    mode = input("Do you want to send or receive files? (send/receive/exit)?\n").lower()
    if mode == "cancel" or mode == "abort" or mode == "exit":
        return False
    return mode


def download_transfer(origin, dl_server, recipient_transfer_id, password, save_path):
    cs = CryptshareClient(dl_server)
    #  Reads existing verifications from the 'store' file if any
    cs.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cs.exists_client_id() is False:
        cs.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cs.cors(origin)

    download = cs.download(recipient_transfer_id, password)
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


def main():
    inputs = parse_args()
    default_server_url = os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com")
    origin = os.getenv("CRYPTSHARE_CORS_ORIGIN", "https://localhost")
    if inputs.server:
        default_server_url = inputs.server
        print("Using server: " + default_server_url)
    if inputs.mode == "send":
        print("Not supported yet)")
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
            sender_email = input("From which email do you want to send transfers?\n")

            print(f"You received an E-Mail containing a verification Code at {sender_email}")
            user_verification_code = input("Enter verification code:\n")
            # cs.get_verification_token(user_verification_code)

            print("ToDO: verifying user")
        elif mode == "receive":
            dl_server = input(
                f"From which server do you want to download a Transfer? (default={default_server_url}) \n"
            )
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
        if mode is False:
            break


if __name__ == "__main__":
    main()
