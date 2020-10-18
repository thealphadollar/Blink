import hashlib
import http.client

import pandas as pd

MOTHERSHIP_URL = 'enixcflc7e828.x.pipedream.net'


def generate_data_for_mothership(email, label_list):
    identifier = hashlib.md5(email.encode('utf-8')).hexdigest()
    to_send = {}
    for label in label_list:
        del label["id"]
        label["identifier"] = identifier
    csv_data = pd.DataFrame(label_list).to_csv(index=False, header=True)
    return identifier, csv_data


def send_to_mothership(data):
    conn = http.client.HTTPSConnection(MOTHERSHIP_URL)
    conn.request("POST", "/", data, {'Content-Type': 'text/csv'})
