from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("FI_BASE_ID"),'Career Mode Type Ratings', os.getenv("JOHN_AIRTABLE_ID"))
jsonPath = './cm_typeratings.json'
def get_unassigned():
    data = airtable.get_all()
    pilots_array = []
    for item in data:
        pilots_array.append(item["fields"])
    response_string = ""
    for pilot in pilots_array:
        if "Flight Instructor" in pilot.keys():
            pass
        else:
            response_format = "Callsign : {}\nDiscord name: {}\nRegion:{}\nScheduling Preference: {}\n================\n\n"
            response_string = response_string + response_format.format(pilot["Callsign"], pilot["Discord Display Name"], pilot["Region"], pilot["Scheduling Preference"])
    return response_string


def get_typeratings_by_region(region):
    data = airtable.get_all()
    pilots_array = []
    for item in data:
        pilots_array.append(item["fields"])
    response_string = ""
    for pilot in pilots_array:
        if ("Flight Instructor" in pilot.keys()) and (region.upper() in pilot["Flight Instructor"].upper()) and (not ("Career Mode Status" in pilot.keys()) or (pilot["Career Mode Status"] == "In Progress") or (pilot["Career Mode Status"] == "Not Started")):
            if "Scheduling Preference" in pilot.keys():
                scheduling = pilot["Scheduling Preference"]
            else:
                scheduling = "-"
            if "Career Mode Status" in pilot.keys():
                status = pilot["Career Mode Status"]
            else:
                status = "-"
            response_format = "Callsign : {}\nDiscord name: {}\nRegion:{}\nScheduling Preference: {}\nFlight Instrucor: {}\nStatus: {}\n================\n\n"
            response_string = response_string + response_format.format(pilot["Callsign"], pilot["Discord Display Name"], pilot["Region"], scheduling,pilot["Flight Instructor"], status)
    return response_string
