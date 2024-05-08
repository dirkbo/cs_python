from cryptshare.Client import Client as CryptshareClient
from cryptshare.NotificationMessage import NotificationMessage
from cryptshare.SecurityMode import SecurityMode
from cryptshare.Sender import Sender as CryptshareSender
from cryptshare.TransferSettings import TransferSettings
from helpers import clean_string_list, clean_expiration

from examples.shell_example.helpers import verify_sender


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
    cryptshare_client=None,
):
    if cryptshare_client is None:
        cryptshare_client = CryptshareClient(send_server)

    files = clean_string_list(files)
    recipients = clean_string_list(recipients)
    cc = clean_string_list(cc)
    bcc = clean_string_list(bcc)
    expiration_date = clean_expiration(expiration_date)

    transformed_recipients = []
    for recipient in recipients:
        transformed_recipients.append({"mail": recipient})
    transformed_cc_recipients = []
    for recipient in cc:
        transformed_cc_recipients.append({"mail": recipient})
    transformed_bcc_recipients = []
    for recipient in bcc:
        transformed_bcc_recipients.append({"mail": recipient})

    all_recipients = []
    all_recipients.extend(recipients)
    all_recipients.extend(cc)
    all_recipients.extend(bcc)
    # All recipients list needed for policy request

    print(f"Sending Transfer from {sender_email} using {send_server}")
    print(f" To Recipients: {recipients}")
    print(f" CC Recipients: {cc}")
    print(f" BCC Recipients: {bcc}")
    print(f" Files: {files}")

    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()
    cryptshare_client.set_email(sender_email)

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        # cryptshare_client.cors(origin)
        # ToDo: After cors check, client verification from store is not working anymore
        pass

    verify_sender(cryptshare_client, sender_email)

    # ToDo: show password rules to user, when asking for password
    transfer_security_mode = SecurityMode(password=transfer_password, mode="MANUAL")
    if transfer_password == "" or transfer_password is None:
        transfer_password = cryptshare_client.get_password().get("password")
        print(f"Generated Password to receive Files: {transfer_password}")
        transfer_security_mode = SecurityMode(password=transfer_password, mode="GENERATED")
    else:
        passwort_validated_response = cryptshare_client.validate_password(transfer_password)
        valid_password = passwort_validated_response.get("valid")
        if not valid_password:
            print("Passwort is not valid.")
            password_rules = cryptshare_client.get_password_rules()
            print(f"Passwort rules:\n{password_rules}")
            return

    policy_response = cryptshare_client.get_policy(all_recipients)
    valid_policy = policy_response.get("allowed")
    if not valid_policy:
        print("Policy not valid.")
        print(f"Policy response: {policy_response}")
        return

    #  Transfer definition
    sender = CryptshareSender(sender_name, sender_phone)
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
        transfer.upload_file(file)

    # pre_transfer_info = transfer.get_transfer_settings()
    # print(f" Pre-Transfer info: \n{pre_transfer_info}")
    transfer.send_transfer()
    post_transfer_info = transfer.get_transfer_status()
    print(f" Post-Transfer info: \n{post_transfer_info}")
    cryptshare_client.write_client_store()
    transfer_id = transfer.get_transfer_id()
    print(f"Transfer {transfer_id} uploaded successfully.")
