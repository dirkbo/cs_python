import logging
import pprint

from cryptshare import CryptshareClient
from examples.shell_example.helpers import (
    ShellCryptshareSender,
    ShellCryptshareValidators,
)

logger = logging.getLogger(__name__)


def status_transfer(
    cryptshare_client: CryptshareClient = None,
    transfer_tracking_id=None,
):
    """
    :param cryptshare_client:
    :param transfer_tracking_id:
    :return:
    """
    if transfer_tracking_id is not None:
        if not ShellCryptshareValidators.is_valid_tracking_id(transfer_tracking_id):
            logger.error(f"Invalid transfer tracking id: {transfer_tracking_id}")
            return

    sender = ShellCryptshareSender("", "", cryptshare_client.sender_email)
    sender.setup_and_verify_sender(cryptshare_client)

    if transfer_tracking_id is None or transfer_tracking_id == "":
        all_transfers = cryptshare_client.transfer_status()
        logger.debug("Transfer status for all transfers\n")
        print(f"Transfer status for all transfers from {sender.email}:")
        pprint.pprint(all_transfers)
        return

    logger.debug(f"Transfer status for transfer {transfer_tracking_id}\n")
    transfers_status = cryptshare_client.transfer_status(transfer_tracking_id=transfer_tracking_id)
    pprint.pprint(transfers_status)
    return
