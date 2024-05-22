import hashlib
import itertools
import logging

from helpers import (
    QuestionaryCryptshareSender,
    clean_string_list,
    send_password_with_twilio,
    twilio_sms_is_configured,
)
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from cryptshare import CryptshareClient
from cryptshare.CryptshareNotificationMessage import CryptshareNotificationMessage
from cryptshare.CryptshareTransfer import CryptshareTransfer, TransferFile
from cryptshare.CryptshareTransferSecurityMode import (
    CryptshareTransferSecurityMode,
    SecurityModes,
)
from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings

logger = logging.getLogger(__name__)


class TqdmFile(TransferFile):
    """File class with tqdm progress bar for file upload"""

    def calculate_checksum(self):
        logger.debug("Calculating checksum")  # Calculate file hashsum
        with open(self.path, "rb") as data:
            file_content = data.read()
            self.checksum = hashlib.sha256(file_content).hexdigest()
            print(f"Checksum for {self.name}: {self.checksum}")

    def upload_file_content(self):
        upload_url = f"{self.transfer_session_url}/files/{self._file_id}/content"
        logger.info(f"Uploading file {self.name} content to {upload_url}")

        with open(self.path, "rb") as f:
            with tqdm(total=self.size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                self._request(
                    "PUT",
                    upload_url,
                    data=wrapped_file,
                    verify=self._cryptshare_client.ssl_verify,
                    headers=self._cryptshare_client.header.request_header,
                    handle_response=False,
                )
        return True


class TqdmTransfer(CryptshareTransfer):
    def upload_file(self, path: str, cryptshare_client: CryptshareClient = None):
        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None

        url = f"{self.get_transfer_session_url()}/files"
        logger.debug(f"Uploading file {path} to {url}")

        file = TqdmFile(path, self.tracking_id, self._cryptshare_client)
        file.announce_upload()
        file.upload_file_content()
        self.files.append(file)
        return file


def send_transfer(
    origin,
    send_server,
    sender_email,
    sender_name,
    sender_phone,
    transfer_password,
    expiration_date,
    files,
    recipients,
    cc="",
    bcc="",
    subject="",
    message="",
    recipient_sms_phones=None,
    cryptshare_client=None,
):
    if cryptshare_client is None:
        cryptshare_client = CryptshareClient(send_server)

    files = clean_string_list(files)
    recipients = clean_string_list(recipients)
    cc = clean_string_list(cc)
    bcc = clean_string_list(bcc)

    transformed_recipients = [{"mail": recipient} for recipient in recipients]
    transformed_cc_recipients = [{"mail": recipient} for recipient in cc]
    transformed_bcc_recipients = [{"mail": recipient} for recipient in bcc]
    all_recipients = list(itertools.chain(recipients, cc, bcc))
    # All recipients list needed for policy request

    print(f"Sending Transfer from {sender_email} using {send_server}")
    print(f" To Recipients: {recipients}")
    print(f" CC Recipients: {cc}")
    print(f" BCC Recipients: {bcc}")
    print(f" Subject: {subject}")
    print(f" Message: {message}")
    print(f" Files: {files}")

    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    sender = QuestionaryCryptshareSender(sender_name, sender_phone, sender_email)
    sender.setup_and_verify_sender(cryptshare_client)

    send_password_sms = False
    if twilio_sms_is_configured() and recipient_sms_phones is not None:
        send_password_sms = True

    show_generated_pasword = not send_password_sms
    if recipient_sms_phones and all_recipients:
        if len(recipient_sms_phones) != len(all_recipients):
            logger.debug("Number of SMS recipients does not match number of email recipients.")
            show_generated_pasword = True

    # ToDo: show password rules to user, when asking for password
    transfer_security_mode = CryptshareTransferSecurityMode(password=transfer_password, mode=SecurityModes.MANUAL)
    if transfer_password == "" or transfer_password is None:
        transfer_password = cryptshare_client.get_password().get("password")
        if not show_generated_pasword:
            print("Generated Password to receive Files will be sent via SMS.")
        else:
            print(f"Generated Password to receive Files: {transfer_password}")
            if send_password_sms:
                print(
                    "Number of phone numbers does not match number of email addresses. SMS might not be sent to all recipients."
                )
        transfer_security_mode = CryptshareTransferSecurityMode(password=transfer_password)
    else:
        passwort_validated_response = cryptshare_client.validate_password(transfer_password)
        valid_password = passwort_validated_response.get("valid")
        if not valid_password:
            print("Passwort is not valid.")
            password_rules = cryptshare_client.get_password_rules()
            logger.debug(f"Passwort rules:\n{password_rules}")
            return
        if send_password_sms:
            print("Password to receive Files will be sent via SMS.")

    policy_response = cryptshare_client.get_policy(all_recipients)
    valid_policy = policy_response.get("allowed")
    if not valid_policy:
        print("Policy not valid.")
        logger.debug(f"Policy response: {policy_response}")
        return

    #  Transfer definition
    notification = CryptshareNotificationMessage(message, subject)
    settings = CryptshareTransferSettings(
        sender,
        notification_message=notification,
        send_download_notifications=True,
        security_mode=transfer_security_mode,
        expiration_date=expiration_date,
        senderLanguage=sender.language,
        recipientLanguage=notification.language,
    )
    print(f" Expiration Date: {settings.expiration_date}")

    #  Start of transfer on server side
    transfer = TqdmTransfer(
        settings,
        to=transformed_recipients,
        cc=transformed_cc_recipients,
        bcc=transformed_bcc_recipients,
        cryptshare_client=cryptshare_client,
    )

    transfer.start_transfer_session()
    transfer.update_transfer_settings()
    print("Uploading files to transfer...")
    for file in files:
        transfer.upload_file(file)

    pre_transfer_info = transfer.get_transfer_settings()
    logger.debug(f"Pre-Transfer info: \n{pre_transfer_info}")
    transfer.send_transfer()
    post_transfer_info = transfer.get_transfer_status()
    logger.debug(f" Post-Transfer info: \n{post_transfer_info}")

    print(f"Transfer {transfer.tracking_id} uploaded successfully.")
    if recipient_sms_phones:
        for recipient_sms in recipient_sms_phones:
            send_password_with_twilio(transfer.tracking_id, transfer_password, recipient_sms)
