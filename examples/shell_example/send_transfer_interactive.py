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
    ShellCryptshareValidators,
    ShellCryptshareSender,
    questionary_ask_for_sender,
)
from send_transfer import ShellCryptshareTransfer

from cryptshare import CryptshareClient
from cryptshare.CryptshareNotificationMessage import CryptshareNotificationMessage
from cryptshare.CryptshareTransferSecurityMode import (
    CryptshareTransferSecurityMode,
    SecurityModes,
)
from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings

logger = logging.getLogger(__name__)


def send_transfer_interactive(
    default_server_url, default_sender_email, default_sender_name, default_sender_phone, origin
):
    send_server = questionary.text(
        "Which server do you want to use to send a Transfer?\n",
        default=default_server_url,
        validate=ShellCryptshareValidators.is_valid_server_url,
    ).ask()
    if send_server == "":
        send_server = default_server_url
    cryptshare_client = CryptshareClient(send_server)
    cryptshare_client.read_client_store()
    print(f"Sending transfer using {send_server}")

    sender_email, sender_name, sender_phone = questionary_ask_for_sender(
        default_sender_email, default_sender_name, default_sender_phone
    )

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    sender = ShellCryptshareSender(sender_name, sender_phone, sender_email)
    sender.setup_and_verify_sender(cryptshare_client)

    all_recipients = []
    recipient_policy_ok = False
    disallow_continue = "No Recipients added"
    disallow_remove = "No recipients added to remove."
    do_continue = False
    recipients_list = []
    cc_list = []
    bcc_list = []

    transfer_policy = None
    while not do_continue:
        recipients = ""
        cc = ""
        bcc = ""
        new_recipients_list = recipients_list.copy()
        new_cc_list = cc_list.copy()
        new_bcc_list = bcc_list.copy()
        selection_message = "Recipients for your Transfer:"
        if new_recipients_list or (not new_cc_list and not new_bcc_list):
            selection_message += "\n To: {}".format(", ".join(new_recipients_list))
        if new_cc_list:
            selection_message += "\n CC: {}".format(", ".join(new_cc_list))
        if new_bcc_list:
            selection_message += "\n BCC: {}".format(", ".join(new_bcc_list))
        selection_message += "\nWhat do you want to do?"
        recipient_selection = questionary.select(
            selection_message,
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
                remove_choices = [
                    questionary.Choice(title=f"{recipient}", value=recipient) for recipient in all_recipients
                ] + [questionary.Choice(title="Back", value="Back", shortcut_key="b")]
                select_remove_choice = questionary.select(
                    "Which recipient do you want to remove?",
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
                validate=ShellCryptshareValidators.is_valid_multiple_emails,
            ).ask()
        if recipient_selection == "AddCC":
            cc = questionary.text(
                "Which email addresses do you want to cc? (separate multiple addresses with a space)\n",
                validate=ShellCryptshareValidators.is_valid_multiple_emails,
            ).ask()
        if recipient_selection == "AddBcc":
            bcc = questionary.text(
                "Which email addresses do you want to bcc? (separate multiple addresses with a space)\n",
                validate=ShellCryptshareValidators.is_valid_multiple_emails,
            ).ask()

        # Validate policy for recipients before adding them
        new_recipients_list.extend(ShellCryptshareValidators.clean_string_list(recipients))
        new_cc_list.extend(ShellCryptshareValidators.clean_string_list(cc))
        new_bcc_list.extend(ShellCryptshareValidators.clean_string_list(bcc))
        new_all_recipients = list(itertools.chain(new_recipients_list, new_cc_list, new_bcc_list))
        # All recipients list needed for policy request

        logger.debug(f"{len(all_recipients)} Recipients: {all_recipients} New Recipients: {new_all_recipients}")
        if len(new_all_recipients) == 0:
            disallow_continue = "Please provide at least one recipient, cc recipient or bcc recipient."
            disallow_remove = "No recipients added to remove."
            continue
        disallow_remove = False

        transfer_policy = cryptshare_client.get_policy(new_all_recipients)
        valid_policy = transfer_policy.get("allowed")
        if not valid_policy:
            print("Policy does not allow adding these recipients!")
            logger.debug(f"Policy response: {transfer_policy}")
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

    #  Password for transfer
    send_password_sms = False
    show_generated_pasword = True
    is_valid_password = False
    human_password_rules = cryptshare_client.get_human_readable_password_rules()

    transfer_security_mode = None
    while not is_valid_password:
        selection_message = "What is the Passwort the recipients will need to use to receive the transfer?"
        selection_message += "\n Password rules:"
        selection_message += "\n  * {}".format("\n  * ".join(human_password_rules))
        selection_message += "\n (blank=Password will be generated)"

        transfer_password = questionary.password(selection_message).ask()
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
            is_valid_password = True
        else:
            passwort_validated_response = cryptshare_client.validate_password(transfer_password)
            is_valid_password = passwort_validated_response.get("valid", False)
            if not is_valid_password:
                print("Passwort is not valid.")
                continue

            if send_password_sms:
                print("Password to receive Files will be sent via SMS.")

    # Transfer Session is open loop. Options: Add/Remove Files, Change expiration date, send Transfer, abort
    do_send = False
    can_send_disabled = "No Files added"
    do_abort = False
    default_transfer_expiration = "2d"
    transfer_expiration = default_transfer_expiration
    expiration_date = ShellCryptshareValidators.clean_expiration(default_transfer_expiration)
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
    transfer = ShellCryptshareTransfer(
        settings,
        to=transformed_recipients,
        cc=transformed_cc_recipients,
        bcc=transformed_bcc_recipients,
        cryptshare_client=cryptshare_client,
    )

    transfer.start_transfer_session()
    transfer.update_transfer_settings(settings)
    transfer_policy_settings = transfer_policy.get("settings", dict())

    while do_send is False and do_abort is False:
        number_of_files = len(files_list)
        number_of_recipients = len(all_recipients)
        if number_of_files > 0:
            can_send_disabled = False
        else:
            can_send_disabled = "Add at least 1 files to send a Transfer."
        selection_message = "Transfer Session is open."
        if recipients_list:
            selection_message += "\n To: {}".format(", ".join(recipients_list))
        if cc_list:
            selection_message += "\n CC: {}".format(", ".join(cc_list))
        if bcc_list:
            selection_message += "\n BCC: {}".format(", ".join(bcc_list))
        if files_list:
            selection_message += "\n Files:{}".format(", ".join(files_list))
        if transfer_expiration != default_transfer_expiration:
            selection_message += f"\n Transfer expiration: {transfer_expiration}"
        if subject != "":
            selection_message += f"\n Notification subject: {subject}"
        if message != "":
            selection_message += f"\n Notification message: {message}"
        selection_message += "\nWhat do you want to do?"

        selection_choices = [
            questionary.Choice(title="Add a file", value="AddFile"),
            questionary.Choice(title="Remove a file", value="RemoveFile"),
            questionary.Choice(title="Change expiration date", value="ChangeExpiration"),
        ]
        if transfer_policy_settings.get("recipientNotificationEditable", False):
            selection_choices.append(questionary.Choice(title="Set custom Notification subject", value="SetSubject"))
            selection_choices.append(questionary.Choice(title="Set custom Notification message", value="SetMessage"))

        selection_choices.append(
            questionary.Choice(
                title=f"Upload {number_of_files} files and send Transfer to {number_of_recipients} recipients",
                value="SendTransfer",
                disabled=can_send_disabled,
                shortcut_key="s",
            )
        )
        selection_choices.append(questionary.Choice(title="Abort", value="AbortTransfer", shortcut_key="q"))

        session_option = questionary.select(
            selection_message,
            choices=selection_choices,
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
            files = ShellCryptshareValidators.clean_string_list(files)
            files_list.extend(files)
            files_list = list(dict.fromkeys(files_list))
        if session_option == "RemoveFile":
            select_remove = True
            while select_remove:
                remove_choices = [questionary.Choice(title=f"{file}", value=file) for file in files_list] + [
                    questionary.Choice(title="Back", value="Back", shortcut_key="b")
                ]
                select_remove_choice = questionary.select(
                    "Which file do you want to remove?", choices=remove_choices, use_shortcuts=True
                ).ask()
                if select_remove_choice == "Back":
                    select_remove = False
                    continue
                try:
                    files_list.remove(select_remove_choice)
                except ValueError:
                    pass
        if session_option == "ChangeExpiration":
            valid_transfer_expiration = False
            while not valid_transfer_expiration:
                transfer_expiration = questionary.text(
                    "When should the transfer expire? (maximum {} days)\n".format(
                        transfer_policy_settings.get("maxRetentionPeriod")
                    ),
                    default=f"{transfer_expiration}",
                    validate=ShellCryptshareValidators.is_valid_expiration,
                ).ask()
                if transfer_expiration == "":
                    transfer_expiration = "2d"
                print(f"Transfer expiration: {transfer_expiration}")
                expiration_date = ShellCryptshareValidators.clean_expiration(transfer_expiration)
                print(transfer_policy_settings)
                if expiration_date <= datetime.now() + timedelta(hours=23, minutes=59):
                    print("Expiration date must be at least 1 day in the future.")
                    continue
                if expiration_date < datetime.now() + timedelta(
                    days=transfer_policy_settings.get("maxRetentionPeriod")
                ):
                    valid_transfer_expiration = True

        if session_option == "SetMessage":
            message = questionary.text(
                "What is the Notification message of the transfer? (blank=default Cryptshare Notification message)\n"
            ).ask()
            notification = CryptshareNotificationMessage(message, subject)
        if session_option == "SetSubject":
            subject = questionary.text(
                "What is the subject of the transfer? (blank=default Cryptshare subject)\n",
                validate=ShellCryptshareValidators.is_valid_transfer_subject,
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
