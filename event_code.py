from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("EVENT_BASE_ID"), 'Events Planning', os.getenv("JOHN_AIRTABLE_ID"))


def get_table_data():
    print("Requesting Airtable for data")
    data = airtable.get_all()
    print("Data fetch successful")
    pilots_array = []
    for item in data:
        pilots_array.append(item["fields"])
    return pilots_array


def get_table_unfiltered():
    print("Requesting Airtable for data")
    data = airtable.get_all()
    print("Data fetch successful")
    return data

def get_next_event():
    events = get_table_data()
    response_string = "\n=========================\n"
    event_string = "**Date**:  {}\n**Event**:  {}\n **Leader**:  {}\n**Notes**:  {}\n**Status**:  {}\n=========================\n"
    today_date = datetime.datetime.now()
    for event in events:
        event_date = datetime.datetime.strptime(event["Date"], "%Y-%m-%d")
        if "Event" in event.keys() and event_date > today_date - datetime.timedelta(days=1):
            note = "-"
            status = "-"
            if "notes" in event.keys():
                note = event["notes"]
            if "Status" in event.keys():
                status = event["Status"]
            response_string = response_string + event_string.format(event["Date"], event["Event"], ", ".join(event["Leader"]), note, status)
    return response_string

