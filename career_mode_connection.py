from airtable import Airtable
from dotenv import load_dotenv
import json
import datetime
from dateutil.parser import parse
import math

env = load_dotenv(dotenv_path="./.env")

import os

route_sets_airtable = Airtable(os.getenv("CAREER_MODE_BASE_ID"), 'Career Mode Route Sets',
                               os.getenv("JOHN_AIRTABLE_ID"))
career_mode_airtable = Airtable(os.getenv("CAREER_MODE_BASE_ID"), 'Career Mode Pilots', os.getenv("JOHN_AIRTABLE_ID"))


def get_routes():
    routes = route_sets_airtable.get_all()
    return routes


def get_pilot_data(callsign):
    routes = career_mode_airtable.get_all()
    for item in routes:
        if callsign.upper() in item["fields"]["Callsign"].upper():
            return item
    return {}


def get_possible_routes(aircraft, hub, routes, airline):
    possible_routes = []
    for route in routes:
        if route["Aircraft"] == aircraft and route["Hub"] == hub:
            possible_routes.append(route)
    return possible_routes


def get_next_routes(assigned_route, routes):
    print(assigned_route)
    print(routes)
    route_index = 0
    while route_index < len(routes):
        index = 0
        while index < len(assigned_route):
            if assigned_route[index] == routes[route_index] and not(route_index == (len(routes) - 1)):
                return routes[index] + 1
            index = index + 1
        route_index = route_index + 1
    return "Something went wrong"



def assign_routes_to_pilot(callsign, aircraft, hub):
    routes = get_routes()
    possible_routes = get_possible_routes(aircraft, hub, routes)

    pilot_data = get_pilot_data(callsign)
    new_routes = get_next_routes(pilot_data["Assigned Routes"], possible_routes)
    print(new_routes)



