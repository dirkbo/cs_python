import logging
import pprint

from helpers import ShellCryptshareSender, ShellCryptshareValidators

from cryptshare import CryptshareClient

logger = logging.getLogger(__name__)


def revoke_transfer(
    cryptshare_client: CryptshareClient = None,
    transfer_tracking_id=None,
):
    """
    :param cryptshare_client:
    :param transfer_tracking_id:
    :return:
    """
    if transfer_tracking_id is None or transfer_tracking_id == "":
        logger.error(f"No transfer tracking id: {transfer_tracking_id}")
        return

    if not ShellCryptshareValidators.is_valid_tracking_id(transfer_tracking_id):
        logger.error(f"Invalid transfer tracking id: {transfer_tracking_id}")
        return

    sender = ShellCryptshareSender("", "", cryptshare_client.sender_email)
    sender.setup_and_verify_sender(cryptshare_client)

    logger.debug(f"Transfer status for transfer {transfer_tracking_id}\n")
    transfers_status = cryptshare_client.revoke_active_transfer(transfer_tracking_id=transfer_tracking_id)
    pprint.pprint(transfers_status)
    return
