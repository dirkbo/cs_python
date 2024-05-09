import os

import requests
from tqdm import tqdm

from cryptshare.Client import Client as CryptshareClient


def download_file(dl_server, file, directory):
    response = requests.get(dl_server + file["href"], stream=True)
    full_path = os.path.join(directory, file["fileName"])
    os.makedirs(directory, exist_ok=True)
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


def receive_transfer(origin, dl_server, recipient_transfer_id, password, save_path):
    """
    Downloads a transfer from a Cryptshare server.

    Parameters:
    origin (str): The origin of the request.
    dl_server (str): The URL of the Cryptshare server.
    recipient_transfer_id (str): The Transfer ID of the transfer to download.
    password (str): The password for the transfer.
    save_path (str): The path where the downloaded files should be saved.

    Returns:
    None
    """
    cryptshare_client = CryptshareClient(dl_server)
    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()

    directory = os.path.join("transfers", save_path)
    print(f"Downloading Transfer {recipient_transfer_id} from {dl_server}...")
    download = cryptshare_client.download(recipient_transfer_id, password)
    files_info = download.download_files_info()

    for file in files_info:
        download_file(dl_server, file, directory)

    print(f"Downloaded Transfer {recipient_transfer_id} to {directory} complete.")
