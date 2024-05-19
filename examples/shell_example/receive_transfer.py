import os

import requests
from tqdm import tqdm

from cryptshare import CryptshareClient
from cryptshare.CryptshareDownload import CryptshareDownload


class TqdmCryptshareDownload(CryptshareDownload):
    """A class to download files from a Cryptshare server with a progress bar."""

    def download_file(self, file, directory) -> None:
        response = requests.get(self.server + file["href"], stream=True)
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

    download = TqdmCryptshareDownload(cryptshare_client, recipient_transfer_id, password)
    download.download_all_files(directory)

    print(f"Downloaded Transfer {recipient_transfer_id} to {directory} complete.")
