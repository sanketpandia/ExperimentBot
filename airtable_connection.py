from airtable import Airtable

import json
import datetime
from dateutil.parser import parse
import math
from dotenv import load_dotenv
import bot_utils as utils

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("BASE_ID"), 'Career Mode Pilots', os.getenv("JOHN_AIRTABLE_ID"))


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
        if ((datetime.datetime.now() - last_active_date).days > 1):
            fun_text = "Its been so long bossman. Checkout your routes with the cm_flightlines command. \n"
        else:
            fun_text = "Always fun when you log flights bossman \n"

        answer_string = "Total CM Hours: {}\nRequired Hours for Next Aircraft: {}\nLast Active on: {}"
        cm_hours = format_time(times["cm_hours"])
        required_hours = format_time(times["required_hours"])
        resultant = fun_text + answer_string.format(cm_hours, required_hours, last_active_date.date())
    return resultant


def get_afklm_pilots():
    airtable_pilot = Airtable(os.getenv("BASE_ID"), 'All Pilots', os.getenv("JOHN_AIRTABLE_ID"))
    data = airtable_pilot.get_all()
    pilots = []
    for item in data:
        if "IFC Name" in item["fields"].keys():
            pilots.append(item["fields"]["IFC Name"])
    return pilots


def file_pirep(pirep):
    airtable_pirep = Airtable(os.getenv("BASE_ID"), 'PIREP Center', os.getenv("JOHN_AIRTABLE_ID"))
    pirep["Route"] = [pirep["Route"]["id"]]
    pirep["Callsign"] = pirep["Callsign"]
    pirep["Date Completed"] = datetime.datetime.now().strftime('%Y-%m-%d')

    airtable_pirep.insert(pirep)


def refresh_pilots():
    airtable_pirep = Airtable(os.getenv("BASE_ID"), 'All Pilots', os.getenv("JOHN_AIRTABLE_ID"))
    routes = airtable_pirep.get_all()
    routes_clean = []
    for route in routes:
        clean_route = {
            "id": route["id"],
            "callsign": route["fields"]["Callsign"]
        }
        routes_clean.append(clean_route)
    with open("./pilot_list.json", "w") as pilot_f:
        json.dump(routes_clean, pilot_f, indent=4)


def refresh_routes():
    airtable_pirep = Airtable(os.getenv("BASE_ID"), 'Routes', os.getenv("JOHN_AIRTABLE_ID"))
    routes = airtable_pirep.get_all()
    routes_clean = []
    for route in routes:
        clean_route = {
            "id": route["id"],
            "route": route["fields"]["Route"]
        }
        routes_clean.append(clean_route)
    with open("./routes_check.json", "w") as routes_f:
        json.dump(routes_clean, routes_f, indent=4)
    with open("./pirep_configs.json", "r") as pirep_f:
        pirep_configs = json.load(pirep_f)
    for key in pirep_configs["Special Routes"].keys():
        route_id = utils.get_route_id(key)
        pirep_configs["Special Routes"][key] = route_id
    with open("./pirep_configs.json", "w") as pirep_f:
        json.dump(pirep_configs, pirep_f, indent=4)


def get_pireps():
    airtable_pirep = Airtable(os.getenv("BASE_ID"), 'PIREP Center', os.getenv("JOHN_AIRTABLE_ID"))
    count = 1
    print("Fetching records")
    data = airtable_pirep.get_all()
    print("records fetched")
    pireps = []
    for value in data:
        if count > 5:
            break
        pireps.append(value["fields"])
        count = count + 1

    with open("./pirep_file_log.json", "w") as pf:
        json.dump(pireps, pf)


# get_pireps()
refresh_pilots()

