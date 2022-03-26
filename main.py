# Tabuu 3.0
# by Phxenix for SSBU Training Grounds
# Version: 9.3.1
# Last Changes: 26 March 2022
# Contact me on Discord: Phxenix#1104

import os

import discord
from discord.ext import commands

import utils.logger
import utils.sqlite


class Tabuu3(commands.Bot):
    """
    The bot.
    """

    def __init__(self):
        super().__init__(
            command_prefix="%",
            intents=discord.Intents.all(),
            status=discord.Status.online,
        )

        # to be used in %stats
        self.version_number = "9.3.1"
        self.commands_ran = 0
        self.events_listened_to = 0

        # check to make sure persistent buttons do not get added twice.
        self.modmail_button_added = None

    async def start(self, *args, **kwargs):
        # getting the bot token
        with open(r"./files/token.txt", encoding="utf-8") as f:
            token = f.readline()

        await super().start(token=token, *args, **kwargs)

    async def setup_hook(self):
        # we need to set up some stuff at startup
        utils.logger.create_logger()

        await utils.sqlite.setup_db()

        # loads all of our cogs
        for filename in os.listdir(r"./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    def get_logger(self, name: str):
        # we just attach it to the bot so we dont have to import it everywhere.
        return utils.logger.get_logger(name)

    async def close(self):
        # closing the connection on bot shutdown.
        # this is more of a placeholder for now.
        await super().close()

    async def on_ready(self):
        print(
            f"Lookin' good, connected as: {str(bot.user)}, at: {discord.utils.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC"
        )


bot = Tabuu3()

bot.run()
