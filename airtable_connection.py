from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("BASE_ID"),'Career Mode Pilots', os.getenv("JOHN_AIRTABLE_ID"))


def format_time(obj_time):
    min_num = obj_time / 60
    hours = math.floor(min_num / 60)
    min_num = math.floor(min_num % 60)
    flighttime = "";
    if min_num < 10:
        flighttime = str(hours) + ':0' + str(min_num)
    else:
        flighttime = str(hours) + ':' + str(min_num)
    return flighttime


def get_flightlines(callsign):
    routes = []
    data = airtable.get_all()
    pilots_array = []
    for item in data:
        pilots_array.append(item["fields"])
    for item in pilots_array:
        if callsign.upper() in item["Callsign"].upper():
            routes = item["Assigned Routes"]
    answer_string = ""
    for item in routes: answer_string = answer_string + item + "\n"
    return answer_string

def get_time(callsign):
    times = {}
    data = airtable.get_all()
    pilots_array = []
    for item in data:
        pilots_array.append(item["fields"])
    for item in pilots_array:
        if callsign.upper() in item["Callsign"].upper():
            times["cm_hours"] = item["Total CM Hours"]
            times["last_activity"] = item["Last activity in CM"]
            times["required_hours"] = item["Required hours to next aircraft"]
    resultant = ""
    if not (len(times.keys()) < 3):
        last_active_date = (parse(times["last_activity"])).replace(tzinfo=None)
        if((datetime.datetime.now() - last_active_date).days > 1):
            fun_text = "Its been so long bossman. Checkout your routes with the cm_flightlines command. \n"
        else:
            fun_text = "Always fun when you log flights bossman \n"

        answer_string = "Total CM Hours: {}\nRequired Hours for Next Aircraft: {}\nLast Active on: {}"
        cm_hours = format_time(times["cm_hours"])
        required_hours = format_time(times["required_hours"])
        resultant = fun_text + answer_string.format(cm_hours, required_hours, last_active_date.date())
    return resultant

