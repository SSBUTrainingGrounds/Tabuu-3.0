# Tabuu 3.0
# by Phxenix for SSBU Training Grounds
# Version: 8.4.0
# Last Changes: 25 February 2022
# Contact me on Discord: Phxenix#1104


import discord
from discord.ext import commands
import os
import utils.logger
import utils.sqlite
from cogs.modmail import ModmailButton


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

        # loads all of our cogs
        for filename in os.listdir(r"./cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")

        # to be used in %stats
        self.version_number = "8.4.0"
        self.commands_ran = 0
        self.events_listened_to = 0

        # check to make sure the buttons do not get added twice.
        self.persistent_views_added = None

    async def start(self, *args, **kwargs):
        # we override the start method to do set up the database and logging.
        utils.logger.create_logger()

        await utils.sqlite.setup_db()

        # getting the bot token
        with open(r"./files/token.txt") as f:
            token = f.readline()

        await super().start(token=token, *args, **kwargs)

    def get_logger(self, name: str):
        # we just attach it to the bot so we dont have to import it everywhere.
        return utils.logger.get_logger(name)

    async def close(self):
        # closing the connection on bot shutdown.
        # this is more of a placeholder for now.
        await super().close()

    async def on_ready(self):
        # adds the modmail button if it hasnt already.
        # on_ready gets called multiple times, so the check is needed.
        if not self.persistent_views_added:
            self.add_view(ModmailButton())
            self.persistent_views_added = True

        print(
            f"Lookin' good, connected as: {str(bot.user)}, at: {discord.utils.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC"
        )


bot = Tabuu3()

bot.run()
