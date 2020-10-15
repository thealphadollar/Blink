import hashlib


def generate_data_for_mothership(email, label_list):
    identifier = hashlib.md5(email).hexdigest()
    to_send = {}
    to_send["identifier"] = identifier
    to_send["data"] = label_list
    return identifier, to_send

def send_to_mothership(data):
    pass