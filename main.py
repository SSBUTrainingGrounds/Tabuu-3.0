# Tabuu 3.0
# by Phxenix for SSBU Training Grounds
# Version: 7.0.0
# Last Changes: 10 February 2022
# Contact me on Discord: Phxenix#1104


import discord
from discord.ext import commands
import os
import utils.logger
import utils.sqlite


# intents so the bot can track its users
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents, status=discord.Status.online)
# for a custom help command
bot.remove_command("help")

# to be used in the stats command
bot.version_number = "7.0.0"
bot.commands_ran = 0
bot.events_listened_to = 0

utils.logger.create_logger()

# sets up the database for first time use
@bot.event
async def on_connect():
    await utils.sqlite.setup_db()


# prints to the console when its ready
@bot.event
async def on_ready():
    print(
        f"Lookin' good, connected as: {str(bot.user)}, at: {discord.utils.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC"
    )


# loads all of our cogs
for filename in os.listdir(r"./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.command()
@commands.is_owner()
async def reloadcogs(ctx):
    """
    Command for manually reloading all cogs, so i dont have to restart the bot for every change.
    Can only be used by the owner of the bot.
    """
    # embeds can have up to 25 fields, we are at 21 cogs currently. need a different solution when we go over that
    embed = discord.Embed(title="Reloading cogs...", colour=discord.Colour.blue())
    for filename in os.listdir(r"./cogs"):
        if filename.endswith(".py"):
            try:
                bot.unload_extension(f"cogs.{filename[:-3]}")
                bot.load_extension(f"cogs.{filename[:-3]}")
                embed.add_field(
                    name=f"✅ Successfully reloaded {filename[:-3]} ✅",
                    value="Ready to go.",
                    inline=False,
                )
            except Exception as exc:
                embed.add_field(
                    name=f"❌ FAILED TO RELOAD {filename[:-3]} ❌",
                    value=exc,
                    inline=False,
                )
    await ctx.send(embed=embed)


@reloadcogs.error
async def reloadcogs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("You are not the owner of this bot!")
    else:
        raise error


# run token, in different file because of security
with open(r"./files/token.txt") as f:
    TOKEN = f.readline()

bot.run(TOKEN)
