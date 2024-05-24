import datetime
import inspect
import os
import sys

import PySimpleGUI as sg
from dateutil import parser as date_parser

# To work from exapmples folder, parentfolder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, parentdir)

import cryptshare.CryptshareClient as CryptshareClient
import cryptshare.CryptshareNotificationMessage as NotificationMessage
import cryptshare.CryptshareTransferSettings as Settings
from cryptshare.CryptshareTransferSecurityMode import CryptshareTransferSecurityMode

# Please change these parameters accordingly to your setup
cryptshare_server_url = os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com")
transfer_password = "Thunderstruck!"
origin = os.getenv("CRYPTSHARE_CORS_ORIGIN", "https://localhost")


def ui(cryptshare_client: CryptshareClient):
    #  reads all email addresses from client store
    senders = cryptshare_client.get_emails()
    to_recipients = []
    cc_recipients = []
    bcc_recipients = []
    file_list = []
    expiration_date = ""

    s_lst = sg.Listbox(
        senders,
        size=(20, 4),
        font=("Arial Bold", 14),
        expand_y=True,
        enable_events=True,
        key="-Sender-",
    )
    to_r_lst = sg.Listbox(
        to_recipients,
        size=(20, 4),
        font=("Arial Bold", 14),
        expand_y=True,
        enable_events=True,
        select_mode="multiple",
        key="-To Recipient-",
    )
    cc_r_lst = sg.Listbox(
        cc_recipients,
        size=(20, 4),
        font=("Arial Bold", 14),
        expand_y=True,
        enable_events=True,
        select_mode="multiple",
        key="-CC Recipient-",
    )
    bcc_r_lst = sg.Listbox(
        bcc_recipients,
        size=(20, 4),
        font=("Arial Bold", 14),
        expand_y=True,
        enable_events=True,
        select_mode="multiple",
        key="-BCC Recipient-",
    )
    layout1 = [
        [
            sg.Input(size=(50, 1), font=("Arial Bold", 14), expand_x=True, key="-INPUT-"),
            sg.Button("Add Sender"),
            sg.Button("Remove"),
            sg.Button("Exit"),
        ],
        [sg.Text("Sender", font=("Arial Bold", 14), justification="left"), s_lst],
        [sg.Button("Next")],
    ]
    layout2 = [
        [
            sg.Input(size=(20, 1), font=("Arial Bold", 14), expand_x=True, key="-INPUT-"),
            sg.Button("Add To Recipient"),
            sg.Button("Add CC Recipient"),
            sg.Button("Add BCC Recipient"),
            sg.Button("Remove"),
            sg.Button("Exit"),
        ],
        [
            sg.Text("    To Recipients", font=("Arial Bold", 14), justification="right"),
            to_r_lst,
            sg.Text("CC Recipients", font=("Arial Bold", 14), justification="left"),
            cc_r_lst,
        ],
        [
            sg.Text("BCC Recipients", font=("Arial Bold", 14), justification="right"),
            bcc_r_lst,
        ],
        [sg.Button("Next")],
    ]
    layout3 = [
        [
            sg.Listbox(file_list, key="files", size=(80, 4)),
            sg.FilesBrowse(key="file", enable_events=True, change_submits=True, target="file"),
        ],
        [sg.Button("Next")],
    ]
    layout4 = [
        [
            sg.Text(expiration_date, key="-Selected Date-"),
            sg.CalendarButton(
                button_text="Expiration Date",
                key="date",
                enable_events=True,
                target="date",
            ),
        ],
        [sg.Button("Next")],
    ]
    window = sg.Window("Cryptshare Sender Selection", layout1)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            return
        if event == "Add Sender":
            senders.append(values["-INPUT-"])
            window["-Sender-"].update(senders)
        if event == "Remove":
            if s_lst.get():
                vallist = s_lst.get()
                for val in vallist:
                    senders.remove(val)
            window["-Sender-"].update(senders)
        if event == "Next":
            if s_lst.get():
                sender_email = s_lst.get()[0]
            else:
                continue
            window.close()
            break
    window = sg.Window("Cryptshare Recipient Selection", layout2)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            return
        if event == "Add To Recipient":
            to_recipients.append(values["-INPUT-"])
            to_recipients = remove_duplicates(to_recipients)
            window["-To Recipient-"].update(to_recipients)
        if event == "Add CC Recipient":
            cc_recipients.append(values["-INPUT-"])
            cc_recipients = remove_duplicates(cc_recipients)
            window["-CC Recipient-"].update(cc_recipients)
        if event == "Add BCC Recipient":
            bcc_recipients.append(values["-INPUT-"])
            bcc_recipients = remove_duplicates(bcc_recipients)
            window["-BCC Recipient-"].update(bcc_recipients)
        if event == "Remove":
            if to_r_lst.get():
                vallist = to_r_lst.get()
                for val in vallist:
                    to_recipients.remove(val)
            if cc_r_lst.get():
                vallist = cc_r_lst.get()
                for val in vallist:
                    cc_recipients.remove(val)
            if bcc_r_lst.get():
                vallist = bcc_r_lst.get()
                for val in vallist:
                    bcc_recipients.remove(val)
            window["-To Recipient-"].update(to_recipients)
            window["-CC Recipient-"].update(cc_recipients)
            window["-BCC Recipient-"].update(bcc_recipients)
        if event == "Next":
            window.close()
            break
    window = sg.Window("Cryptshare File Selection", layout3)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            return
        if event == "Next":
            window.close()
            break
        if event == "file":
            file_list.extend(values.get("file").split(";"))
            file_list = remove_duplicates(file_list)
            window["files"].update(file_list)
    window = sg.Window("Cryptshare Date Selection", layout4)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            return
        if event == "Next":
            window.close()
            break
        if event == "date":
            expiration_date = datetime.datetime.strptime(values.get("date"), "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            window["-Selected Date-"].update(expiration_date)
    return (
        sender_email,
        to_recipients,
        cc_recipients,
        bcc_recipients,
        file_list,
        expiration_date,
    )


def recipient_transformation(recipients) -> list:
    return_list = []
    for recipient in recipients:
        return_list.append({"mail": recipient})
    return return_list


def remove_duplicates(input_list) -> list:
    r = []
    for e in input_list:
        if e not in r:
            r.append(e)
    return r


def display_transfer_information(transfer_settings):
    layout = [
        [sg.Multiline(transfer_settings, size=(45, 5))],
        [sg.Button("Send"), sg.Button("Cancel")],
    ]
    window = sg.Window("Cryptshare Transfer Information", layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            return False
        if event == "Send":
            return True


def main():
    #  Set server URL
    cryptshare_client = CryptshareClient(server=cryptshare_server_url, ssl_verify=False)

    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    #  determine transfer settings by UI
    (
        sender_address,
        to_recipient,
        cc_recipient,
        bcc_recipient,
        files,
        expiration_date,
    ) = ui(cryptshare_client)
    #  determine sender
    cryptshare_client.set_sender(sender_address, "REST by Python", "+4976138913100")
    # request verification for sender if not verified already
    if cryptshare_client.is_verified() is False:
        cryptshare_client.request_code()
        cryptshare_client.verify_code(sg.popup_get_text("code").strip())
        cryptshare_client.is_verified()
    #  Example code for API functionality
    # password_rules = cryptshare_client.get_password_rules()
    # password_response = cryptshare_client.get_password()
    # passwort_validated_response = cryptshare_client.validate_password("happyday123asd")
    # policy_response = cryptshare_client.get_policy(["python@domain.com"])
    #  Transfer definition
    expiration_date = date_parser.parse(expiration_date)
    sender = cryptshare_client.sender
    message = NotificationMessage.CryptshareNotificationMessage("test", "Test the REST")
    settings = Settings.CryptshareTransferSettings(
        sender,
        expiration_date,
        message,
        send_download_notifications=True,
        security_mode=CryptshareTransferSecurityMode(password=transfer_password),
        senderLanguage=sender.language,
        recipientLanguage=message.language,
    )

    #  Start of transfer on server side
    transfer = cryptshare_client.start_transfer(
        {
            "bcc": recipient_transformation(bcc_recipient),
            "cc": recipient_transformation(cc_recipient),
            "to": recipient_transformation(to_recipient),
        },
        settings,
    )
    for file in files:
        transfer.upload_file(file)
    pre_transfer_info = transfer.get_transfer_settings()
    if display_transfer_information(transfer.get_transfer_settings()):
        transfer.send_transfer()
    post_transfer_info = transfer.get_transfer_status()
    cryptshare_client.write_client_store()

    print(pre_transfer_info)
    print(post_transfer_info)


main()
