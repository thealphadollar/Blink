from dateutil.parser import parse
import json
import re
import os
import sys

INTERACTION_TYPE = ["SENT", "RECEIVED"]
TRACKING_TYPE = ["OPEN", "CLICK"]
TIME_QUADRANT = ["1", "2", "3", "4"]
CONTENT_TYPE = ["CATEGORY_PERSONAL", "CATEGORY_UPDATES",
                "CATEGORY_PROMOTIONS", "CATEGORY_FORUMS", "CATEGORY_SOCIAL"]
WEEKDAY_NUM_TO_STRING = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday"
}

# make work with frozen data from pyinstaller
if getattr(sys, 'frozen', False):
    TRACKER_LIST_JSON_PATH = os.path.join(sys._MEIPASS, "trackerList.json")
else:
    TRACKER_LIST_JSON_PATH = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "trackerList.json")
TRACKER_LIST = None

with open(TRACKER_LIST_JSON_PATH) as f:
    TRACKER_LIST = json.load(f)


def get_interaction_type(mail_to, participant_email):
    if participant_email in mail_to:
        return INTERACTION_TYPE[1]
    return INTERACTION_TYPE[0]


def get_content_type(mail):
    if INTERACTION_TYPE[0] in mail["labels"]:
        return CONTENT_TYPE[0]
    else:
        for label in mail["labels"]:
            if label in CONTENT_TYPE:
                return label
    return CONTENT_TYPE[0]


def get_tracking_type(mail):
    tracking_types = []
    lowercase_body = mail.get("body", "").lower()
    for tracking_type in TRACKING_TYPE:
        cur_type_tracker_found = False
        for tracker in TRACKER_LIST[tracking_type]:
            for domain in tracker["domains"]:
                if domain in lowercase_body:
                    tracking_types.append(tracking_type)
                    cur_type_tracker_found = True
                    break
            else:
                for pattern in tracker["patterns"]:
                    if len(re.findall(pattern, lowercase_body)) > 0:
                        tracking_types.append(tracking_type)
                        cur_type_tracker_found = True
                        break
            if cur_type_tracker_found:
                break
    if len(tracking_types) == 0:
        return False, False
    if len(tracking_types) == 2:
        return True, True
    if TRACKING_TYPE[0] in tracking_types:
        return True, False
    else:
        return False, True


def get_time_details(timestamp):
    timestamp = parse(timestamp)
    quadrant = timestamp.hour//6
    return (quadrant + 1), timestamp.hour, timestamp.minute, WEEKDAY_NUM_TO_STRING.get(timestamp.isoweekday()), timestamp.day, timestamp.month


def get_thread_avg_time(threads, thread_len, participant_email):
    for index, thread in enumerate(threads):
        threads[index]["timestamp"] = parse(thread["timestamp"])
    reply_delay_total, reply_number_total = 0, 0
    receive_delay_total, receive_number_total = 0, 0
    threads.sort(key=lambda x: x["timestamp"])
    for ind, thread in enumerate(threads):
        if ind == 0:
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
    reply_avg_delay = reply_delay_total / \
        reply_number_total if (reply_number_total) else reply_delay_total
    receive_avg_delay = receive_delay_total / \
        receive_number_total if (receive_number_total) else receive_delay_total
    return reply_avg_delay, receive_avg_delay


def label_email(email, participant_email):
    labels = {}
    labels["id"] = email["id"]
    labels["interaction_type"] = get_interaction_type(
        email.get("to", "##"), participant_email)
    labels["has_open_tracking"], labels["has_click_tracking"] = get_tracking_type(
        email)
    labels["content_type"] = get_content_type(email).replace("CATEGORY_", "")
    labels["time_quadrant"], labels["hour"], labels["minute"], labels["weekday"], labels["date"], labels["month"] = get_time_details(
        email["timestamp"])
    labels["thread_length"] = len(email["thread"])
    if labels["thread_length"] <= 1:
        labels["thread_avg_reply_delay"], labels["thread_avg_receive_delay"] = 0, 0
    else:
        labels["thread_avg_reply_delay"], labels["thread_avg_receive_delay"] = get_thread_avg_time(
            email["thread"], labels["thread_length"], participant_email)
    return labels
