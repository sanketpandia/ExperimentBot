from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

airtable = Airtable(os.getenv("FI_BASE_ID"),'Pilot Academy', os.getenv("JOHN_AIRTABLE_ID"))

CFs = ["CF1 Grade", "CF2 Grade", "CF3 Grade"]
CF_STATUSES = ["PASS", "FAIL", "RETRY", "NO SHOW"]
STATUSES= ["In Progress", "Closed - Graduated", "Contact to Schedule CF1", "Closed - Did Not Complete", "Removed - Inactivity"]

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
        if ("Flight Instructor" in pilot.keys()) and (region.upper() in pilot["Flight Instructor"].upper()) and (not ("Status" in pilot.keys()) or (pilot["Status"] == "In Progress") or (pilot["Status"] == "Not Started") or (pilot["Status"] == "Contact to Schedule CF1")):
            print(pilot)
            if "Scheduling Preference" in pilot.keys():
                scheduling = pilot["Scheduling Preference"]
            else:
                scheduling = "-"
            if "Status" in pilot.keys():
                status = pilot["Status"]
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
        if instructor.upper() in person.upper():
            return person
    return ""

def get_unique_record_id(callsign, records):
    for record in records:
        pilot = record["fields"]
        if ("Callsign" in pilot.keys() and callsign.upper() in pilot["Callsign"].upper()) and (("Flight Instructor" not in pilot.keys()) or ("Status" not in pilot.keys()) or (pilot["Status"] == "Contact to Schedule CF1") or (pilot["Status"] == "In Progress")):
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
    fields = {"Status": true_status}
    try:
        print(true_status)
        airtable.update(record_id, fields)
        return str(true_status + " assigned to " + callsign)
    except:
        return "Update unsuccessful. Try again or use Airtable"

def update_cf(callsign, CF, cf_status):

    true_status = ""
    pilot_data = get_table_unfiltered()
    for status in CFs:
        if CF.upper() in status.upper():
            true_status =  status
            break
    true_CF = ""
    for status in CF_STATUSES:
        if cf_status.upper() in status.upper():
            true_CF = status
            break
    record_id = get_unique_record_id(callsign, pilot_data)
    if true_status == "":
        return ""
    if record_id == "":
        return "No matching call sign record found"
    fields = {true_status: true_CF}
    try:
        print(true_status)
        airtable.update(record_id, fields)
        return str(true_CF + " assigned to " + callsign + " for " + true_status)
    except:
        return "You might be using a status that is not available for that particular CF. Try these:\nCF1 has the status : PASS, FAIL, RETRY\nCF2 has: PASS, FAIL, NO SHOW\nCF3 has: PASS, FAIL\nUpdate unsuccessful. Try again or use Airtable"
