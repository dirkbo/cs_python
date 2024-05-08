from cryptshare.Transfer import Transfer


def transfer_status(
    origin,
    send_server,
    sender_email,
    transfer_transfer_id,
    cryptshare_client=None,
):
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

    # request verification for sender if not verified already
    if cryptshare_client.is_verified() is True:
        print(f"Sender {sender_email} is verified.")
    else:
        cryptshare_client.request_code()
        verification_code = input(f"Please enter the verification code sent to your email address ({sender_email}):\n")
        cryptshare_client.verify_code(verification_code.strip())
        if cryptshare_client.is_verified() is not True:
            print("Verification failed.")
            return

    transfer = Transfer()
    transfer.set_sender(sender_email)
    transfer.set_location(send_server)
    transfer.get_transfer_status()
