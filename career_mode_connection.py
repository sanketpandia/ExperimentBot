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
    route_list = []
    for item in routes:
        route_list.append(item["fields"])
    return route_list


def get_pilot_data():
    routes = career_mode_airtable.get_all()
    pilot_list = []
    for item in routes:
        pilot_list.append(item["fields"])
    return pilot_list


def get_possible_routes(aircraft, hub, routes):
    possible_routes = []
    for route in routes:
        if route["Aircraft"] == aircraft and route["Hub"] == hub:
            possible_routes.append(route)
    return possible_routes


def assign_routes_to_pilot(callsign, aircraft, hub):
    routes = get_routes()
    possible_routes = get_possible_routes(aircraft, hub, routes)
    print(possible_routes)


assign_routes_to_pilot("AFKLM012", "B777", "EHAM")