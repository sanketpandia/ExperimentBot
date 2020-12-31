import json
import re
import requests
import os
from dotenv import load_dotenv
import csv
import math

env = load_dotenv(dotenv_path="./.env")

base_url = os.getenv("IF_API_URL")
api_key = os.getenv("IF_API_KEY")

with open("./bot_controls.json", "r") as controlsf:
    bot_controls = json.load(controlsf)


def load_csv():
    csv_files = bot_controls["aircraft_livery_csv"]
    aircraft_livery_list = []
    for file in csv_files:
        with open(file) as f:
            reader = csv.DictReader(f)
            a = list(reader)
            aircraft_livery_list.append(a)

    aircraft_livery_master = []
    for file_data in aircraft_livery_list:
        for data in file_data:
            aircraft_livery_master.append(data)

    return aircraft_livery_master


def get_session_id():
    params = {"Authorization": "Bearer " + api_key}
    session = (requests.get(url=base_url + "sessions", headers=params))
    session = session.json()
    if "result" in session.keys():
        for server in session["result"]:
            if "EXPERT" in server["name"].upper():
                return server["id"]
    return ""


def get_fpl(session_id):
    params = {"Authorization": "Bearer " + api_key}
    fpl_all = (requests.get(url=base_url + "flightplans/" + session_id, headers=params))
    return (fpl_all.json())["result"]


def get_flights(session_id):
    params = {"Authorization": "Bearer " + api_key}
    flights = (requests.get(url=base_url + "flights/" + session_id, headers=params))
    return (flights.json())["result"]


def get_fpl_by_id(fpl_list, flight_id):
    for fpl in fpl_list:
        if fpl["flightId"] == flight_id and "waypoints" in fpl.keys():
            return fpl["waypoints"][0] + " - " + fpl["waypoints"][-1]
    return "No FPL Filed"


def format_string(text, limit):
    fixed_str = (text[:limit-1] + '.') if len(text) > limit else text
    fixed_str = (fixed_str+ (limit-len(fixed_str)) * " ") if len(fixed_str) < limit else fixed_str
    return fixed_str

def get_flight_plans_and_flights():
    session_id = get_session_id()
    if session_id == "":
        return ""
    flights = get_flights(session_id)

    aircraft_list = load_csv()

    fpl = get_fpl(session_id)
    afklm_flights = []
    live_flight_ids = []
    pattern = re.compile("\D*\d\d\dAK")
    for flight in flights:
        if pattern.match(flight["callsign"]):
            flight["route"] = get_fpl_by_id(fpl, flight["flightId"])
            for aircraft in aircraft_list:
                if flight["aircraftId"] == aircraft["AircraftId"] and flight["liveryId"] == aircraft["LiveryId"]:
                    flight["aircraft"] = aircraft["AircraftName"]
                    flight["livery"] = aircraft["LiveryName"]

                flight["altitude"] = str(math.ceil(float(flight["altitude"]) / 100) * 100)
                flight["speed"] = str(math.ceil(float(flight["speed"])))

            afklm_flights.append(flight)

    return afklm_flights


def get_afklm_flights(flights):
    afklm_flights = []
    pattern = re.compile("\D*\d\d\dAK")
    for flight in flights:
        if pattern.match(flight["CallSign"]):
            afklm_flights.append(flight)
    return afklm_flights


def get_live():
    afklm_flights = get_flight_plans_and_flights()
    response_string = "```\n      Callsign       |  IFC name  |    Aircraft    |     Livery     |   MSL   |  IAS  | Route\n\n"
    for flight in afklm_flights:
        string_pattern = "{} | {} | {} | {} | {}ft | {}kts | {}\n"
        if flight["username"] == None:
            flight["username"] = "IFC NA"
        flight["callsign"] = format_string(flight["callsign"], 20)
        flight["username"] = format_string(flight["username"], 10)
        flight["aircraft"] = format_string(flight["aircraft"], 14)
        flight["livery"] = format_string(flight["livery"], 14)
        response_string = response_string + string_pattern.format(flight["callsign"], flight["username"],
                                                                  flight["aircraft"], flight["livery"],
                                                                  flight["altitude"], flight["speed"], flight["route"])
    return response_string + "\n```"

def get_live_mobile():
    afklm_flights = get_flight_plans_and_flights()
    response_string = "```\n"
    for flight in afklm_flights:
        string_pattern = """
        Callsign: {}
        IFC Username: {}
        Aircraft: {}
        Livery: {}
        Altitude: {}ft
        Speed: {}kts
        {}\n"""
        response_string = response_string + string_pattern.format(flight["callsign"], flight["username"],
                                                                  flight["aircraft"], flight["livery"],
                                                                  flight["altitude"], flight["speed"], flight["route"])
    return response_string + "\n```"

def get_help():
    return "Not Implemented yet"