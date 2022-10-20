#!/bin/python3

import discord
import base64
import re
import json
import os
from discord.ext import commands, tasks
from mcstatus import JavaServer, BedrockServer

import bot_library as b

path = "/status_bot/"

async def server_status(address: str) -> JavaServer | BedrockServer:
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

async def decode_icon(server_icon: str, address: str) -> discord.File:
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
            with open(path + f"server-icons/{filename}.png", "wb") as f:
                f.write(base64.b64decode(server_icon.split(",")[1]))
                f.close()
            with open(path + f"server-icons/{filename}.png", "rb") as f:
                picture = discord.File(f, filename="image.png")
                f.close()
        except:
            with open(path + "server-icons/default-64.png", "rb") as f:
                picture = discord.File(f, filename="image.png")
                f.close()
    else:
        with open(path + "server-icons/default-64.png", "rb") as f:
                picture = discord.File(f, filename="image.png")
                f.close()

    return picture

async def status(address) -> discord.Embed | discord.File:
        # Init variables
        ((java_status, java_query), bedrock_status) = await server_status(address)

        # Logic for the server-icon.
        if java_status != None and "favicon" in java_status.raw.keys():
            file = await decode_icon(java_status.favicon, address)
        else:
            file = await decode_icon("None", address)

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

        elif java_status != None:
            title = f"Java Server: {address}"
            description = f"""{re.sub('[§][a-z0-9]','',java_status.description)}
            Players: {java_status.players.online}/{java_status.players.max}
            Version: {java_status.version.name}
            """

            # Add Colour
            color = 0x65bf65

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
            else:
                # Error response
                title = f"Minecraft Server: {address}"
                description = f"Whoops, something went wrong,\ncouldn't reach {address}.\t¯\\\\_(\"/)\_/¯"
                color = 0xbf0f0f

        # Output Discord Embed object
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_image(url=image)

        return (embed, file)

async def save_message(channel_id, message_id) -> None:
    filename = path + "/messages.json"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("{\"messages\":[" + f"{channel_id}-{message_id}" + "]}")
            f.close()

    else:
        with open(filename) as json_file:
            messages = json.load(json_file)
            json_file.close()

        new_messages = messages
        new_messages["messages"].append(f"{channel_id}-{message_id}")

        with open(filename, "w") as outfile:
            json.dump(new_messages, outfile, indent = 4)
            outfile.close()

class PersistentView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Refresh', style=discord.ButtonStyle.gray, custom_id='persistent_view:refresh')
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message("Refreshed!", ephemeral=True)
        msg = interaction.message
        address = msg.embeds.pop().title.split("Server: ")[1]
        (embed, file) = await status(address)
        await msg.edit(embed=embed, attachments=[file])

class StatusTracker(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.task.start()

    @tasks.loop(minutes=1)
    async def task(self):
        filename = path + "/messages.json"
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("{\"messages\":[]}")
                f.close()

        with open(filename) as json_file:
            messages = json.load(json_file)
            json_file.close()

        if messages["messages"] != []:
            new_messages = messages

            for i in new_messages["messages"]:
                try:
                    ids = i.split("-")
                    channel = self.bot.get_channel(int(ids[0]))
                    message = await channel.fetch_message(int(ids[1]))
                    address = message.embeds.pop().title.split("Server: ")[1]
                    (embed, file) = await status(address)
                    await message.edit(embed=embed, attachments=[file])
                except:
                    new_messages["messages"].remove(i)

            with open(filename, "w") as outfile:
                json.dump(new_messages, outfile, indent = 4)
                outfile.close()

    @commands.command()
    async def track(self, ctx: commands.Context, address) -> None:
        """Creates an embed to check server status"""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        self.bot.log(channel, author, content)

        (embed, file) = await status(address)

        # Log the output
        self.bot.log(channel, self.bot.user, embed.description)

        await ctx.message.delete()
        channel_id = ctx.channel.id
        message_id = (await ctx.send(embed=embed, file=file, view=PersistentView())).id
        await save_message(channel_id, message_id)



async def setup(bot: commands.bot) -> None:
    await bot.add_cog(StatusTracker(bot))
    bot.add_view(PersistentView())
