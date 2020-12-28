from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("FI_BASE_ID"),'Career Mode Type Ratings', os.getenv("JOHN_AIRTABLE_ID"))

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

def get_unassigned():
    pilots_array = get_table_data()
    response_string = ""
    for pilot in pilots_array:
        if "Flight Instructor" in pilot.keys():
            pass
        else:
            response_format = "Callsign : {}\nDiscord name: {}\nRegion:{}\nScheduling Preference: {}\n================\n\n"
            response_string = response_string + response_format.format(pilot["Callsign"], pilot["Discord Display Name"], pilot["Region"], pilot["Scheduling Preference"])
    return response_string


def get_typeratings_by_region(region):
    pilots_array = get_table_data()
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

def get_instructor(instructor, pilots_array):
    instructors = []
    for pilot in pilots_array:
        if ("Flight Instructor" in pilot.keys()) and (pilot["Flight Instructor"] not in instructors) and ("NOT ACTIVE" not in pilot["Flight Instructor"]):
            instructors.append(pilot["Flight Instructor"])
    for person in instructors:
        if instructor.upper() in person():
            return person
    return ""

def get_unique_record_id(callsign, records):
    for record in records:
        pilot = record["fields"]
        if callsign.upper() in pilot["Callsign"].upper() and (("Flight Instructor" not in pilot.keys()) or ("Career Mode Status" not in pilot.keys()) or (pilot["Career Mode Status"] == "Not Started") or (pilot["Career Mode Status"] == "In Progress")):
            return record["id"]
    return ""

def update_instructor(callsign, instructor):
    pilot_data = get_table_unfiltered()
    pilots_array = []
    for item in pilot_data:
        pilots_array.append(item["fields"])
    true_instructor = get_instructor(instructor, pilots_array)
    with open('./cm_typeratings.json', 'w') as jsonf:
        jsonf.write(json.dumps(pilot_data, indent=4))
    if true_instructor == "":
        return ""
    record_id = get_unique_record_id(callsign, pilot_data)
    if record_id == "":
        return "No matching call sign record found"
    fields = {"Flight Instructor": true_instructor}
    try:
        airtable.update(record_id, fields)
        return  str(callsign + " assigned to " + true_instructor)
    except:
        return "Update unsuccessful. Try again or use Airtable"

def update_status(callsign, req_status):
    STATUSES= ["In Progress", "Passed", "Not Started", "Removed - no activity", "Closed - did not pass"]
    true_status = ""
    pilot_data = get_table_unfiltered()
    for status in STATUSES:
        if req_status.upper() in status.upper():
            true_status =  status
            break
    record_id = get_unique_record_id(callsign, pilot_data)
    if true_status == "":
        return ""
    if record_id == "":
        return "No matching call sign record found"
    fields = {"Career Mode Status": true_status}
    try:
        airtable.update(record_id, fields)
        return str(true_status + " assigned to " + callsign)
    except:
        return "Update unsuccessful. Try again or use Airtable"