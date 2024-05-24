import os

from helpers import TqdmCryptshareDownload
from tqdm import tqdm

from cryptshare import CryptshareClient


def receive_transfer(
    dl_server, recipient_transfer_id, password, save_path, download_zip: bool = False, download_eml: bool = False
) -> None:
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
    if download_eml:
        download.download_eml_file(directory)
        print(f"Downloaded Transfer {recipient_transfer_id} as eml file  to {directory} complete.")
        return

    if download_zip:
        download.download_zip_file(directory)
        print(f"Downloaded Transfer {recipient_transfer_id} as zip file  to {directory} complete.")
        return

    download.download_all_files(directory)
