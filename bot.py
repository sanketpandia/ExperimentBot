import discord
from discord.ext import commands
import json

client = commands.Bot(command_prefix=">")
json_data = {}
with open('./aircraft-performances.json') as jsonf:
    json_data = json.load(jsonf)


@client.event
async def on_ready():
    print("Bot is ready. Logged in as {0.user}".format(client))


keyword = "AIRCRAFT PERFORMANCE"


def get_aircraft(message):
    aircrafts_listed = json_data["keys"]
    aircraft_flag = False

    for aircraft in aircrafts_listed:
        if aircraft in message:
            return aircraft

    return ""

def show_table(table):
    string = ''
    for line in table:
        string += '| {} '.format(line)
        string += '|\n'

    return string

def get_aircraft_list_string():
    aircraft_listed = json_data["keys"]

    aircraft_listed_str = ""
    counter = 2
    for plane in aircraft_listed:
        aircraft_listed_str = aircraft_listed_str + str(plane)

        if counter == 3:
            counter = 1
            aircraft_listed_str = aircraft_listed_str + "\n"
        else:
            empty_spaces = 50 - len(plane)

            aircraft_listed_str = aircraft_listed_str + empty_spaces * " "

        counter = counter + 1

    return "Sorry I couldn't recognise it. Try one from this list\n" + aircraft_listed_str

def get_optimised_aircraft_string(aircraft_data):
    aircraft_data_string = """
    **Aircraft**: {}                Flight Ceiling: {}
    MTOW: {}                    MLW: {}
    V2: {}                      VS: {}
    Climb: 
    5000: {}
    15000: {}
    24000: {}
    Mach climb: {}
    Cruise Speed: {}            Typical Range: {}
    Descent:
    Descent to 24000ft: {}      Descent to 10000ft: {}
    Approach / MCS: {}
    Landing Speed: {}
    Flap Speeds: {}
    Checklists: {}
    """
    return  aircraft_data_string.format(aircraft_data["Airplane"], aircraft_data["Ceiling"], aircraft_data["MTOW"], aircraft_data["MLW"],aircraft_data["V2"], aircraft_data["VS"], aircraft_data["Climb to 5000ft"], aircraft_data["Climb to 15000ft"],aircraft_data["Climb to 24000ft"], aircraft_data["Mach Climb"], aircraft_data["Cruise speed"], aircraft_data["Typical Range"],aircraft_data["Descend to 24000ft"], aircraft_data["Descend to 10000ft"], aircraft_data["Approach / MCS"],aircraft_data["Landing"], aircraft_data["Flaps at descend"], aircraft_data["IF Checklist"])


@client.command(name="aircraft")
async def get_airplanes(ctx, args):
    aircraft = get_aircraft(args)
    get_aircraft_list_string()
    if aircraft == "":
        await ctx.send(get_aircraft_list_string())
    else:
        await ctx.send(get_optimised_aircraft_string(json_data[aircraft]))


client.run("NzkyNjg5MzE4MTE1Mjc4ODU4.X-hXdA.W8YtgHIkbu7PmOgjfoxP8INASaU")
