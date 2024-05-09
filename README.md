# Prerequisites
- A running cryptshare server with licensed REST-API is required.
- python 3.11

# Getting started
Create virtual env 

`python -m venv .venv`

Change to virtualenv

`source .venv/bin/activate` 

Install requirements

`pip install -r requirements.txt`

## Development
Install also development requirements

`pip install -r dev_requirements.txt`

# Configuration

## Environment variables

### CRYPTSHARE_SERVER
Default value is "https://beta.cryptshare.com". The default Cryptshare Server that is beeing used.

### CRYPTSHARE_SENDER_EMAIL
Default value is None. When configured, the email will be used as default sender email for sending transfers.

### CRYPTSHARE_SENDER_NAME
Default Value is "REST-API Sender". When configured, the name will be used as default sender name for sending transfers.

### CRYPTSHARE_SENDER_PHONE"
Default Value is "0". When configured, the phone number will be used as default sender phone for sending transfers.

### CRYPTSHARE_CORS_ORIGIN"
Default Value is "https://localhost". When configured, the origin will be used as default CORS origin.

### TWILIO_ACCOUNT_SID 
Optional, Passwords can't be sent by sms if not configured.

Twilio Account access for sending password by SMS. 

### TWILIO_AUTH_TOKEN
Optional, Passwords can't be sent by sms if not configured.

Twilio Account access for sending password by SMS. 

### TWILIO_SENDER_PHONE
Optional, Passwords can't be sent by sms if not configured.

Phone Number to send password sms from.  


# Examples

## Shell examples

### Run shell examples
install additional requirements

`pip install -r examples/shell_example/requirements.txt`

### send files from commandline
`python examples/shell_example/example.py -m send -e test@example.com -f example_files/test_file.txt -f example_files/file-example_PDF_1MB.pdf --bcc test1@example.com --bcc 'test2@example.com' -p 'test!Test1'`

### send files from commandline, send generated password to recipients by sms (if twilio is configured)
`python examples/shell_example/example.py -m send -e test@example.com -f example_files/test_file.txt -f example_files/file-example_PDF_1MB.pdf --bcc test1@example.com --bcc 'test2@example.com' --sms_recipient +49123456789 --sms_recipient +4112345678`

### receive transfer from commandline
`python examples/shell_example/example.py -m receive -t 5xVluOW7NR -p 'test!Test1'`

### start interactive transfer from commandline
`python examples/shell_example/example.py`

## GUI examples
Requires PySimpleGUI

### Run GUI example
install additional requirements

`pip install -r examples/gui_example/requirements.txt`

Run GUI example

`python examples/gui_example/gui.py`

# Disclaimer
This project is in no way affiliated with Pointsharp and completely based on publicly available [documentation](http://documentation.cryptshare.com). 

Pointsharp Support can and will not provide any support for this project.