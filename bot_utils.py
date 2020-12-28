import json
import re

with open('./flights.json',) as jsonf:
    json_data = json.load(jsonf)

def get_afklm_flights(flights):
    afklm_flights = []
    pattern = re.compile("\D*\d\d\dAK")
    for flight in flights:
        if pattern.match(flight["CallSign"]):
            afklm_flights.append(flight)
    return  afklm_flights


def get_live():
    objects = json_data
    afklm_flights = get_afklm_flights(objects)
    response_string = "Callsign    |    IFC name    |    Aircraft    |    Livery    |    MSL    |    IAS\n"
    for flight in afklm_flights:
        string_pattern = "{}     |    {}    |    {}    |    {}   |     {}    |    {}\n"
        response_string = response_string + string_pattern.format(flight["CallSign"], flight["DisplayName"], flight["Aircraft"], flight["Livery"], flight["Altitude"], flight["Speed"])
    return response_string
