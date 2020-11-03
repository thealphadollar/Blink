import json
import os
from datetime import datetime
import sys

from collector import get_participant_email, get_sample_each_type, read_emails
from googleapiclient.discovery import build
from httplib2 import Http
from labeller import label_email
from oauth2client import client, file, tools
from sender import generate_data_for_mothership, send_to_mothership

AUTH_CREDS = os.path.join(os.path.expanduser('~'), ".blinkcreds")

# make work with frozen data from pyinstaller
if getattr(sys, 'frozen', False):
    APP_CREDS = os.path.join(sys._MEIPASS, ".client_secrets")
else:
    APP_CREDS = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), ".client_secrets")

OUTPUT_PATH_CSV = os.path.join(
    os.path.expanduser('~'), "email_tracking_analysis.csv")
SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
FROM = "01/10/20"   # in DD/MM/YY, inclusive
TO = "31/10/20"     # in DD/MM/YY, inclusive
NUM_SAMPLES_TO_COLLECT = 1
SURVEY_LINK = "https://shivamcsiitkgp.typeform.com/to/RvRdbgcZ"


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


if __name__ == "__main__":
    gm_serv = auth()
    participant_email = get_participant_email(gm_serv)
    if participant_email is not None:
        confirmation = input("Your email ID is " +
                             participant_email + ". Is that correct? (Y/n) ")
        if confirmation != "" and confirmation.lower() != "y":
            participant_email = None
    if participant_email is None:
        participant_email = input(
            "Please enter your email ID (will not be sent to researches, used only for generating identifier): ")
    FROM = datetime.strptime(FROM, "%d/%m/%y")
    TO = datetime.strptime(TO, "%d/%m/%y")
    TO = TO.replace(hour=23, minute=59, second=59)
    print("INFO: Reading emails from " + str(FROM) + " to " + str(TO) +
          ", please fill the survey at " + SURVEY_LINK + " as this may take a few minutes!")
    mail_list = read_emails(gm_serv, FROM, TO)
    print("INFO: fetched " + str(len(mail_list)) + " emails!")
    print("INFO: analysing mails and associating labels...")
    label_list = []
    for mail in mail_list:
        if mail.get("body") is None:
            continue
        try:
            label_list.append(label_email(mail, participant_email))
        except:
            continue
    tracked, non_tracked = get_sample_each_type(
        label_list, NUM_SAMPLES_TO_COLLECT, participant_email)
    identifier, csv_to_send = generate_data_for_mothership(
        participant_email, label_list)
    with open(OUTPUT_PATH_CSV, 'w+') as f:
        f.write(csv_to_send)
    consent = input("Do you want to proceed to send data stored in " + OUTPUT_PATH_CSV +
                    " for research purpose as stated in consent and recruitment form? (Y/n) ")
    if consent != "" and consent.lower() != "y":
        print("Please let us know the issue with sending data by reaching us at shivam.cs.iit.kgp@gmail.com")
        exit(1)
    send_to_mothership(csv_to_send)
    print("We have received your data, use the following information in the survey: ")
    print("Identifier: " + identifier)
    for index, sample in enumerate(zip(tracked, non_tracked)):
        print("EMAIL_SAMPLE_A" + str(index+1) + ": " + sample[0])
        print("EMAIL_SAMPLE_B" + str(index+1) + ": " + sample[1])
