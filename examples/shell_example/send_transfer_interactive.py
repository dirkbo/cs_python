import argparse
import inspect
import itertools
import logging
import os
import sys
from datetime import datetime, timedelta

import questionary

# To work from examples folder, parent folder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, parentdir)

from helpers import (
    QuestionaryCryptshareSender,
    questionary_ask_for_sender,
    clean_expiration,
    is_valid_expiration,
    is_valid_multiple_emails, clean_string_list,
)
from send_transfer import TqdmTransfer

from cryptshare import CryptshareClient, CryptshareValidators
from cryptshare.CryptshareNotificationMessage import CryptshareNotificationMessage
from cryptshare.CryptshareTransferSecurityMode import CryptshareTransferSecurityMode, SecurityModes
from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings

logger = logging.getLogger(__name__)


def send_transfer_interactive(
        default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
):
    send_server = questionary.text(
        "Which server do you want to use to send a Transfer?\n",
        default=default_server_url,
        validate=CryptshareValidators.is_valid_server_url,
    ).ask()
    if send_server == "":
        send_server = default_server_url
    cryptshare_client = CryptshareClient(send_server)
    cryptshare_client.read_client_store()
    print(f"Sending transfer using {send_server}")

    sender_email, sender_name, sender_phone = questionary_ask_for_sender(
        default_sender_email,
        default_sender_name,
        default_sender_phone
    )

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    sender = QuestionaryCryptshareSender(sender_name, sender_phone, sender_email)
    sender.setup_and_verify_sender(cryptshare_client)

    all_recipients = []
    recipient_policy_ok = False
    disallow_continue = "No Recipients added"
    disallow_remove = "No recipients added to remove."
    do_continue = False
    recipients_list = []
    cc_list = []
    bcc_list = []

    while not do_continue:
        recipients = ""
        cc = ""
        bcc = ""
        new_recipients_list = recipients_list.copy()
        new_cc_list = cc_list.copy()
        new_bcc_list = bcc_list.copy()
        recipient_selection = questionary.select(
            f"Recipients for your Transfer:\n To: {new_recipients_list}\n CC: {new_cc_list}\n BCC: {new_bcc_list}\n",
            choices=[
                questionary.Choice(title="Add To Recipient", value="AddTo"),
                questionary.Choice(title="Add CC Recipient", value="AddCC"),
                questionary.Choice(title="Add Bcc Recipient", value="AddBcc"),
                questionary.Choice(title="Remove Recipient", value="Remove", disabled=disallow_remove),
                questionary.Choice(title="Continue", value="Continue", disabled=disallow_continue, shortcut_key="c"),
                questionary.Choice(title="Abort", value="Abort", shortcut_key="q"),
            ],
            use_shortcuts=True,
            ).ask()
        if recipient_selection == "Remove":
            select_remove = True
            while select_remove:
                remove_choices = [questionary.Choice(title=f"{recipient}", value=recipient) for recipient in all_recipients] + [
                    questionary.Choice(title="Back", value="Back", shortcut_key="b")
                    ]
                select_remove_choice = questionary.select("Which recipient do you want to remove?",
                                                          choices=remove_choices,
                                                          use_shortcuts=True,
                                                          ).ask()
                if select_remove_choice == "Back":
                    select_remove = False
                    new_cc_list = cc_list
                    new_bcc_list = bcc_list
                    new_recipients_list = recipients_list
                    continue
                try:
                    recipients_list.remove(select_remove_choice)
                except ValueError:
                    pass
                try:
                    cc_list.remove(select_remove_choice)
                except ValueError:
                    pass
                try:
                    bcc_list.remove(select_remove_choice)
                except ValueError:
                    pass
                all_recipients = list(itertools.chain(recipients_list, cc_list, bcc_list))

        if recipient_selection == "Abort":
            return
        if recipient_selection == "AddTo":
            recipients = questionary.text(
                "Which email addresses do you want to send to? (separate multiple addresses with a space)\n",
                validate=is_valid_multiple_emails,
            ).ask()
        if recipient_selection == "AddCC":
            cc = questionary.text(
                "Which email addresses do you want to cc? (separate multiple addresses with a space)\n",
                validate=is_valid_multiple_emails,
            ).ask()
        if recipient_selection == "AddBcc":
            bcc = questionary.text(
                "Which email addresses do you want to bcc? (separate multiple addresses with a space)\n",
                validate=is_valid_multiple_emails,
            ).ask()

        # Validate policy for recipients before adding them
        new_recipients_list.extend(clean_string_list(recipients))
        new_cc_list.extend(clean_string_list(cc))
        new_bcc_list.extend(clean_string_list(bcc))
        new_all_recipients = list(itertools.chain(new_recipients_list, new_cc_list, new_bcc_list))
        # All recipients list needed for policy request

        logger.debug(f"{len(all_recipients)} Recipients: {all_recipients} New Recipients: {new_all_recipients}")
        if len(new_all_recipients) == 0:
            disallow_continue = "Please provide at least one recipient, cc recipient or bcc recipient."
            disallow_remove = "No recipients added to remove."
            continue
        disallow_remove = False

        policy_response = cryptshare_client.get_policy(new_all_recipients)
        valid_policy = policy_response.get("allowed")
        if not valid_policy:
            print("Policy does not allow adding these recipients!")
            logger.debug(f"Policy response: {policy_response}")
            recipient_policy_ok = False
            continue
        else:
            cc_list = new_cc_list
            bcc_list = new_bcc_list
            recipients_list = new_recipients_list
            all_recipients = new_all_recipients
            recipient_policy_ok = True
            disallow_continue = False

        if recipient_selection == "Continue" and recipient_policy_ok is True and disallow_continue is False:
            do_continue = True

    transfer_password = questionary.password(
        "What is the password for the transfer? (blank=Password will be generated)\n"
    ).ask()

    send_password_sms = False
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

    # Transfer Session is open loop. Options: Add/Remove Files, Change expiration date, send Transfer, abort
    do_send = False
    can_send_disabled = "No Files added"
    do_abort = False
    transfer_expiration = "5d"
    expiration_date = datetime.now() + timedelta(days=5)
    subject = ""
    message = ""
    files_list = []
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

    #  Start of transfer on server side
    transformed_recipients = [{"mail": recipient} for recipient in recipients_list]
    transformed_cc_recipients = [{"mail": recipient} for recipient in cc_list]
    transformed_bcc_recipients = [{"mail": recipient} for recipient in bcc_list]
    transfer = TqdmTransfer(
        settings,
        to=transformed_recipients,
        cc=transformed_cc_recipients,
        bcc=transformed_bcc_recipients,
        cryptshare_client=cryptshare_client,
    )

    transfer.start_transfer_session()
    transfer.update_transfer_settings(settings)

    while do_send is False and do_abort is False:
        number_of_files = len(files_list)
        number_of_recipients = len(all_recipients)
        if number_of_files > 0:
            can_send_disabled = False
        else:
            can_send_disabled = "Add at least 1 files to send a Transfer."
        session_option = questionary.select(
            f"Transfer Session is open. What do you want to do?\n"
            f" To: {recipients_list}\n"
            f" CC: {cc_list}\n"
            f" BCC: {bcc_list}\n"
            f" Files:{files_list}\n"
            f" Notification subject: {subject}\n"
            f" Notification message: {message}\n",
            choices=[
                questionary.Choice(title="Add a file", value="AddFile"),
                questionary.Choice(title="Remove a file", value="RemoveFile"),
                questionary.Choice(title=f"Change expiration date ({transfer_expiration})", value="ChangeExpiration"),
                questionary.Choice(title=f"Set custom Notification message and subject", value="SetMessage"),
                questionary.Choice(title=f"Upload {number_of_files} files and send Transfer to {number_of_recipients} recipients", value="SendTransfer", disabled=can_send_disabled, shortcut_key="s"),
                questionary.Choice(title="Abort", value="AbortTransfer", shortcut_key="q"),
            ],
            use_shortcuts=True,
        ).ask()
        if session_option == "SendTransfer":
            for file in files_list:
                transfer.upload_file(file)
            pre_transfer_info = transfer.get_transfer_settings()
            logger.debug(f"Pre-Transfer info: \n{pre_transfer_info}")
            transfer.send_transfer()
            post_transfer_info = transfer.get_transfer_status()
            logger.debug(f" Post-Transfer info: \n{post_transfer_info}")
            do_send = True
            continue
        if session_option == "AbortTransfer":
            do_abort = True
            del transfer
            # Abort transfer on cryptshare server bei deleting the transfer object
            return
        if session_option == "AddFile":
            # Adding files to Transfer Session
            files = questionary.path(
                "Which file do you want to add? (separate multiple files with a space, default=example_files/test_file.txt)\n",
                default="examples/example_files/test_file.txt",
            ).ask()
            if files == "":
                files = "examples/example_files/test_file.txt"
            files = clean_string_list(files)
            files_list.extend(files)
            files_list = list(dict.fromkeys(files_list))
        if session_option == "RemoveFile":
            select_remove = True
            while select_remove:
                remove_choices = [questionary.Choice(title=f"{file}", value=file) for file in files_list] + [
                    questionary.Choice(title="Back", value="Back", shortcut_key="b")
                ]
                select_remove_choice = questionary.select("Which file do you want to remove?", choices=remove_choices, use_shortcuts=True).ask()
                if select_remove_choice == "Back":
                    select_remove = False
                    continue
                try:
                    files_list.remove(select_remove_choice)
                except ValueError:
                    pass
        if session_option == "ChangeExpiration":
            transfer_expiration = questionary.text(
                "When should the transfer expire?\n",
                default=f"{transfer_expiration}",
                validate=is_valid_expiration,
            ).ask()
            if transfer_expiration == "":
                transfer_expiration = "2d"
            print(f"Transfer expiration: {transfer_expiration}")
            expiration_date = clean_expiration(transfer_expiration)
        if session_option == "SetMessage":
            subject = questionary.text(
                "What is the subject of the transfer? (blank=default Cryptshare subject)\n").ask()
            message = questionary.text(
                "What is the Notification message of the transfer? (blank=default Cryptshare Notification message)\n"
            ).ask()
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
        transfer.update_transfer_settings(settings)