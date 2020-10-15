def get_participant_email(service):
    user_details = service.users().getProfile(userId='me').execute()
    return user_details.get("emailAddress", None)

def read_emails(service, fro, to):
    emails = service.users().messages().list(userId="me",
                                      q = "after:" + fro.strftime("%Y/%m/%d") + " before:" + to.strftime("%Y/%m/%d"),
                                      maxResults = 1000
                                    ).execute()
    print(emails)

def get_sample_each_type(label_list, num_samples):
    pass