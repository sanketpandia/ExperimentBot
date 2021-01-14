import discord
from discord.ext import commands
import json
import airtable_connection
from dotenv import load_dotenv
import cmflight_instructors as cm
import bot_utils as utils
import pilot_academy as pa
import event_code as event

env = load_dotenv(dotenv_path="./.env")

import os

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
    message = message.upper()
    for aircraft in aircrafts_listed:
        if aircraft.upper() in message:
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
    5000ft: {}
    15000ft: {}
    24000ft: {}
    Mach climb: {}
    Cruise Speed: {}            Typical Range: {}
    Descent:
    Descent to 24000ft: {}      Descent to 10000ft: {}
    Approach / MCS: {}
    Landing Speed: {}
    Flap Speeds: {}
    """
    return aircraft_data_string.format(aircraft_data["Airplane"], aircraft_data["Ceiling"], aircraft_data["MTOW"],
                                       aircraft_data["MLW"], aircraft_data["V2"], aircraft_data["VS"],
                                       aircraft_data["Climb to 5000ft"], aircraft_data["Climb to 15000ft"],
                                       aircraft_data["Climb to 24000ft"], aircraft_data["Mach Climb"],
                                       aircraft_data["Cruise speed"], aircraft_data["Typical Range"],
                                       aircraft_data["Descend to 24000ft"], aircraft_data["Descend to 10000ft"],
                                       aircraft_data["Approach / MCS"], aircraft_data["Landing"],
                                       aircraft_data["Flaps at descend"])


@client.command(name="aircraft")
async def get_airplanes(ctx, args):
    aircraft = get_aircraft(args)
    get_aircraft_list_string()
    if aircraft == "":
        await ctx.send(get_aircraft_list_string())
    else:
        await ctx.send(get_optimised_aircraft_string(json_data[aircraft]))


@client.command(name="cm_flightlines")
async def get_flightlines(ctx, args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_flightlines", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = airtable_connection.get_flightlines(args)
    if len(flightlines) == 0:
        await ctx.send("Art thou sure you have thy callsign correct?")
    else:
        await ctx.send("Here art thy flight lines: \n" + flightlines)


@client.command(name="cm_time")
async def get_cm_time(ctx, args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_time", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = airtable_connection.get_time(args)
    if len(flightlines) == 0:
        await ctx.send("Your record seems to be misplaced/ unavailable. Or might be something wrong with me :cry:")
    else:
        await ctx.send(flightlines)


@client.command(name="cm_pirep")
async def file_cm_pirep(ctx, *args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_pirep", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    await ctx.author.send("Here's your link for career mode pirep: https://airtable.com/shrYTRklbSY8L5pYI")


@client.command(name="pirep")
async def file_pirep(ctx, *args):
    await ctx.author.send("Here's your link pirep: https://airtable.com/shru5XYHBMx1rnvVA")


@client.command(name="cm_unassigned")
async def get_unassigned(ctx):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_unassigned", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = cm.get_unassigned()
    if len(flightlines) == 0:
        await ctx.send("Unable to find any unassigned pilots. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the unassigned pilots\n" + flightlines)


@client.command(name="cm_my_trainee")
async def get_assigned(ctx, args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_my_trainee", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = cm.get_typeratings_by_region(args)
    if len(flightlines) == 0:
        await ctx.send(
            "Unable to find any assigned pilots to this region/pilot. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the pilots assigned to this region / FI \n" + flightlines)


@client.command(name="cm_assign")
async def get_instructors(ctx, callsign, instructor):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_assign", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = cm.update_instructor(callsign, instructor)
    if len(flightlines) == 0:
        await ctx.send("Invalid instructor name. Try using your name. Not Case sensitive. Try Again! :smile:")
    else:
        await ctx.send(str(flightlines))


@client.command(name="cm_update")
async def get_instructors(ctx, *args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("cm_update", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    if len(args) < 2:
        await ctx.send("use the format >cm_update AFKLMxxx in progress")
        return

    status = " ".join(args[1:])

    flightlines = cm.update_status(args[0], status)

    if len(flightlines) == 0:
        await ctx.send("Invalid callsign . Not Case sensitive. Try Again! :smile:")
    else:
        await ctx.send(str(flightlines))


@client.command(name="pa_unassigned")
async def get_unassigned_pa(ctx):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("pa_unassigned", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = pa.get_unassigned()
    if len(flightlines) == 0:
        await ctx.send("Unable to find any unassigned pilots. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the unassigned \n" + flightlines)


@client.command(name="pa_my_trainee")
async def get_assigned_pa(ctx, args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("pa_my_trainee", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = pa.get_typeratings_by_region(args)
    if len(flightlines) == 0:
        await ctx.send(
            "Unable to find any assigned pilots to this region/pilot. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the pilots assigned to this region/ FI \n" + flightlines)


@client.command(name="pa_assign")
async def assign_instructors_pa(ctx, callsign, instructor):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("pa_assign", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = pa.update_instructor(callsign, instructor)
    if len(flightlines) == 0:
        await ctx.send("Invalid instructor name. Try using your name. Not Case sensitive. Try Again! :smile:")
    else:
        await ctx.send(str(flightlines))


@client.command(name="pa_update")
async def update_instructors_pa(ctx, *args):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("pa_update", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    if len(args) < 2:
        await ctx.send("use the format >cm_update AFKLMxxx in progress")
        return

    status = " ".join(args[1:])

    flightlines = pa.update_status(args[0], status)

    if len(flightlines) == 0:
        await ctx.send(
            "Try using one of these statuses In Progress, Closed - Graduated, Contact to Schedule CF1, Closed - Did Not Complete, Removed - Inactivity")
    else:
        await ctx.send(str(flightlines))


@client.command(name="pa_cfupdate")
async def update_instructors_pa(ctx, arg1, arg2, arg3):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("pa_cfupdate", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = pa.update_cf(arg1, arg2, arg3)

    if len(flightlines) == 0:
        await ctx.send("Invalid callsign . Not Case sensitive. Try Again! :smile:")
    else:
        await ctx.send(str(flightlines))


@client.command(name="event")
async def get_next_event(ctx):
    role_names = [role.name for role in ctx.author.roles]
    validated_role = utils.validate_role("event", role_names)
    if not validated_role[0]:
        await ctx.send(validated_role[1])
        return
    flightlines = event.get_next_event()

    if flightlines == "\n=========================\n":
        await ctx.send("Sorry couldn't find any events")
    else:
        await ctx.send(flightlines)


@client.command(name="live_small")
async def get_live_flights(ctx):
    flightlines = utils.get_live()

    if len(flightlines) == 0:
        await ctx.send("Invalid callsign . Not Case sensitive. Try Again! :smile:")
    else:
        await ctx.send(flightlines)


@client.command(name="live")
async def get_live_flights_mobile(ctx):
    flightlines = utils.get_live_mobile()

    if len(flightlines) == 0:
        await ctx.send("Invalid callsign . Not Case sensitive. Try Again! :smile:")
    else:
        for live in flightlines:
            await ctx.send(live)


@client.command(name="learn")
async def get_learn_metar(ctx, args):
    get_url = utils.get_learn_url(args)
    if get_url[0] == "":
        await ctx.send(
            "```\nSorry we don't have this command. Available commands are: " + ', '.join(get_url[1]) + "\n```")
    else:
        await ctx.send(
            "```\nI have DMed you the document.\n You can use these commands too: " + ', '.join(get_url[1]) + "\n```")
        await ctx.author.send(get_url[0])


@client.command(name="wt3")
async def get_world_tour(ctx, args):
    if args.upper() == "WEBSITE":
        await ctx.author.send("https://www.if-airfranceklmva.com/worldtour-383119.html")
    elif args.upper() == "ROUTES":
        await ctx.author.send("https://airtable.com/shrFU6ORS5fazxMOA")
    else:
        await ctx.send("Try using >wt3 routes or >wt3 website")


@client.command(name="ifatc_afklm")
async def get_live_ifatc_afklm(ctx):
    flightlines = utils.get_afklm_ifatc()

    await ctx.send(flightlines)


@client.command(name="ifatc")
async def get_live_ifatc(ctx):
    flightlines = utils.get_ifatc()

    await ctx.send(flightlines)


@client.command()
async def afklm_help(ctx):
    role_names = [role.name for role in ctx.author.roles]
    help_response = utils.get_help(role_names)
    if help_response[1] == "":
        await ctx.send(help_response[0])
    else:
        await ctx.send(help_response[0])
        await ctx.author.send(help_response[1])


@client.command()
async def prep_my_flight(ctx):
    print(ctx.message.author.display_name)
    checklist_files = utils.get_user_current_flight_checklist(ctx.message.author.display_name)
    if len(checklist_files) <= 1:
        await ctx.send("***Sorry we don't have the checklist for " + checklist_files[0] + ". May the force be with "
                                                                                          "you!!***")
    else:
        await ctx.send("***I have DMed you the checklists for " + checklist_files[0] + "***")
        first_flag = True
        for file_name in checklist_files:
            if first_flag:
                first_flag = False
                continue
            with open('./checklists/' + file_name, 'rb') as fp:
                await ctx.author.send(file=discord.File(fp, file_name))


@client.command()
async def acars_pirep(ctx):
    print(ctx.message.author.display_name)
    pirep_data = utils.get_acars(ctx.message.author.display_name)
    if isinstance(pirep_data,str):
        await ctx.send("Make sure you are on the expert server with a flight plan! Also make sure your Discord Display Name "
                 "has your callsign in it")
        return
    option_string = "Send {} for {}\n"
    # await ctx.send("The current data I have are as follows\n "+ json.dumps(pirep_data, indent=4))
    if len(pirep_data.keys()) <= 1:
        await ctx.send("***Sorry I can't fetch your ACARS data. May the force be with "
                       "you!!***")
        return
    else:
        flight_mode_response = "Please type your messages/ replies within 30 secs. \nHello " + pirep_data["Callsign"][
            "callsign"] + ", What was your Flight mode? Choose " \
                          "from the list " \
                          "below:\n "
        flight_mode_flag = False
        while not flight_mode_flag:
            flight_mode_message = "What was your Flight mode? Choose " \
                                  "from the list " \
                                  "below:\n "
            for i in range(len(pirep_data["Flight Mode"])):
                flight_mode_response = flight_mode_response + option_string.format(i + 1, pirep_data["Flight Mode"][i])
            await ctx.send(flight_mode_response)
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if msg.content.isnumeric() and int(msg.content) <= len(pirep_data["Flight Mode"]):
                pirep_data["Flight Mode"] = pirep_data["Flight Mode"][int(msg.content) - 1]
                flight_mode_flag = True
            elif msg.content.upper() == "EXIT":
                await ctx.send("Sorry to see you go")
                return

        if len(pirep_data["Route"].keys()) == 0:
            route_flag = False
            while not route_flag:
                route_response = "Your route couldn't be validated. You can try to enter the route here in the format " \
                                 "SCEL-EHAM. Or you may choose any of the special routes below\n "
                for i in range(len(pirep_data["Special Routes"])):
                    route_response = route_response + option_string.format(i + 1, pirep_data["Special Routes"][i]["route"])
                await ctx.send(route_response)
                msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
                if msg.content.isnumeric():
                    response = int(msg.content)
                    if response > len(pirep_data["Special Routes"]):
                        await ctx.send("You sure you entered the right response?\n Try again!")
                    else:
                        pirep_data["Route"] = pirep_data["Special Routes"][int(msg.content) - 1]
                elif msg.content.upper() == "EXIT":
                    await ctx.send("Sorry to see you go")
                    return
                else:
                    pirep_data["Route"] = utils.validate_route(msg.content)
                    if len(pirep_data["Route"].keys()) > 0:
                        route_flag = True
        else:

            route_response = "Was your route **" + pirep_data["Route"][
                "route"] + "** or any of the special routes below? Reply ***YES*** " \
                           "to confirm if it was your route\n "
            for i in range(len(pirep_data["Special Routes"])):
                route_response = route_response + option_string.format(i + 1, pirep_data["Special Routes"][i]["route"])
            await ctx.send(route_response)
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if msg.content.isnumeric():
                response = int(msg.content)
                if response > len(pirep_data["Special Routes"]):
                    await ctx.send("You sure you entered the right response?\n Try again!")
                elif msg.content.upper() == "EXIT":
                    await ctx.send("Sorry to see you go")
                    return
                else:
                    pirep_data["Route"] = pirep_data["Special Routes"][int(msg.content) - 1]
                    await ctx.send("Your route was validated")
            elif msg.content.upper() == "YES":
                await ctx.send("Your route was validated")
            elif msg.content.upper() == "EXIT":
                await ctx.send("Sorry to see you go")
                return
            elif msg.content.upper() == "NO":
                route_flag = False
                while not route_flag:
                    await ctx.send("**Enter your route**:")
                    msg = await client.wait_for('message', check=lambda message: message.author == ctx.author,
                                                timeout=30)
                    pirep_data["Route"] = utils.validate_route(msg.content)
                    if len(pirep_data["Route"].keys()) > 0:
                        await ctx.send(
                            "The route you selected is **" + pirep_data["Route"]["route"] + "**. Do you agree?")
                        msg = await client.wait_for('message', check=lambda message: message.author == ctx.author,
                                                    timeout=30)
                        if msg.content.upper() == "YES":
                            route_flag = True

        time_flag = False
        while not time_flag:
            await ctx.send("What was your flight time? Enter in **hh:mm** format")
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if msg.content.upper() == "EXIT":
                await ctx.send("Sorry to see you go")
                return
            ft = utils.get_ft_from_string(msg.content)
            if ft == 0:
                await ctx.send("You sure you entered it right?")
            else:
                pirep_data["Flight Time"] = ft
                time_flag = True
        region_flag = False
        while not region_flag:
            region_response = "What is your flight region? Choose from the below options\n"
            for i in range(len(pirep_data["Pilot Region"])):
                region_response = region_response + option_string.format(i + 1, pirep_data["Pilot Region"][i])
            await ctx.send(region_response)
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if msg.content.isnumeric():
                response = int(msg.content)
                if response > len(pirep_data["Pilot Region"]):
                    await ctx.send("You sure you entered the right response?\n Try again!")
                else:
                    pirep_data["Pilot Region"] = pirep_data["Pilot Region"][int(msg.content) - 1]
                    region_flag = True
            elif msg.content.upper() == "EXIT":
                await ctx.send("Sorry to see you go")
                return
            else:
                ctx.send("Make sure to enter a number please!")
        ifc_id_flag = False
        while not ifc_id_flag:
            if pirep_data["What is your IFC Username?"] == "":
                await ctx.send("What is your IFC id? Please make sure you have it correct before hitting send!")
                msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
                pirep_data["What is your IFC Username?"] = msg.content
                ifc_id_flag = True
            elif msg.content.upper() == "EXIT":
                await ctx.send("Sorry to see you go")
                return
            else:
                ifc_id_flag = True
        await ctx.send("Do you have any remarks? If yes type them and hit enter. Otherwise type No and hit enter")
        msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
        if msg.content.upper() == "NO":
            pirep_data["Pilot Remarks"] = "\n~ Filled with the AFKLM bot.~"
        else:
            pirep_data["Pilot Remarks"] = msg.content + "\n~ Filled with the AFKLM bot.~"
        del pirep_data["Special Routes"]
        ft_hr = str(int(pirep_data["Flight Time"]/3600))
        ft_mn = str(int(pirep_data["Flight Time"]%3600*60))
        callsign = pirep_data["Callsign"]
        pirep_data["Callsign"] = callsign["callsign"]
        await ctx.send("Your log is ready. Verify the deets and type confirm to file it. Else you may type No\nYour "
                       "details are as follows:\n **Callsign**: {}\n**Route**: {}\n**Flight Mode**: {}\n**Flight "
                       "Time**:{}\n**Aircraft**: {}\n**Airline**: {}\n**IFC Username**: {}\n**Pilot Remarks**: {}".format(
            pirep_data["Callsign"], pirep_data["Route"]["route"], pirep_data["Flight Mode"], ft_hr+ ":"+ ft_mn,
            pirep_data["Aircraft"], pirep_data["Airline"], pirep_data["What is your IFC Username?"],
            pirep_data["Pilot Remarks"]
        ))
        msg = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
        if msg.content.strip().upper() == "CONFIRM":
            pirep_data["Callsign"] = [callsign["id"]]
            airtable_connection.file_pirep(pirep_data)
            await ctx.send("Your log has been successfully filed")
        elif msg.content.strip().upper() == "NO":
            await ctx.send("Sorry your log could not be filed.")


@client.command()
async def update_routes(ctx):
    await ctx.send("Routes are syncing with airtable. This should not take more than a minute")
    airtable_connection.refresh_routes()


@client.command()
async def file_pirep(ctx, number: int = 1):
    """Show the provided challenge number."""

    embed = discord.Embed(
        title="Testing the embed command",
        colour=discord.Colour(0xE5E242),
        url="https://airtable.com/shru5XYHBMx1rnvVA",
        description="To file a pirep",
    )

    embed.set_image(url="https://www.airfranceklm.com/sites/all/themes/afklm/images/logo.png")
    embed.set_thumbnail(
        url="https://www.airfranceklm.com/sites/all/themes/afklm/images/logo.png"
    )
    embed.set_author(name="The Experiment")
    embed.set_footer(
        text=f"File Pirep thing test by Sanket"
    )
    return await ctx.send(embed=embed)


client.run(os.getenv("BOT_ID"))
