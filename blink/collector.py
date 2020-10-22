import base64
from random import sample

SAMPLE_MAIL_URL_STR = "https://mail.google.com/mail?authuser=EMAILADDRESS#all/MESSAGEID"


def _get_from_base64(base64_message):
    return base64.urlsafe_b64decode(base64_message)


def get_participant_email(service):
    user_details = service.users().getProfile(userId='me').execute()
    return user_details.get("emailAddress", None)


def read_emails(service, fro, to):
    email_list = []
    emails = service.users().messages().list(userId="me",
                                             q="after:" +
                                             fro.strftime(
                                                 "%Y/%m/%d") + " before:" + to.strftime("%Y/%m/%d"),
                                             maxResults=1000
                                             ).execute()
    for email in emails["messages"]:
        email_dict = {}
        email_dict["id"] = email["id"]
        email_info = service.users().messages().get(
            userId="me", id=email["id"]).execute()
        email_dict["labels"] = email_info["labelIds"]
        for header in email_info["payload"]["headers"]:
            if header["name"] == "To":
                email_dict["to"] = header["value"]
            elif header["name"] == "Date":
                email_dict["timestamp"] = header["value"]
            elif header["name"] == "From":
                email_dict["from"] = header["value"]
            elif header["name"] == "Subject":
                email_dict["subject"] = header["value"]
        if email_info["payload"]["body"].get("data"):
            email_dict["body"] = str(_get_from_base64(
                email_info["payload"]["body"]["data"]))
        elif len(email_info["payload"]["parts"]) > 0:
            for part in email_info["payload"]["parts"]:
                if part["mimeType"] == "text/plain" or part["mimeType"] == "text/html":
                    email_dict["body"] = str(
                        _get_from_base64(part["body"]["data"]))
        else:
            email_dict["body"] = None

        # thread information
        thread_info = service.users().threads().get(
            userId="me", id=email["threadId"]).execute()
        email_dict["thread"] = []
        for message in thread_info["messages"]:
            minimal_cur_thread_info = {}
            for header in message["payload"]["headers"]:
                if header["name"] == "To":
                    minimal_cur_thread_info["to"] = header["value"]
                elif header["name"] == "Date":
                    minimal_cur_thread_info["timestamp"] = header["value"]
                elif header["name"] == "From":
                    minimal_cur_thread_info["from"] = header["value"]
            email_dict["thread"].append(minimal_cur_thread_info)
        email_list.append(email_dict)
    return email_list


def get_sample_each_type(label_list, num_samples, participant_email):
    sample_mail_url = SAMPLE_MAIL_URL_STR.replace(
        "EMAILADDRESS", participant_email)
    all_tracking = set([x for x in range(len(label_list))])
    with_tracking = set()
    for ind in range(len(label_list)):
        if len(label_list[ind]["tracking_type"]):
            with_tracking.add(ind)
    without_tracking = all_tracking - with_tracking
    tracked = []
    non_tracked = []
    try:
        tracked = sample(with_tracking, num_samples)
        non_tracked = sample(without_tracking, num_samples)
    except ValueError:
        pass
    tracked = [sample_mail_url.replace(
        "MESSAGEID", label_list[x]["id"]) for x in tracked]
    non_tracked = [sample_mail_url.replace(
        "MESSAGEID", label_list[x]["id"]) for x in non_tracked]
    return tracked, non_tracked
