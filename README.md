# Prerequisites
- A running cryptshare server with licensed REST-API is required.
- Cryptshare REST-API 1.9 (with Server v7.0.0)
- python 3.10

# Getting started
Create virtual env 

`python -m venv .venv`

Change to virtualenv

`source .venv/bin/activate` 

Install requirements

`pip install dist/cryptshare-0.1.0-py3-none-any.whl`

## Development
Install also development requirements

`pip install -r dev_requirements.txt`

### Understanging the Cryptshare API
The Cryptshare API is documented in the [Cryptshare REST-API documentation](http://documentation.cryptshare.com).

If you want to see what API Calls are used to perform a specific actions, set the log level for `"cryptshare.CryptshareApiRequestHandler"` to `INFO` or `DEBUG`.

# Configuration

## Environment variables 
The following environment variables (also .env file) can be used to configure the client.

### CRYPTSHARE_SERVER
Default value is "http://localhost". The default Cryptshare Server that is beeing used.

### CRYPTSHARE_SENDER_EMAIL
Default value is None. When configured, the email will be used as default sender email for sending transfers.

### CRYPTSHARE_SENDER_NAME
Default Value is "REST-API Sender". When configured, the name will be used as default sender name for sending transfers.

### CRYPTSHARE_SENDER_PHONE"
Default Value is "0". When configured, the phone number will be used as default sender phone for sending transfers.

### CRYPTSHARE_CORS_ORIGIN"
Default Value is "https://localhost". When configured, the origin will be used as default CORS origin.

## Extra Environment variables
Only required for sending Password SMS using twilio with the `--sms_recipient` option of the shell example.

### TWILIO_ACCOUNT_SID 
Optional, Passwords can't be sent by sms if not configured.

Twilio Account access for sending password by SMS. 

### TWILIO_AUTH_TOKEN
Optional, Passwords can't be sent by sms if not configured.

Twilio Account access for sending password by SMS. 

### TWILIO_SENDER_PHONE
Optional, Passwords can't be sent by sms if not configured.

Phone Number to send password sms from. Twilio trial accounts can only send SMS from and to verified numbers. 


# Examples

## Shell examples

### Run shell examples
`cd examles/shell_example`

Install additional requirements

`pip install -r requirements.txt`

### send files from commandline

`python example.py -m send -e test@example.com -f example_files/test_file.txt -f example_files/file-example_PDF_1MB.pdf --bcc test1@example.com --bcc 'test2@example.com' -p 'test!Test1'`

### send files from commandline, send generated password to recipients by sms (if twilio is configured)
`python example.py -m send -e test@example.com -f example_files/test_file.txt -f example_files/file-example_PDF_1MB.pdf --bcc test1@example.com --bcc 'test2@example.com' --sms_recipient +49123456789 --sms_recipient +4112345678`

### receive transfer from commandline

#### Download all files to transfers/transfer_id/
`python example.py -m receive -transfer_id 5yVluOW8NR -p 'test!Test1'`

#### Download a .zip file containing all files to transfers/transfer_id/
`python example.py -m receive -transfer_id 5yVluOW8NR -p 'test!Test1' --zip`

#### Download a .eml file containing all files to transfers/transfer_id/
Only works, when the transfer contains a confidential message.

`python example.py -m receive -transfer_id 5yVluOW8NR -p 'test!Test1' --eml`

### check status of send transfers from commandline
#### All send transfers
`python example.py -m status '`

#### A specific sent transfer
`python example.py -m status -tracking_id 20240524-192513-3n2yqVIW`

### start interactive transfer from commandline
`python example.py`

`python example.py -m interactive`

## GUI examples
Requires PySimpleGUI

### Run GUI example

`cd examles/shell_example`

Install additional requirements

`pip install -r requirements.txt`

Run GUI example

`python gui_example/gui.py`

# Disclaimer
This project is in no way affiliated with Pointsharp and completely based on publicly available [documentation](http://documentation.cryptshare.com). 

Pointsharp Support can and will not provide any support for this project.
