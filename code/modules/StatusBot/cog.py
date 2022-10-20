#!/bin/python3

import discord
import base64
import re
from discord.ext import commands
from mcstatus import JavaServer, BedrockServer

import bot_library as b

class StatusBot(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def server_status(self, address: str) -> JavaServer | BedrockServer:
        # Java
        java = await JavaServer.async_lookup(address, timeout=0.5)
        try: 
            java_status = await java.async_status()
        except:
            java_status = None

        try: 
            java_query = await java.async_query()
        except:
            java_query = None

        # Bedrock
        bedrock = BedrockServer.lookup(address, timeout=0.5)
        try:
            bedrock_status = await bedrock.async_status()
        except:
            bedrock_status = None

        return ((java_status, java_query), bedrock_status)

    async def decode_icon(self, server_icon: str, address: str) -> discord.File:
        """
        Input:
            :param server_icon:
        Function: Uses the API to convert mcip into a dictionary, grabs base64 png data and
                returns it as a discord.File() object.
        Returns: discird.File()
        """

        filename = address.replace(":", "-").replace(".", "-")

        if "data:image/png;base64," in server_icon:
            try:
                with open(self.bot.path + f"server-icons/{filename}.png", "wb") as f:
                    f.write(base64.b64decode(server_icon.split(",")[1]))
                    f.close()
                with open(self.bot.path + f"server-icons/{filename}.png", "rb") as f:
                    picture = discord.File(f, filename="image.png")
                    f.close()
            except:
                with open(self.bot.path + "server-icons/default-64.png", "rb") as f:
                    picture = discord.File(f, filename="image.png")
                    f.close()
        else:
            with open(self.bot.path + "server-icons/default-64.png", "rb") as f:
                    picture = discord.File(f, filename="image.png")
                    f.close()

        return picture

    # The !status command and logging logic.
    @commands.command()
    async def status(self, ctx: commands.Context, address) -> None:
        """Returns status data collected from the server."""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        self.bot.log(channel, author, content)

        # Init variables
        ((java_status, java_query), bedrock_status) = await self.server_status(address)

        # Logic for the server-icon.
        if java_status != None and "favicon" in java_status.raw.keys():
            file = await self.decode_icon(java_status.favicon, address)
        else:
            file = await self.decode_icon("None", address)

        image = f"attachment://image.png"


        # Logic to send the Java Server status
        if java_query != None:
            title = f"Java Server: {address}"
            description = f"""{re.sub('[§][a-z0-9]','',java_query.motd)}
            Players: {java_query.players.online}/{java_query.players.max}
            {java_query.software.brand}: {java_query.software.version}
            """

            # Add Colour
            color = 0x65bf65

            # Log the output
            self.bot.log(channel, self.bot.user, description)
            #self.json_log(java_status.raw, channel, "java")

        elif java_status != None:
            title = f"Java Server: {address}"
            description = f"""{re.sub('[§][a-z0-9]','',java_status.description)}
            Players: {java_status.players.online}/{java_status.players.max}
            Version: {java_status.version.name}
            """

            # Add Colour
            color = 0x65bf65

            # Log the output
            self.bot.log(channel, self.bot.user, description)
            #self.json_log(java_status.raw, channel, "java")

        else:
            # Response for a Bedrock server
            if bedrock_status != None:
                title = f"Bedrock Server: {address}"
                description = f"""{re.sub('[§][a-z0-9]','',bedrock_status.motd)}
                {re.sub('[§][a-z0-9]','',bedrock_status.map)}
                Players: {bedrock_status.players_online}/{bedrock_status.players_max}
                {bedrock_status.version.brand}: {bedrock_status.version.version}
                """
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
            else:
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.bot.log(channel, self.bot.user, description)

        # Output Discord Embed object
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_image(url=image)

        await ctx.send(embed=embed, file=file)
    
    # The !players command and logging logic.
    @commands.command()
    async def players(self, ctx: commands.Context, address) -> None:
        """Returns player data collected from the server."""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        self.bot.log(channel, author, content)

        # Init variables
        ((java_status, java_query), bedrock_status) = await self.server_status(address)

        # Logic for the server-icon.
        if java_status != None and "favicon" in java_status.raw.keys():
            file = await self.decode_icon(java_status.favicon, address)
        else:
            file = await self.decode_icon("None", address)

        image = f"attachment://image.png"

        # Logic to list Java players
        if java_query != None:
            if java_query.players.online > 0:
                # Initializing the title and description
                title = f"Java Server: {address}"
                description = "Players:\n"

                # Add Players to description
                description += ", ".join(java_query.players.names)

                # Add Colour
                color = 0x65bf65

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")
            else:
                title = f"Java Server: {address}"
                description = "No players online."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")

        elif java_status != None:
            if java_status.players.online > 0:
                # Initializing the title and description
                title = f"Java Server: {address}"
                description = "Players:\n"

                # Add Players to description
                description += ", ".join(player.name for player in java_status.players.sample)

                # Add Colour
                color = 0x65bf65

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")

            else:
                title = f"Java Server: {address}"
                description = "No players online."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")

        else:
            # Response for a Bedrock server
            if bedrock_status != None:
                if bedrock_status.players_online > 0:
                    # Initializing the title and description
                    title = f"Bedrock Server: {address}"
                    description = f"Players: {bedrock_status.players_online}/{bedrock_status.players_max}\n"
                    color = 0x65bf65

                else:
                    title = f"Bedrock Server: {address}"
                    description = "No players online."
                    color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
            else:
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.bot.log(channel, self.bot.user, description)

        # Output Discord Embed object
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_image(url=image)

        await ctx.send(embed=embed, file=file)
    
    # The !plugins command and logging logic.
    @commands.command()
    async def plugins(self, ctx: commands.Context, address) -> None:
        """Returns plugin data collected from the server."""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        self.bot.log(channel, author, content)

        # Init variables
        ((java_status, java_query), bedrock_status) = await self.server_status(address)

        # Logic for the server-icon.
        if java_status != None and "favicon" in java_status.raw.keys():
            file = await self.decode_icon(java_status.favicon, address)
        else:
            file = await self.decode_icon("None", address)

        image = f"attachment://image.png"

        if java_query != None:
            # Logic to list Java plugins
            if java_query.software.plugins != []:
                # Initializing the title and description
                title = f"Java Server: {address}"
                description = "Plugins:\n"

                # Add Plugin to descriptions
                for i in java_query.software.plugins:
                    description += f"{i}, "

                # Add Colour
                color = 0x65bf65

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")
            else:
                title = f"Java Server: {address}"
                description = "No plugins detected."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")
        else:
            # Response for a Bedrock server
            if bedrock_status != None:
                title = f"Bedrock Server: {address}"
                description = "No plugins detected."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
            else:
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.bot.log(channel, self.bot.user, description)

        # Output Discord Embed object
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_image(url=image)

        await ctx.send(embed=embed, file=file)

    # The !mods command and logging logic.
    @commands.command()
    async def mods(self, ctx: commands.Context, address: str) -> None:
        """Returns mod data collected from the server."""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        self.bot.log(channel, author, content)

        # Init variables
        ((java_status, java_query), bedrock_status) = await self.server_status(address)

        # Logic for the server-icon.
        if java_status != None and "favicon" in java_status.raw.keys():
            file = await self.decode_icon(java_status.favicon, address)
        else:
            file = await self.decode_icon("None", address)

        image = f"attachment://image.png"

        if java_status != None:
            # Logic to list Java mods
            if "modinfo" in java_status.raw.keys() and java_status.raw["modinfo"]["modList"] != []:
                # Initializing the title and description
                title = f"Java Server: {address}"
                description = "Mods:\n"

                # Add Mods to descriptions
                for i in java_status.raw["modinfo"]["modList"]:
                    modid = i["modid"]
                    version = i["version"]
                    description += f"{modid}: v{version}, "

                # Add Colour
                color = 0x65bf65

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")
            else:
                title = f"Java Server: {address}"
                description = "No mods detected."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
                #self.json_log(java_status.raw, channel, "java")
        else:
            # Response for a Bedrock server
            if bedrock_status != None:
                title = f"Bedrock Server: {address}"
                description = "No mods detected."
                color = 0xe6d132

                # Log the output
                self.bot.log(channel, self.bot.user, description)
            else:
                # Error response
                title = f"Error:"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

                # Log the output
                self.bot.log(channel, self.bot.user, description)

        # Output Discord Embed object
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_image(url=image)

        await ctx.send(embed=embed, file=file)

    # The !dump command and logging logic.
    @commands.command()
    @commands.is_owner()
    async def dump(self, ctx: commands.Context, address) -> None:
        """To return server data collected from the server response."""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        # Init variables
        # Java
        java = await JavaServer.async_lookup(address)

        try:
            java_status = (await java.async_query()).raw
        except:
            java_status = "No Java server detected"

        # Bedrock
        bedrock = BedrockServer.lookup(address)
        try:
            bedrock_status = await bedrock.async_status()
        except:
            #bedrock_status = "No Bedrock server detected"
            pass

        description = f"""Java Dump:
        {java_status}
        Bedrock Dump:
        Ping: {round(bedrock_status.latency*1000)}ms
        Gamemode: {bedrock_status.gamemode}
        MOTD: {bedrock_status.motd}
        Map: {bedrock_status.map}
        Players: {bedrock_status.players_online}/{bedrock_status.players_max}
        Version: {bedrock_status.version.version}
        Server Type: {bedrock_status.version.brand}
        Protocol: {bedrock_status.version.protocol}
        """

        # Log the output
        self.bot.log(channel, author, content)
        self.bot.log(channel, self.bot.user, description)

        await ctx.send("Info dumped to the log.")

async def setup(bot: commands.bot) -> None:
    await bot.add_cog(StatusBot(bot))
