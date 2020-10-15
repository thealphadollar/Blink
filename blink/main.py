import json
import os
from datetime import datetime

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from blink.collector import (get_participant_email, get_sample_each_type,
                             read_emails)
from blink.labeller import label_email
from blink.sender import generate_data_for_mothership, send_to_mothership

AUTH_CREDS = os.path.join(os.path.expanduser('~'), ".blinkcreds")
APP_CREDS = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), ".client_secrets")
OUTPUT_PATH_JSON = os.path.join(
    os.path.expanduser('~'), "email_tracking_analysis.json")
SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
FROM = "01/10/20"   # in DD/MM/YY, inclusive
TO = "31/10/20"     # in DD/MM/YY, inclusive
NUM_SAMPLES_TO_COLLECT = 1
SURVEY_LINK = "https://example.com"


def auth():
    """
    authorises the application using saved credentials
    :return: service: authenticated and built gmail API service client
    """
    store = file.Storage(AUTH_CREDS)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(APP_CREDS, SCOPES)
        creds = tools.run_flow(flow, store)
    gmail_service = build('gmail', 'v1', http=creds.authorize(Http()))
    return gmail_service


# def get_draft_list(service):
#     """
#     prints the list of drafts present in user's draft box

#     :param service: authenticated and built gmail API service client
#     :return: list containing iD and subject of drafts
#     """
#     draft_list = service.users().drafts().list(userId='me').execute()
#     beautiful_draft_list = []

#     for draft in draft_list.get("drafts", []):
#         # print(draft)
#         draft_body = service.users().drafts().get(userId='me', id=draft["id"], format="metadata").execute()
#         # print(draft_body)
#         beautiful_draft_list.append([
#             draft["id"],
#             draft_body["message"]["snippet"]
#         ])
#     return beautiful_draft_list


# def make_copies(service, draft_id, n):
#     """
#     make copies of the draft
#     :param service: authenticated gmail service
#     :param draft_id: GMail draft ID
#     :param n: number of copies
#     :return: True if successful, False otherwise
#     """
#     draft_response = service.users().drafts().get(userId="me", id=draft_id, format="raw").execute()
#     raw_response = {'raw': draft_response["message"]["raw"]}
#     message = {'message': raw_response}
#     try:
#         for x in range(int(n)):
#             draft = service.users().drafts().create(userId="me", body=message).execute()
#             print("draft number "+str(x+1)+" created")
#         return True
#     except Exception as err:
#         print(err)
#         return False


if __name__ == "__main__":
    gm_serv = auth()
    print("INFO: Reading emails from " + str(FROM) + " to " + str(TO))
    FROM = datetime.strptime(FROM, "%d/%m/%y")
    TO = datetime.strptime(FROM, "%d/%m/%y")
    participant_email = get_participant_email(gm_serv)
    mail_list = read_emails(gm_serv, FROM, TO)
    print("INFO: fetched " + len(mail_list) + " emails!")
    print("INFO: analysing mails and associating labels...")
    label_list = []
    for mail in mail_list:
        label_list.append(label_email(mail))
    tracked, non_tracked = get_sample_each_type(
        label_list, NUM_SAMPLES_TO_COLLECT)
    identifier, json_to_send = generate_data_for_mothership(
        participant_email, label_list)
    with open(OUTPUT_PATH_JSON) as f:
        json.dump(json_to_send, f, indent=4)
    consent = input("Do you want to proceed to send data stored in " + OUTPUT_PATH_JSON +
                    " for research purpose as stated in consent and recruitment form? (Y/n) ")
    if consent != "" and consent != "Y":
        print("Please let us know the issue with sending data by reaching us at shivam.cs.iit.kgp@gmail.com")
        exit(1)
    send_to_mothership(json_to_send)
    print("We have received your data, please fill the survey at " +
          SURVEY_LINK + " Use the following information in the survey:")
    print("Identifier: " + identifier)
    for index, sample in enumerate(zip(tracked, non_tracked)):
        print("EMAIL_SAMPLE_A" + (index+1) + ": " + sample[0])
        print("EMAIL_SAMPLE_B" + (index+1) + ": " + sample[1])
