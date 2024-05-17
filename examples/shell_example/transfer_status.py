import logging

from helpers import verify_sender

from cryptshare.Client import Client as CryptshareClient
from cryptshare.Transfer import Transfer
from cryptshare.TransferSettings import TransferSettings

logger = logging.getLogger(__name__)


def print_transfer_status(status):
    logger.info("Printing user friendly transfer status")
    logger.debug(f"Status data: {status}")
    files = status["files"]
    num_files = len(files)
    recipients = status["recipients"]
    print(f" status: {status['state']}")
    if status["warnings"] is not False:
        print("Warnings:")
        for warning in status["warnings"]:
            print(f"  {warning}")
    print(f" Files: {num_files}")
    print(" Recipients:")
    for recipient in recipients:
        print(f"  {recipient['mail']}")
        print(f"   Transfer ID: {recipient['id']}")
        print(f"   Download URL: {recipient['downloadUrl']}")
        print("   Files:")
        for file in recipient["fileDownloads"]:
            print(f"    {file['id']}")
            for access in file["downloads"]:
                print(f"     {access['retrievalMethod']}: {access['downloadDate']}")
            if not file["downloads"]:
                print("     No downloads")
    print(" Files:")
    for file in files:
        if file["removed"]:
            print(f"  {file['id']} - removed: {file['removalCause']}")
        else:
            print(f"  {file['id']} - Provided")


def print_transfer_status_list(transfers, send_server, sender_email, cryptshare_client):
    logger.info("Printing user friendly transfer status list")
    logger.debug(f"Status data: {transfers}")
    for list_transfer in transfers:
        tracking_id = list_transfer["trackingId"]
        print(f"Transfer status for Tracking ID {tracking_id}:")
        transfer = Transfer(cryptshare_client.header.general, [], [], [], TransferSettings(sender_email))
        status_location = f"{send_server}/api/users/{sender_email}/transfers/{tracking_id}"
        transfer.set_location(status_location)
        transfer = transfer.get_transfer_status()
        status = transfer["status"]
        print_transfer_status(status)


def transfer_status(
    send_server,
    sender_email,
    transfer_transfer_id=None,
    cryptshare_client=None,
):
    if cryptshare_client is None:
        cryptshare_client = CryptshareClient(send_server)

    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()
    cryptshare_client.set_email(sender_email)

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()

    # request verification for sender if not verified already
    verify_sender(cryptshare_client, sender_email)

    if transfer_transfer_id is None:
        all_transfers = cryptshare_client.get_transfers()
        logger.debug("Transfer status for all transfers\n")
        print_transfer_status_list(all_transfers, send_server, sender_email, cryptshare_client)
        return

    logger.debug(f"Transfer status for transfer {transfer_transfer_id}\n")
    transfer = Transfer(cryptshare_client.header.general, [], [], [], TransferSettings(sender_email))
    status_location = f"{send_server}/api/users/{sender_email}/transfers/{transfer_transfer_id}"
    transfer.set_location(status_location)
    transfer = transfer.get_transfer_status()
    print(f"Transfer status for Tracking ID {transfer_transfer_id}:")
    status = transfer["status"]
    print_transfer_status(status)
    return
