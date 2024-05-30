import logging

from receive_transfer import receive_transfer

logger = logging.getLogger(__name__)


def receive_transfer_by_url(
    download_url: str, save_path: str = None, download_zip: bool = False, download_eml: bool = False
) -> None:
    """
    Downloads a transfer from a Cryptshare server.

    Parameters:
    download_url (str): The URL of the Cryptshare Download, including transfer-id and password.
    save_path (str): The path where the downloaded files should be saved.
    zip (bool): Download the transfer as a zip file.
    eml (bool): Download the transfer as an eml file (if it contains a confidential message).

    Returns:
    None
    """

    # Extract server from download_url
    dl_server = download_url.replace("https://", "").replace("http://", "").split("/")[0]
    protocol = "https://" if download_url.startswith("https://") else "http://"
    dl_server = f"{protocol}{dl_server}"
    logger.debug(f"dl_server: {dl_server}")

    # Extract transfer-id and password from download_url
    params = download_url.replace(f"{protocol}{dl_server}/", "").replace("&", "?").split("?")
    logger.debug(f"download_url: {download_url}")
    logger.debug(f"params: {params}")
    recipient_transfer_id = None
    password = None
    for param in params:
        if param.startswith("id="):
            recipient_transfer_id = param.split("=")[1]
        if param.startswith("password="):
            password = param.split("=")[1]
    if recipient_transfer_id is None or password is None:
        raise ValueError("Invalid download_url. Must contain id and password parameters.")

    if save_path is None:
        save_path = recipient_transfer_id

    logger.debug(
        f"Downloading Transfer {recipient_transfer_id} from {dl_server} with password {password} to {save_path}..."
    )
    receive_transfer(dl_server, recipient_transfer_id, password, save_path, download_zip, download_eml)
