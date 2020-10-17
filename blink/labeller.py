from dateutil.parser import parse

INTERACTION_TYPE = ["SENT", "RECEIVED"]
TRACKING_TYPE = ["READ", "LINK"]
CONTENT_TYPE = ["PERSONAL", "BUSINESS"]
TIME_QUADRANT = ["Q1", "Q2", "Q3", "Q4"]

def get_interaction_type(mail_to, participant_email):
    if participant_email in mail_to:
        return INTERACTION_TYPE[1]
    return INTERACTION_TYPE[0]

# TODO: Improve method to decide content type
def get_content_type(mail):
    if "@gmail.com" in mail["from"] or "@gmail.com" in mail["to"]:
        return CONTENT_TYPE[1]
    return CONTENT_TYPE[0]

# TODO: Improve method to decide tracking
def get_tracking_type(mail):
    tracking_types = []
    if "sendgrid" in mail.get("body", "").lower():
        tracking_types.append(TRACKING_TYPE[1])
    if "mailtrack" in mail.get("body", "").lower():
        tracking_type.append(TRACKING_TYPE[0])
    return tracking_types

def get_time_details(timestamp):
    timestamp = parse(timestamp)
    quadrant = timestamp.hour//6
    return quadrant, timestamp.hour, timestamp.minute, timestamp.isoweekday(), timestamp.day, timestamp.month
    
def get_thread_avg_time(threads, thread_len, participant_email):
    for index, thread in enumerate(threads):
        threads[index]["timestamp"] = parse(thread["timestamp"])
    reply_delay_total, reply_number_total = 0,0
    receive_delay_total, receive_number_total = 0,0
    threads.sort(key=lambda x:x["timestamp"])
    for ind, thread in enumerate(threads):
        if ind==0:
            continue
        time_diff = thread['timestamp'] - threads[ind-1]["timestamp"]
        time_diff = abs(time_diff.total_seconds())
        time_diff_in_minutes = divmod(time_diff, 60)[0]
        if participant_email in thread["to"]:
            receive_delay_total += time_diff_in_minutes
            receive_number_total += 1
        else:
            reply_delay_total += time_diff_in_minutes
            reply_number_total += 1
    reply_avg_delay = reply_delay_total/reply_number_total if (reply_number_total) else reply_delay_total
    receive_avg_delay = receive_delay_total/receive_number_total if (receive_number_total) else receive_delay_total
    return reply_avg_delay, receive_avg_delay
    
def label_email(email, participant_email):
    labels = {}
    labels["interaction_type"] = get_interaction_type(email["to"], participant_email)
    labels["tracking_type"] = get_tracking_type(email)
    labels["content_type"] = get_content_type(email)
    labels["time_quadrant"], labels["hour"], labels["minute"], labels["weekday"], labels["date"], labels["month"] = get_time_details(email["timestamp"])
    labels["thread_length"] = len(email["thread"])
    if labels["thread_length"] <= 1:
        labels["thread_avg_reply_delay"], labels["thread_avg_receive_delay"] = 0, 0
    else:
        labels["thread_avg_reply_delay"], labels["thread_avg_receive_delay"] = get_thread_avg_time(email["thread"], labels["thread_length"], participant_email)
    return labels