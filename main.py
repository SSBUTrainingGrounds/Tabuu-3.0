#Tabuu 3.0
#by Phxenix for SSBU Training Grounds
#Version: 4.4.0
#Last Changes: 30 August 2021
#Report any bugs to: Phxenix#1104
#


import discord
from discord.ext import commands, tasks
import os


#
#this main file here loads all the cogs and starts the bot obviously, also holds the reloadcogs command
#

intents=intents=discord.Intents.all() #intents so the bot can track its users
bot = commands.Bot(command_prefix='%', intents=intents) # prefix for commands, we picked %, intents same as above
bot.remove_command('help') #for a custom help command

bot.version_number = "4.4.0" #the "version", maintain every now and then


#bot startup, and some event triggers without commands
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print ("Lookin' good, connected as", bot.user) #prints to the console that its ready


    
#loads all of our cogs
for filename in os.listdir(r'/root/tabuu bot/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')



#command for manually reloading all cogs, so i dont have to restart the bot for every change. can only be used by me
#embeds can have up to 25 fields, we are at 15 cogs currently. need a different solution when we go over that
@bot.command()
@commands.is_owner()
async def reloadcogs(ctx):
    embed = discord.Embed(title="Reloading cogs...", colour=discord.Colour.blue())
    for filename in os.listdir(r'/root/tabuu bot/cogs'):
        if filename.endswith('.py'):
            try:
                bot.unload_extension(f'cogs.{filename[:-3]}')
                bot.load_extension(f'cogs.{filename[:-3]}')
                embed.add_field(name=f"✅ Successfully reloaded {filename[:-3]} ✅", value="Ready to go.", inline=False)
            except Exception as exc:
                embed.add_field(name=f"❌ FAILED TO RELOAD {filename[:-3]} ❌", value=exc, inline=False)
    await ctx.send(embed=embed)

#error handling for the reloadcogs command
@reloadcogs.error
async def reloadcogs_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("You are not the owner of this bot!")
    else:
        raise error




#run token, in different file because of security
with open(r'/root/tabuu bot/files/token.txt') as f:
    TOKEN = f.readline()

bot.run(TOKEN)