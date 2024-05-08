import os
import requests
from tqdm import tqdm
from cryptshare.Client import Client as CryptshareClient


def receive_transfer(origin, dl_server, recipient_transfer_id, password, save_path):
    cryptshare_client = CryptshareClient(dl_server)
    #  Reads existing verifications from the 'store' file if any
    cryptshare_client.read_client_store()

    #  request client id from server if no client id exists
    #  Both branches also react on the REST API not licensed
    if cryptshare_client.exists_client_id() is False:
        cryptshare_client.request_client_id()
    else:
        # Check CORS state for a specific origin.
        cryptshare_client.cors(origin)

    download = cryptshare_client.download(recipient_transfer_id, password)
    files_info = download.download_files_info()
    directory = os.path.join("transfers", save_path)
    print(f"Downloading Transfer {recipient_transfer_id} from {dl_server} to {directory}...")
    for file in files_info:
        response = requests.get(dl_server + file["href"], stream=True)
        full_path = os.path.join(directory, file["fileName"])
        if not os.path.exists(directory):
            os.makedirs(directory)
        print(f"Downloading {file['fileName']} to {full_path}")
        with open(full_path, "wb") as handle:
            for data in tqdm(
                response.iter_content(),
                desc=file["fileName"],
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                total=int(file["size"]),
            ):
                handle.write(data)

    print(f"Downloaded Transfer {recipient_transfer_id} to {directory} complete.")
