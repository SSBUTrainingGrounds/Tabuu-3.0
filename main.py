#Tabuu 3.0
#by Phxenix for SSBU Training Grounds
#Version: 3.2.0
#Last Changes: 13 March 2021
#Report any bugs to: Phxenix#1104
#
#To do list:
#- ask for command ideas & new statuses


import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import asyncio
import os


#
#this main file here loads all the cogs and starts the bot obviously, also includes our custom help command as a sort of glossary
#

intents=intents=discord.Intents.all() #intents so the bot can track its users
bot = Bot(command_prefix='%', intents=intents) # prefix for commands, we picked %(i use * for testing), intents same as above
client = discord.Client(intents=intents) 
bot.remove_command('help') #for a custom help command


#bot startup, and some event triggers without commands
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print ("Lookin' good, connected as", bot.user) #prints to the console that its ready



#help command, to tidy things up instead of using the normal shitty help command
@bot.command()
async def help(ctx): #add an admin check for these commands optimally
    embed = discord.Embed(title = "💻Admin Commands💻 - You need permissions for these!", color = discord.Color.red(), description='\n \
            ```%ban <@user> <reason>``` - Bans a member from the server.\n \
            ```%unban <@user>``` - Revokes a ban from the server.\n \
            ```%kick <@user> <reason>``` - Kicks a user from the server.\n \
            ```%clear <amount>``` - Purges X messages from the channel (default:1)\n \
            ```%delete <message IDs>``` - Deletes certain messages by ID\n \
            ```%mute <@user> <reason>``` - Mutes a user in the server.\n \
            ```%unmute <@user>``` - Unmutes a user in the server.\n \
            ```%tempmute <@user> X <reason>``` - Temporarily mutes a user for X minutes\n \
            ```%addrole <@user> <role>``` - Adds a role to a User.\n \
            ```%removerole <@user> <role>``` - Removes a role from a User.\n \
            ```%warn <@user> <reason>``` - Warns a user.\n \
            ```%warndetails <@user>``` - Shows detailed warnings of a user. \n \
            ```%deletewarn <@user> <warn_id>``` - Deletes a specific warning.\n \
            ```%clearwarns <@user>``` - Clears all the warnings of a user.\n \
            ```%records``` - Shows ban records')
    await ctx.author.send(embed=embed)
#second embed
    embed=discord.Embed(title= "💻Other commands💻 - For the working class", color = discord.Color.green(), description='\n \
            ```%modmail <your message>``` - A private way to communicate with the moderator team. Only works in my DM channel.\n \
            ```%singles``` - Used for 1v1 matchmaking in our arena channels.\n \
            ```%doubles``` - Used for 2v2 matchmaking in our arena channels.\n \
            ```%funnies``` - Used for non-competitive matchmaking in our arena channels.\n \
            ```%roleinfo <role>``` - Displays Role info.\n \
            ```%listrole <role>``` - Displays all the members with a certain Role.\n \
            ```%warns <@user>``` - Displays the number of warnings of a user.\n \
            ```%calendar``` - Calendar with our schedule \n \
            ```%server``` - Info about the server\n \
            ```%userinfo <member>``` - Shows user info of a mentioned member.\n \
            ```%coaching``` - Coaching requirements\n\
            ```%stagelist``` - Our Stagelist for Crew Battles\n \
            ```%coin``` - Throws a coin\n \
            ```%roll <NdN>``` - Rolling dice, format %roll 1d100\n \
            ```%invite``` - For those looking for an invite\n \
            ```%avatar <user>``` - Gets you the avatar of a user\n \
            ```%ping``` - Gets the ping of the bot.\n \
            ```%mp4<move>``` - Tells you the Mana Cost of any of Hero\'s moves\n \
            ```%joke``` - Jokes\n \
            ```%randomquote``` - Quotes\n \
            ```%pickmeup``` - Nice words\n \
            ```%wisdom``` - It\'s wisdom\n \
            ```%boo``` - Looking for a scare, huh?\n \
            ```%uwu``` - For the silly people\n \
            ```%tabuwu``` - For the dumb people')
    await ctx.author.send(embed=embed)

    
#loads all of our cogs
for filename in os.listdir(r'/root/tabuu bot/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


#run token, in different file because of security
with open(r'/root/tabuu bot/files/token.txt') as f:
    TOKEN = f.readline()

bot.run(TOKEN)