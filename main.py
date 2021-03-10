#Tabuu 3.0
#by Phxenix for SSBU Training Grounds
#Version: 3.0.2
#Last Changes: 10 March 2021
#Report any bugs to: Phxenix#1104
#
#To do list:
#- ask for command ideas & new statuses


import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from itertools import cycle
import asyncio
import json
import time
from datetime import datetime, timedelta
import os


#
#this main file here contains everything needed for bot startup + the custom help command
#

intents=intents=discord.Intents.all() #intents so the bot can track its users
bot = Bot(command_prefix='%', intents=intents) # prefix for commands, we picked %(i use * for testing), intents same as above
client = discord.Client(intents=intents) 
bot.remove_command('help') #for a custom help command
status = cycle(["type %help","Always watching 👀","Use the %modmail command in my DM's to privately contact the moderator team"]) #status cycles through these, update these once in a while to keep it fresh



#bot startup, and some event triggers without commands
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    await clear_mmrequests() #clears the mm files, so no ping gets stuck in there when you restart the bot, function is below the mm commands
    change_status.start() #starts the status loop
    warnloop.start() #and the warning check
    print ("Lookin' good, connected as", bot.user) #prints to the console that its ready



@tasks.loop(seconds=30) #the status loop, every 10 secs, could maybe crank that up to 20 or so
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))



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
            ```%records``` - Shows ban records'
            
        )
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






#here are the functions that get called on startup, the check for expired warnings and the clear mm files below

@tasks.loop(hours=24) #this here deletes warnings after 30 days, checks once on startup and then daily
async def warnloop():
    with open(r'/root/tabuu bot/json/warns.json', 'r') as f:
        users = json.load(f)

    tbd_users = []
    tbd_ids = []

    for i in users: #checks every user
        warned_user = i
        warn_id = users[warned_user].keys()
        for warn_id in users[warned_user].keys(): #checks every warning for every user
            timestamp = users[warned_user][warn_id]['timestamp']
            timestamp = datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")
            timenow = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")
            timenow = str(timenow)
            timenow = datetime.strptime(timenow, "%A, %B %d %Y @ %H:%M:%S %p") #have to do this shit, otherwise it doesnt read the right value for whatever reason
            timediff = timenow - timestamp
            daydiff = timediff.days #gets the time difference in days, if its over 30, it appends it to the "to be deleted"-list
            if daydiff > 29:
                tbd_users.append(warned_user)
                tbd_ids.append(warn_id)
                print(f"deleting warn_id #{warn_id} for user {warned_user} after 30 days")
                

    i = 0
    for x in tbd_ids: #deletes every entry in the list determined above, have to do it seperately, otherwise the length of the for loop changes, and that throws an error
        warned_user = tbd_users[i]
        warn_id = tbd_ids[i]
        print(warned_user, x)
        del users[warned_user][warn_id]
        print(f"deleted warn#{warn_id}!")
        i += 1
    
    with open(r'/root/tabuu bot/json/warns.json', 'w') as f:
        json.dump(users, f, indent=4)




#clear the mm files so that no ping gets stuck if i restart the bot
async def clear_mmrequests():

    #deleting singles file

    with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
        singles = json.load(f)
    
    singles_requests = []

    for user in singles:
        singles_requests.append(user)

    for user in singles_requests:
        del singles[user]
    
    with open(r'/root/tabuu bot/json/singles.json', 'w') as f:
        json.dump(singles, f, indent=4)

    print("singles file cleared!")

    #deleting doubles file

    with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
        doubles = json.load(f)
    
    doubles_requests = []

    for user in doubles:
        doubles_requests.append(user)

    for user in doubles_requests:
        del doubles[user]
    
    with open(r'/root/tabuu bot/json/doubles.json', 'w') as f:
        json.dump(doubles, f, indent=4)

    print("doubles file cleared!")

    #deleting funnies file

    with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
        funnies = json.load(f)
    
    funnies_requests = []

    for user in funnies:
        funnies_requests.append(user)

    for user in funnies_requests:
        del funnies[user]
    
    with open(r'/root/tabuu bot/json/funnies.json', 'w') as f:
        json.dump(funnies, f, indent=4)

    print("funnies file cleared!")




    
#loads all of our cogs

for filename in os.listdir(r'/root/tabuu bot/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


#run token, in different file because of security

with open(r'/root/tabuu bot/files/token.txt') as f:
    TOKEN = f.readline()

bot.run(TOKEN)