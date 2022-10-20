#!/bin/python3
#--------------------------------------------------------------------
# Project: Minecraft Status Discord Bot
# Purpose: Get relevant information from Minecraft servers.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 4AUGUST2021
# Updated: 19OCTOBER2022 - p0t4t0sandwich
#   - Overhauled the entire codebase (again)
#   - Converted all bot functions to use Cogs
#   - Switched from using an external API to using https://github.com/py-mine/mcstatus
#--------------------------------------------------------------------

from discord.ext import commands
import discord
import os

import bot_library as b

class StatusBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        self.path = "/status_bot/"
        self.name = "status_bot"

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
        )

    # Function to load in all the cogs.
    async def load_extensions(self) -> None:
        for folder in os.listdir("modules"):
            if os.path.exists(os.path.join("modules", folder, "cog.py")):
                b.bot_logger(self.path, self.name, f"Cog {folder} has been loaded")
                await self.load_extension(f"modules.{folder}.cog")

    # Logging function to decrease clutter.
    def log(self, channel, author, content) -> None:
        b.bot_logger(self.path, self.name, f'[{channel}] [{author}] {content}')

    # Function for On Ready behavior.
    async def on_ready(self) -> None:
        await self.wait_until_ready()
        b.bot_logger(self.path, self.name, f"We have logged in as {self.user}")
        self.owner_id = (await self.application_info()).owner.id
        await self.load_extensions()



if __name__ == "__main__":
    bot = StatusBot()
    bot.run(os.getenv("BOT_ID"))
