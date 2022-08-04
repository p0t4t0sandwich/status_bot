#!/bin/python3
#--------------------------------------------------------------------
# Project: Minecraft Status Discord Bot
# Purpose: Get relevant information from Minecraft servers.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 4AUGUST2021
# Updated: 4AUGUST2022 - p0t4t0sandwich
#   - Overhauled the entire codebase
#   - Converted to the requests library for API calls
#--------------------------------------------------------------------
# API documentation: https://api.mcsrvstat.us/
# Credit: Anders G. Jørgensen - spirit55555.dk

import discord
import requests
import os
import json
import bot_library as b

path = "/app/status_bot"

class Status_Bot():
    """
    Purpose:
        To handle all aspects of the Status Bot.
    Pre-Conditions:
        None
    Post-Conditions:
        Handles all of the Bot's events and classes.
    Return:
        None
    """
    def __init__(self):
        self.cheese = True

    class Server():
        """
        Purpose:
            To store and format common server data.
        Pre-Conditions:
            None
        Post-Conditions:
            Handles all of common returned server data.
        Return:
            None
        """
        def __init__(self, address):
            self.address = address

        class debug():
            """
            Purpose:
                To store and format the server debug data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned server debug data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.ping = self.dct["ping"]
                self.query = self.dct["query"]
                self.srv = self.dct["srv"]
                self.querymismatch = self.dct["querymismatch"]
                self.ipinsrv = self.dct["ipinsrv"]
                self.cnameinsrv = self.dct["cnameinsrv"]
                self.animatedmotd = self.dct["animatedmotd"]
                self.cachetime = self.dct["cachetime"]

        class motd():
            """
            Purpose:
                To store and format the server motd data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned server motd data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.raw = self.dct["raw"]
                self.clean = self.dct["clean"]
                self.html = self.dct["html"]

        class players():
            """
            Purpose:
                To store and format the server player data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned server player data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.online = self.dct["online"]
                self.max = self.dct["max"]
                if "list" in self.dct.keys(): self.list = self.dct["list"]
                else: self.list = "N/A"
                if "uuid" in self.dct.keys(): self.uuid = self.dct["uuid"]
                else: self.uuid = "N/A"

    class Java(Server):
        """
        Purpose:
            To store and format the Java server API response.
        Pre-Conditions:
            :extends Server:
        Post-Conditions:
            Handles all of returned Java server data.
        Return:
            None
        """
        def __init__(self, address):
            super().__init__(address)
            self.dct = json.loads(requests.get(f"https://api.mcsrvstat.us/2/{self.address}").content)
            self.online = self.dct["online"]
            if self.online:
                self.ip = self.dct["ip"]
                self.port = self.dct["port"]
                self.debug = self.debug(self.dct["debug"])
                self.motd = self.motd(self.dct["motd"])
                self.players = self.players(self.dct["players"])
                self.version = self.dct["version"]
                if "protocol" in self.dct.keys(): self.protocol = self.dct["protocol"]
                else: self.protocol = "N/A"
                if "hostname" in self.dct.keys(): self.hostname = self.dct["hostname"]
                else: self.hostname = "N/A"
                if "icon" in self.dct.keys(): self.icon = self.dct["icon"]
                else: self.icon = "N/A"
                if "software" in self.dct.keys(): self.software = self.dct["software"]
                else: self.software = "N/A"
                if "map" in self.dct.keys(): self.map = self.dct["map"]
                else: self.map = "N/A"
                if "plugins" in self.dct.keys(): self.plugins = self.dct["plugins"]
                else: self.plugins = ["N/A"]
                if "mods" in self.dct.keys(): self.mods = self.mods(self.dct["mods"])
                else: self.mods = ["N/A"]
                if "info" in self.dct.keys(): self.info = self.info(self.dct["info"])
                else: self.info = ["N/A"]

        class plugins():
            """
            Purpose:
                To store and format the Java server plugin data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned Java server plugin data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.names = self.dct["names"]
                self.raw = self.dct["raw"]
    
        class mods():
            """
            Purpose:
                To store and format the Java server mod data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned Java server mod data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.names = self.dct["names"]
                self.raw = self.dct["raw"]

        class info():
            """
            Purpose:
                To store and format the Java server info data.
            Pre-Conditions:
                None
            Post-Conditions:
                Handles all of returned Java server info data.
            Return:
                None
            """
            def __init__(self, dct):
                self.dct = dct
                self.raw = self.dct["raw"]
                self.clean = self.dct["clean"]
                self.html = self.dct["html"]

    class Bedrock(Server):
        """
        Purpose:
            To store and format the Bedrock server API response.
        Pre-Conditions:
            :extends Server:
        Post-Conditions:
            Handles all of returned Bedrock server data.
        Return:
            None
        """
        def __init__(self, address):
            super().__init__(address)
            self.dct = json.loads(requests.get(f"https://api.mcsrvstat.us/bedrock/2/{self.address}").content)
            self.online = self.dct["online"]
            if self.online:
                self.ip = self.dct["ip"]
                self.port = self.dct["port"]
                self.debug = self.debug(self.dct["debug"])
                self.motd = self.motd(self.dct["motd"])
                self.players = self.players(self.dct["players"])
                self.version = self.dct["version"]
                if "protocol" in self.dct.keys(): self.protocol = self.dct["protocol"]
                else: self.protocol = "N/A"
                if "hostname" in self.dct.keys(): self.hostname = self.dct["hostname"]
                else: self.hostname = "N/A"
                if "software" in self.dct.keys(): self.software = self.dct["software"]
                else: self.software = "N/A"
                if "map" in self.dct.keys(): self.map = self.dct["map"]
                else: self.map = "N/A"
                self.gamemode = self.dct["gamemode"]
                self.serverid = self.dct["serverid"]

    class Bot():
        """
        Purpose:
            To serve as a hacked-together extension of the discord.Client() class.
        Pre-Conditions:
            None
        Post-Conditions:
            Responds to the Bot's events.
        """
        def __init__(self, bot_id):
            self.bot_id = bot_id

        # Logging function to decrease clutter.
        def log(self, channel, author, content):
            b.bot_logger(path, "status_bot", f'[{channel}] [{author}] {content}')
        
        def json_log(self, dictionary, channel, platform):
            """
            Purpose:
                Logs the Minecraft server data and analytics in Json files
            Pre-Conditions:
                :param dictionary: dictionary
                :param channel: String
                :param platform: String (java|bedrock)
            Post-Conditions:
                Saves analytical data to Json files
            Return:
                None
            """
            # Log Analytics
            b.bot_logger(path + "bot_data/", "status_bot", f"[{channel}] Saving analytics...")
            folder = path + f"bot_data/{channel}/"
            if not os.path.exists(folder):
                os.makedirs(folder)
            index = dictionary["hostname"]+ str(dictionary["port"]) + platform
            filename = folder + index
            file = open(filename +".json", "w")
            json.dump(dictionary, file)
            try:
                a = open(folder + "analytics.json", "r+")
            except:
                a = open(folder + "analytics.json", "w")
                json.dump({}, a)
                a.close()
                a = open(folder + "analytics.json", "r+")
            a_dct = eval(a.read())
            a.close()
            new_a = open(folder + "analytics.json", "r+")
            try:
                a_dct[index] += 1
            except:
                a_dct[index] = 1
            json.dump(a_dct, new_a)
            new_a.close()
            file.close()

        def status(self, channel, author, content):
            """
            Purpose:
                To return server data collected from the API.
            Pre-Conditions:
                :param channel: The discord server the message was sent in (message.guild)
                :param author: The Bot's name (discord.Client.user)
                :param content: The message formatted as a string (message.content)
            Post-Conditions:
                None
            Return:
                A discord.Embed object
            """
            # Init variables
            address = content.replace("!status","").replace(" ","")
            java = Status_Bot.Java(address)
            bedrock = Status_Bot.Bedrock(address)
            output = {}

            # Logic to list Java server data
            if java.online:
                version = java.version.split(", ")[-1]
                title = f"Java Server: {address}"
                description = f"{java.motd.clean[0]}\n{java.motd.clean[1]}\nPlayers: {java.players.online}/{java.players.max}\n{java.software}: {version}"
                image = f"https://api.mcsrvstat.us/icon/{address}"
                color = 0x65bf65

                # Log the output
                self.log(channel, author, description)
                self.json_log(java.dct, channel, "java")
            else:
                # The default image, saved in one of the bot's DMs (easier than decoding base 64 images)
                image = "https://cdn.discordapp.com/attachments/1004646221744443523/1004698049970446356/default-64.png"
                
                # Logic to list Bedrock server data
                if bedrock.online:
                    title = f"Bedrock Server: {address}"
                    description = f"{bedrock.motd.clean[0]}\nPlayers: {bedrock.players.online}/{bedrock.players.max}\n{bedrock.software}: {bedrock.version}"
                    color = 0x65bf65

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(bedrock.dct, channel, "bedrock")
                else:
                    # Error response
                    title = f"Error:"
                    description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                    color = 0xbf0f0f

                    # Log the output
                    self.log(channel, author, description)

            # Output Discord Embed object
            output["embed"] = discord.Embed(title = title, description = description, color = color)
            output["embed"].set_image(url=image)
            return output

        def players(self, channel, author, content):
            """
            Purpose:
                To return player data collected from the API.
            Pre-Conditions:
                :param channel: The discord server the message was sent in (message.guild)
                :param author: The Bot's name (discord.Client.user)
                :param content: The message formatted as a string (message.content)
            Post-Conditions:
                None
            Return:
                A discord.Embed object
            """
            # Init variables
            address = content.replace("!players","").replace(" ","")
            java = Status_Bot.Java(address)
            bedrock = Status_Bot.Bedrock(address)
            output = {}

            if java.online:
                # Logic to list Java players and data
                if java.players.online > 0:
                    # Initializing the title and description
                    title = f"Java Server: {address}"
                    description = f"Players ({java.players.online}/{java.players.max}): "

                    # Add Players to description
                    for i in java.players.list:
                        description += f"{i}, "
                    
                    # Add Info to description
                    if java.info != ["N/A"]:
                        description += f"\nInfo:"
                        for i in java.info.clean[0].split(", "):
                            description += f"\n- {i}"

                    # Add image and Colour
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0x65bf65

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
                else:
                    title = f"Java Server: {address}"
                    description = "No players online."
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0xe6d132

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
            else:
                image = "https://cdn.discordapp.com/attachments/1004646221744443523/1004698049970446356/default-64.png"
                
                # Logic to list Bedrock players
                if bedrock.online:
                    if bedrock.players.online > 0:
                        # Bedrock player info
                        title = f"Bedrock Server: {address}"
                        description = f"Players ({bedrock.players.online}/{bedrock.players.max}): "
                        for i in bedrock.players.list:
                            description += i + ", "
                        color = 0x65bf65

                        # Log the output
                        self.log(channel, author, description)
                        self.json_log(bedrock.dct, channel, "bedrock")
                    else:
                        title = f"Bedrock Server: {address}"
                        description = "No players online."
                        color = 0xe6d132

                        # Log the output
                        self.log(channel, author, description)
                        self.json_log(bedrock.dct, channel, "bedrock")
                else:
                    # Error response
                    title = f"Error:"
                    description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                    color = 0xbf0f0f

                    # Log the output
                    self.log(channel, author, description)

            # Output Discord Embed object
            output["embed"] = discord.Embed(title = title, description = description, color = color)
            output["embed"].set_image(url = image)
            return output

        def plugins(self, channel, author, content):
            """
            Purpose:
                To return player data collected from the API.
            Pre-Conditions:
                :param channel: The discord server the message was sent in (message.guild)
                :param author: The Bot's name (discord.Client.user)
                :param content: The message formatted as a string (message.content)
            Post-Conditions:
                None
            Return:
                A discord.Embed object
            """
            # Init variables
            address = content.replace("!plugins","").replace(" ","")
            java = Status_Bot.Java(address)
            output = {}

            if java.online:
                # Logic to list Java players and data
                if java.plugins != ["N/A"]:
                    # Initializing the title and description
                    title = f"Java Server: {address}"
                    description = ""

                    # Add Plugins to description
                    for i in java.plugins.names:
                        description += f"{i}, "

                    # Add image and Colour
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0x65bf65

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
                else:
                    title = f"Java Server: {address}"
                    description = "No plugins detected."
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0xe6d132

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
            else:
                image = "https://cdn.discordapp.com/attachments/1004646221744443523/1004698049970446356/default-64.png"
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.log(channel, author, description)

            # Output Discord Embed object
            output["embed"] = discord.Embed(title = title, description = description, color = color)
            output["embed"].set_image(url = image)
            return output

        def mods(self, channel, author, content):
            """
            Purpose:
                To return player data collected from the API.
            Pre-Conditions:
                :param channel: The discord server the message was sent in (message.guild)
                :param author: The Bot's name (discord.Client.user)
                :param content: The message formatted as a string (message.content)
            Post-Conditions:
                None
            Return:
                A discord.Embed object
            """
            # Init variables
            address = content.replace("!mods","").replace(" ","")
            java = Status_Bot.Java(address)
            output = {}

            if java.online:
                # Logic to list Java players and data
                if java.mods != ["N/A"]:
                    # Initializing the title and description
                    title = f"Java Server: {address}"
                    description = "Mods: "

                    # Add Mods to description
                    for i in java.mods.names:
                        description += f"{i}, "

                    # Add image and Colour
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0x65bf65

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
                else:
                    title = f"Java Server: {address}"
                    description = "No mods detected."
                    image = f"https://api.mcsrvstat.us/icon/{address}"
                    color = 0xe6d132

                    # Log the output
                    self.log(channel, author, description)
                    self.json_log(java.dct, channel, "java")
            else:
                image = "https://cdn.discordapp.com/attachments/1004646221744443523/1004698049970446356/default-64.png"
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.log(channel, author, description)

            # Output Discord Embed object
            output["embed"] = discord.Embed(title = title, description = description, color = color)
            output["embed"].set_image(url = image)
            return output

        def run(self):
            """
            Purpose:
                The main handler of the Bot's events, plus handling setup and discord.Client.run().
            Pre-Conditions:
                :param bot_id: The Discord bot's super secret id.
            Post-Conditions:
                Responds to the Bot's events.
            Return:
                None
            """
            client = discord.Client()

            # Startup response.
            @client.event
            async def on_ready():
                b.bot_logger(path, "status_bot", f'We have logged in as {client.user}')

            # on_message() event handling and responses.
            @client.event
            async def on_message(message):
                # Skips reading messages written by the bot.
                if message.author == client.user:
                    return

                channel = message.guild.name
                author = message.author
                content = message.content

                # The !status command and logging logic.
                if message.content.startswith('!status'):
                    self.log(channel, author, content)
                    statement = self.status(channel, client.user, content)
                    await message.channel.send(embed=statement["embed"])

                # The !players command and logging logic.
                if message.content.startswith('!players'):
                    self.log(channel, author, content)
                    statement = self.players(channel, client.user, content)
                    await message.channel.send(embed=statement["embed"])

                # The !plugins command and logging logic.
                if message.content.startswith('!plugins'):
                    self.log(channel, author, content)
                    statement = self.plugins(channel, client.user, content)
                    await message.channel.send(embed=statement["embed"])

                # The !mods command and logging logic.
                if message.content.startswith('!mods'):
                    self.log(channel, author, content)
                    statement = self.mods(channel, client.user, content)
                    await message.channel.send(embed=statement["embed"])

            client.run(self.bot_id)


if __name__ == "__main__":
    Status_Bot.Bot(os.getenv("BOT_ID")).run()