import os
from logging import Logger

import discord
from discord.ext import commands

import utils.logger
import utils.sqlite


class Tabuu3(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="%",
            intents=discord.Intents.all(),
            status=discord.Status.online,
        )

        # The main prefix, used for listening to macros and display purposes mainly.
        self.main_prefix = "%"

        # To be used in the stats command.
        self.version_number = "9.23.0"
        self.commands_ran = 0
        self.events_listened_to = 0

        # A check to make sure persistent buttons do not get added twice.
        self.modmail_button_added = None

        # A consistent colour for embeds.
        self.colour = 0x007377

        # The time we store matchmaking pings for, in seconds.
        self.matchmaking_ping_time = 1800

    async def setup_hook(self) -> None:
        # We need to set up some stuff at startup.
        utils.logger.create_logger()
        await utils.sqlite.setup_db()

        for filename in os.listdir(r"./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    def get_logger(self, name: str) -> Logger:
        # Just attaching it to the bot so we dont have to import it everywhere.
        return utils.logger.get_logger(name)

    async def on_ready(self) -> None:
        print(
            f"Lookin' good, connected as: {str(bot.user)}, at: {discord.utils.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC"
        )


bot = Tabuu3()

with open(r"./files/token.txt", encoding="utf-8") as f:
    token = f.readline()

# We have our own logger, so we disable the default one.
bot.run(token, log_handler=None)
