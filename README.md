# Getting started

Create virtual env 
`python -m venv .venv`

Change to virtualenv
`source .venv/bin/activate` 

Install requirements
`pip install -r requirements.txt`

## Run shell examples
install extra requirements
`pip install -r examples/shell_example/extra_requirements.txt`

Run shell example in interactive mode
`python examples/shell_example/example.py`

## Run GUI example
install extra requirements
`pip install -r examples/gui_example/extra_requirements.txt`

Run GUI example
`python examples/gui_example/gui.py`

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

# Examples

## send files from commandline

`python example.py -m send -e test@example.com -f example_files/test_file.txt -f example_files/file-example_PDF_1MB.pdf --bcc test1@example.com --bcc 'test2@example.com' -p 'test!Test1'`

## receive transfer from commandline

`python example.py -m receive -t 5xVluOW7NR -p 'test!Test1'`
