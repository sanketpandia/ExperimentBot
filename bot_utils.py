import json
import re
import requests
import os
from dotenv import load_dotenv
import csv
import math
import airtable_connection
from os import walk
from os import listdir
from os.path import isfile, join

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
    fixed_str = (text[:limit - 1] + '.') if len(text) > limit else text
    fixed_str = (fixed_str + (limit - len(fixed_str)) * " ") if len(fixed_str) < limit else fixed_str
    return fixed_str


def get_flight_plans_and_flights():
    session_id = get_session_id()
    fpl = get_fpl(session_id)
    if session_id == "":
        return ""
    flights = get_flights(session_id)

    aircraft_list = load_csv()

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
    responses = []
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
        if len(response_string) >= 1800:
            responses.append(response_string + "\n```")
            response_string = "```\n"
        response_string = response_string + string_pattern.format(flight["callsign"], flight["username"],
                                                                  flight["aircraft"], flight["livery"],
                                                                  flight["altitude"], flight["speed"], flight["route"])
    responses.append(response_string + "\n```")
    return responses


def get_active_ifatc(session_id):
    params = {"Authorization": "Bearer " + api_key}
    flights = (requests.get(url=base_url + "atc/" + session_id, headers=params))
    return (flights.json())["result"]


def get_afklm_ifatc():
    session_id = get_session_id()
    ifatc = get_active_ifatc(session_id)
    pilots = airtable_connection.get_afklm_pilots()
    active_pilots = "```"
    pilot_string = "\nIFC Username: {}\nAirport: {} \n"
    print(pilots)
    for atc in ifatc:
        for pilot in pilots:
            if atc["username"].strip().upper() == pilot.strip().upper():
                active_pilots = active_pilots + "-----------------" + pilot_string.format(atc["username"],
                                                                                          atc["airportName"])
    if active_pilots == "```":
        return "```\nNo active AFKLM ATC found\n```"
    return active_pilots + "```"


def get_ifatc():
    session_id = get_session_id()
    ifatc = get_active_ifatc(session_id)
    active_pilots = "```"
    pilot_string = "\nIFC Username: {}\nAirport: {} \n"
    for atc in ifatc:
        active_pilots = active_pilots + "-----------------" + pilot_string.format(atc["username"],
                                                                                  atc["airportName"])
    if active_pilots == "```":
        return "```\nNo active ATC found\n```"
    return active_pilots + "```"


def get_learn_url(args):
    learn_commands = bot_controls["learn"]
    learn_keys = learn_commands.keys()
    for key in learn_keys:
        if key.upper() in args.upper():
            return [learn_commands[key], learn_commands]
    return ["", learn_keys]


def get_help(roles):
    admins = bot_controls["adminRoles"]
    help_stuff = "Here are the available commands:\n" + "\n".join(bot_controls["help"]) + "\n"
    admin_help_stuff = "Here are the available admin commands. Please don't reveal them to normal folk:\n" + "\n".join(
        bot_controls["admin_help"])
    admin_flag = False

    for admin in admins:
        if admin in roles:
            admin_flag = True
    if admin_flag:
        return [help_stuff, admin_help_stuff]
    else:
        return [help_stuff, ""]


def validate_role(command, user_role):
    role_restrictions = bot_controls["role_restrict"]
    admin_flag = False
    if command not in role_restrictions.keys():
        return [True, ""]
    else:
        for admin in role_restrictions[command]:
            if admin in user_role:
                admin_flag = True
        if admin_flag:
            return [True, ""]
        else:

            return [False, "\nYou don't have the required authorisation. You need to have the role of " + " or ".join(
                role_restrictions[command]) + " to be able to use these commands"]


def get_user_flight(callsign):
    session_id = get_session_id()
    if session_id == "":
        return ""
    flights = get_flights(session_id)

    pattern = re.compile("\D*" + callsign + "AK")
    for flight in flights:
        if pattern.match(flight["callsign"]):
            return flight

    return "Nothing found. Something broke"


def get_callsign_number(callsign):
    x = re.search("\D*AFKLM(\d\d\d)", callsign)
    found = x.group(1)
    return found


def recognise_aircraft():
    for file in os.listdir("./checklists"):
        if os.path.isfile(os.path.join("./checklists", file)):
            yield file


