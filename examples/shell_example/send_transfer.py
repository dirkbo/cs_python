import logging
import itertools

from helpers import (
    clean_expiration,
    clean_string_list,
    send_password_with_twilio,
    twilio_sms_is_configured,
    QuestionaryCryptshareSender,
)

from cryptshare import CryptshareClient, CryptshareSender
from cryptshare.NotificationMessage import NotificationMessage
from cryptshare.SecurityMode import SecurityMode
from cryptshare.TransferSettings import TransferSettings

logger = logging.getLogger(__name__)


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
    expiration_date = clean_expiration(expiration_date)

    transformed_recipients = [{"mail": recipient} for recipient in recipients]
    transformed_cc_recipients = [{"mail": recipient} for recipient in cc]
    transformed_bcc_recipients = [{"mail": recipient} for recipient in bcc]
    all_recipients = list(itertools.chain(recipients, cc, bcc))
    # All recipients list needed for policy request

    print(f"Sending Transfer from {sender_email} using {send_server}")
    print(f" To Recipients: {recipients}")
    print(f" CC Recipients: {cc}")
    print(f" BCC Recipients: {bcc}")
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
    transfer_security_mode = SecurityMode(password=transfer_password, mode="MANUAL")
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
        transfer_security_mode = SecurityMode(password=transfer_password, mode="GENERATED")
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
    subject = subject if subject != "" else None
    notification = NotificationMessage(message, subject)
    settings = TransferSettings(
        sender,
        notification_message=notification,
        send_download_notifications=True,
        security_mode=transfer_security_mode,
        expiration_date=expiration_date.astimezone().isoformat(),
    )

    #  Start of transfer on server side
    transfer = cryptshare_client.start_transfer(
        {
            "bcc": transformed_bcc_recipients,
            "cc": transformed_cc_recipients,
            "to": transformed_recipients,
        },
        settings,
    )
    for file in files:
        transfer.upload_file(cryptshare_client, file)

    pre_transfer_info = transfer.get_transfer_settings()
    logger.debug(f"Pre-Transfer info: \n{pre_transfer_info}")
    transfer.send_transfer()
    post_transfer_info = transfer.get_transfer_status()
    logger.debug(f" Post-Transfer info: \n{post_transfer_info}")
    cryptshare_client.write_client_store()
    transfer_id = transfer.get_transfer_id()
    print(f"Transfer {transfer_id} uploaded successfully.")
    if twilio_sms_is_configured() and recipient_sms_phones is not None:
        for recipient_sms in recipient_sms_phones:
            send_password_with_twilio(transfer_id, transfer_password, recipient_sms)