def get_aircraft_checklist_files(airframe):
    files = [airframe]
    for file in recognise_aircraft():
        if file.startswith(airframe):
            files.append(file)
    return files


def get_user_current_flight_checklist(callsign):
    callsign_number = get_callsign_number(callsign)
    flight = get_user_flight(callsign_number)

    aircraft_list = load_csv()
    aircraft_checklists = []
    for aircraft in aircraft_list:
        if flight["aircraftId"] == aircraft["AircraftId"] and flight["liveryId"] == aircraft["LiveryId"]:
            aircraft_checklists = get_aircraft_checklist_files(aircraft["AircraftName"])

    return aircraft_checklists


def get_pirep_json(field, key):
    with open("./pirep_configs.json") as pirep_f:
        pirep_configs = json.load(pirep_f)
    if key in pirep_configs[field]:
        return pirep_configs[field][key]
    return pirep_configs[field]["Other"]

def get_route_id(route):
    with open("./routes_check.json", "r") as routes_f:
        routes = json.load(routes_f)
    received_route = route.replace(" ", "")
    for route in routes:
        current_route = route["route"].replace(" ", "")
        if current_route.upper() == received_route.upper():
            return route["id"]
    return "Invalid route. Check with airtable and try again"

def get_pirep_configs(key):
    with open("./pirep_configs.json") as pirep_f:
        pirep_configs = json.load(pirep_f)
    return pirep_configs[key]

def validate_callsign(callsign):
    with open("./pilot_list.json", "r") as pilot_f:
        pilots = json.load(pilot_f)
    callsign = callsign.replace(" ", "")
    for pilot in pilots:
        current_pilot = pilot["callsign"].replace(" ","")
        if current_pilot == callsign:
            return pilot
    return {}

def validate_route(received_route):
    with open("./routes_check.json", "r") as routes_f:
        routes = json.load(routes_f)
    received_route = received_route.replace(" ", "")
    for route in routes:
        current_route = route["route"].replace(" ", "")
        print(current_route + "\t\t" + received_route)
        if current_route.upper() in received_route.upper():
            return route
    return {}

def get_ft_from_string(ft_string):
    try:
        split_str = ft_string.split(':')
        hrs_secs = int(split_str[0]) * 3600
        mm_secs = int(split_str[1]) * 60
        return hrs_secs + mm_secs
    except Exception as e:
        return 0

def get_spl_routes():
    with open("./pirep_configs.json", "r") as pirep_f:
        configs = json.load(pirep_f)
    return configs["Special Routes"]


def get_acars(callsign):
    callsign_number = get_callsign_number(callsign)
    callsign = "AFKLM" + str(get_callsign_number(callsign))
    flight = get_user_flight(callsign_number)
    print(type(flight))
    if isinstance(flight, str):
        return flight
    if flight["username"] is None:
        flight["username"] = ""
    aircraft_list = load_csv()
    for aircraft in aircraft_list:
        if flight["aircraftId"] == aircraft["AircraftId"] and flight["liveryId"] == aircraft["LiveryId"]:
            flight["aircraft"] = aircraft["AircraftName"]
            flight["livery"] = aircraft["LiveryName"]

            flight["altitude"] = str(math.ceil(float(flight["altitude"]) / 100) * 100)
            flight["speed"] = str(math.ceil(float(flight["speed"])))

    session_id = get_session_id()
    fpl = get_fpl(session_id)
    flight["route"] = get_fpl_by_id(fpl, flight["flightId"])
    flight["AFKLM_Callsign"] = callsign
    pirep = {"Callsign": validate_callsign(callsign),
             "Aircraft": get_pirep_json("AircraftMappings", flight["aircraft"]),
             "Airline": get_pirep_json("AirlineMappings", flight["livery"]),
             "Route": validate_route(flight["route"]),
             "Flight Mode": get_pirep_configs("Flight Modes"),
             "Flight Time": 0,
             "What is your IFC Username?": flight["username"],
             "Pilot Region": get_pirep_configs("Pilot Regions"),
             "Pilot Remarks": ""}
    spl_routes = get_spl_routes()
    routes_spl = []
    for key in spl_routes.keys():
        routes_spl.append({
            "id": spl_routes[key],
            "route": key
        })

    pirep["Special Routes"] = routes_spl

    return pirep
