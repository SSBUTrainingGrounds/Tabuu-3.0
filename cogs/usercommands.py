import discord
from discord.ext import commands, tasks
import random
from fuzzywuzzy import process
from discord.utils import get
import platform
import asyncio
import psutil
import datetime
import os
import time


#
#this file here contains most useful commands that don't need special permissions
#

class Usercommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command() #some basic info about a role
    async def roleinfo(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role))
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
            role = get(ctx.guild.roles, name=match)

        #the above block searches all roles for the closest match, as seen in the admin cog

        creationdate = role.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p")
        embed = discord.Embed(color = role.colour)
        embed.add_field(name="Role Name:", value=role.mention, inline=True)
        embed.add_field(name="Role ID:", value=role.id, inline=True)
        embed.add_field(name="Users with role:", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable:", value=role.mentionable, inline=True)
        embed.add_field(name="Displayed Seperately:", value=role.hoist, inline=True)
        embed.add_field(name="Color:", value=role.color, inline=True)
        embed.set_footer(text=f"Role created on: {creationdate} CET")
        await ctx.send(embed=embed)

    @commands.command(aliases=['listroles']) #lists every member in the role if there arent more than 60 members, to prevent spam
    async def listrole(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role))
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
            role = get(ctx.guild.roles, name=match)

        members = role.members
        memberlist = []

        if len(members) > 60:
            await ctx.send(f"Users with the {role} role ({len(role.members)}):\nToo many users to list!")
            return
        if len(members) == 0:
            await ctx.send(f"No user currently has the {role} role!")
            return
        else:
            for member in members:
                memberlist.append(f"{member.name}#{member.discriminator}")
            all_members = ', '.join(memberlist)
            await ctx.send(f"Users with the {role} role ({len(role.members)}):\n{all_members}")


    #modmail
    @commands.command()
    async def modmail(self, ctx, *, args):
        if str(ctx.channel.type) == 'private': #only works in dm's
            guild = self.bot.get_guild(739299507795132486) #ssbu tg server
            modmail_channel = self.bot.get_channel(806860630073409567) #modmail channel
            mod_role = discord.utils.get(guild.roles, id=739299507816366106)
            atm = ''
            if ctx.message.attachments:
                atm = ", ".join([i.url for i in ctx.message.attachments])
            await modmail_channel.send(f"**✉️ New Modmail {mod_role.mention}! ✉️**\nFrom: {ctx.author} \nMessage:\n{args} \n{atm}")
            await ctx.send("Your message has been sent to the Moderator Team. They will get back to you shortly.")


        else:
            await ctx.message.delete()
            await ctx.send("For the sake of privacy, please only use this command in my DM's. They are always open for you.")
    

    #serverinfo, gives out basic info about the server
    @commands.command(aliases=['serverinfo'])
    async def server(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title=f"{server.name}({server.id})", color=discord.Color.green())
        embed.add_field(name="Created on:", value=server.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p CET"), inline=True) #same as above
        embed.add_field(name="Owner:", value=server.owner.mention, inline=True)
        embed.add_field(name="Channels:", value=len(server.channels), inline=True)
        embed.add_field(name="Members:", value=f"{len(server.members)} (Bots: {sum(member.bot for member in server.members)})")
        embed.add_field(name="Emojis:", value=len(server.emojis))
        embed.add_field(name="Roles:", value=len(server.roles))
        embed.set_thumbnail(url=server.icon_url)
        await ctx.send(embed=embed)

    #userinfo
    @commands.command(aliases=['user'])
    async def userinfo(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            activity = member.activity.name
        except:
            activity = "None"

        embed=discord.Embed()
        embed = discord.Embed(title=f"Userinfo of {member.name}#{member.discriminator}", color=member.top_role.color)
        embed.add_field(name="Name:", value=member.mention, inline=True)
        embed.add_field(name="ID:", value=member.id, inline=True)
        embed.add_field(name="Number of Roles:", value=f"{(len(member.roles)-1)}", inline=True) #gives the number of roles to prevent listing like 35 roles, -1 for the @everyone role
        embed.add_field(name="Top Role:", value=member.top_role.mention, inline=True) #instead only gives out the important role
        embed.add_field(name="Joined Server on:", value=member.joined_at.strftime("%A, %B %d %Y @ %H:%M:%S %p CET"), inline=True) #the strftime and so on are for nice formatting
        embed.add_field(name="Joined Discord on:", value=member.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p CET"), inline=True) #would look ugly otherwise
        embed.add_field(name="Online Status:", value=member.status, inline=True)
        embed.add_field(name="Activity Status:", value=activity, inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    #some bot stats
    @commands.command(aliases=['stats'])
    async def botstats(self, ctx):
        pyversion = platform.python_version() #python version
        dpyversion = discord.__version__ #discord.py version
        servercount = len(self.bot.guilds) #total servers
        membercount = len(set(self.bot.get_all_members())) #total members
        proc = psutil.Process(os.getpid()) #gets process id
        uptimeSeconds = time.time() - proc.create_time() #gets uptime in seconds
        delta = datetime.timedelta(seconds=uptimeSeconds) #converts that to a timedelta object
        tabuu3 = self.bot.get_user(785303736582012969) #the bot
        embed = discord.Embed(title="Tabuu 3.0 Stats", color=0x007377, url="https://github.com/sonnenbankpimp/Tabuu-3.0-Bot") #link to the github, its still private but maybe not in the future, who knows
        embed.add_field(name="Name:", value=f"{tabuu3.mention}", inline=True)
        embed.add_field(name="Servers:", value=servercount, inline=True)
        embed.add_field(name="Total Users:", value=membercount, inline=True)
        embed.add_field(name="Bot Version:", value=self.bot.version_number, inline=True)
        embed.add_field(name="Python Version:", value=pyversion, inline=True)
        embed.add_field(name="discord.py Version:", value=dpyversion, inline=True)
        embed.add_field(name="CPU Usage:", value=f"{psutil.cpu_percent(interval=1)}%", inline=True) #only gets the % value
        embed.add_field(name="RAM Usage:", value=f"{psutil.virtual_memory()[2]}%", inline=True) #only gets the % value, thats what the [2] is for
        embed.add_field(name="Uptime:", value=str(delta).split(".")[0], inline=True) #the split thing is to get rid of the microseconds, who cares about uptime in microseconds
        embed.set_footer(text="Creator: Phxenix#1104, hosted on: Raspberry Pi 3B+")
        embed.set_thumbnail(url=tabuu3.avatar_url)
        await ctx.send(embed=embed)


    @commands.command(aliases=['icon'])
    async def avatar(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.send(member.avatar_url)


    @commands.command()
    async def poll(self, ctx, question, *options: str):
        if len(options) < 2:
            await ctx.send("You need at least 2 options to make a poll!") #obviously
            return
        if len(options) > 10:
            await ctx.send("You can only have 10 options at most!") #reaction emoji limit
            return
        try:
            await ctx.message.delete()
        except:
            pass

        reactions = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','0️⃣'] #in order
        description = []

        for x, option in enumerate(options):
            description += f'\n{reactions[x]}: {option}' #adds the emoji: option to the embed
        embed = discord.Embed(title=question, description=''.join(description), colour=discord.Colour.dark_purple())
        embed.set_footer(text=f'Poll by {ctx.author}')
        embed_message = await ctx.send(embed=embed) #sends the embed out
        for reaction in reactions[:len(options)]: #and then reacts with the correct number of emojis
            await embed_message.add_reaction(reaction)


    #pic with our stagelist on it, change file when it changes
    @commands.command()
    async def stagelist(self, ctx):
        await ctx.send(file=discord.File(r"/root/tabuu bot/files/stagelist.png")) 

    #classic ping
    @commands.command()
    async def ping(self, ctx):
        pingtime=self.bot.latency * 1000
        await ctx.send(f"Ping: {round(pingtime)}ms")

    #invite link
    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Here's the invite link to our server: https://discord.gg/ssbutg") #if this link expires, change it

    #coaching info
    @commands.command()
    async def coaching(self, ctx):
        await ctx.send("It seems like you are looking for coaching: make sure to tell us what exactly you need so we can best assist you!\n\n1. Did you specify which character you need help with?\n2. Are you looking for general advice, character-specific advice, both?\n3. How well do you understand general game mechanics on a scale of 1-5 (1 being complete beginner and 5 being knowledgeable)?\n4. Region?\n5. What times are you available?\n\nPlease keep in mind if you are very new to the game or have a basic understanding, it is recommended to first learn more via resources like Izaw's Art of Smash series (which you can find on YouTube) or other resources we have pinned in <#739299508403437621>.")

    #links to our calendar
    @commands.command(aliases=['calender', 'calandar', 'caIendar'])
    async def calendar(self, ctx): #the basic schedule for our server
        await ctx.send("https://calendar.google.com/calendar/embed?src=ssbu.traininggrounds%40gmail.com&ctz=America%2FNew_York")

    #generic coin toss
    @commands.command()
    async def coin(self, ctx):
        coin = ['Coin toss: **Heads!**', 'Coin toss: **Tails!**']
        await ctx.send(random.choice(coin))

    #neat dice roll
    @commands.command(aliases=['r'])
    async def roll(self, ctx, dice:str):
        try:
            amount, sides = map(int, dice.split('d'))
        except:
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
            return
        results = []
        if amount > 100:
            await ctx.send("Too many dice!")
            return
        if sides > 1000:
            await ctx.send("Too many sides!")
            return
        for r in range(amount):
            x = random.randint(1, sides)
            results.append(x)
        if len(results) == 1:
            await ctx.send(f"Rolling **1**-**{sides}** \nResult: **{results}**")
        else:
            await ctx.send(f"Rolling **1**-**{sides}** **{r+1}** times \nResults: **{results}** \nTotal: **{sum(results)}**")


    @commands.command()
    async def countdown(self, ctx, count:int):
        if count > 50:
            await ctx.send("Please don't use numbers that big.")
            return
        if count < 1:
            await ctx.send("Invalid number!")
            return
        
        initial_count = count

        countdown_message = await ctx.send(f"Counting down from {initial_count}...\n{count}")

        while count > 1:
            count -= 1
            await asyncio.sleep(2) #sleeps 2 secs instead of 1
            await countdown_message.edit(content=f"Counting down from {initial_count}...\n{count}") #edits the message with the new count

        await asyncio.sleep(2) #sleeps again before sending the final message
        await countdown_message.edit(content=f"Counting down from {initial_count}...\nFinished!")


    @commands.command(aliases=['remindme'])
    async def reminder(self, ctx, time, *, remind_message):
        #this here gets the time
        if time.lower().endswith("d"):
            seconds = int(time[:-1]) * 60 * 60 * 24
            reminder_time = f"{seconds // 60 // 60 // 24} day(s)"
        elif time.lower().endswith("h"):
            seconds = int(time[:-1]) * 60 * 60
            reminder_time = f"{seconds // 60 // 60} hour(s)"
        elif time.lower().endswith("m"):
            seconds = int(time[:-1]) * 60
            reminder_time = f"{seconds // 60} minute(s)"
        elif time.lower().endswith("s"):
            seconds = int(time[:-1])
            reminder_time = f"{seconds} seconds"
        else:
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.")
            return
        
        if seconds < 30:
            await ctx.send("Duration is too short! I'm sure you can remember that yourself.")
            return
        if seconds > 2592000: #30 days
            await ctx.send("Duration is too long! Maximum duration is 30 days.")
            return

        await ctx.send(f"{ctx.author.mention}, I will remind you about {remind_message} in {reminder_time}!")

        await asyncio.sleep(seconds) #bit flawed, if i restart the bot obviously the reminders get deleted, would work better if i would store them in a json file but oh well

        await ctx.send(f"{ctx.author.mention}, you wanted me to remind you of {remind_message}, {reminder_time} ago.")


    @commands.command(aliases=['emoji'])
    async def emote(self, ctx, emoji:discord.Emoji):
        embed = discord.Embed(title="Emoji Info", colour=discord.Colour.orange(), description=f"\
**Server:** {emoji.guild} ({emoji.guild.id})\n\
**Url:** {emoji.url}\n\
**Name:** {emoji.name}\n\
**ID:** {emoji.id}\n\
            ")
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)


    @commands.command()
    async def spotify(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        if not ctx.guild:
            await ctx.send("This command does not work in my DM channel.")
            return

        listeningstatus = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)

        if listeningstatus is None:
            await ctx.send("This user is not listening to Spotify right now or their account is not connected.")
        else:
            await ctx.send(f"https://open.spotify.com/track/{listeningstatus.track_id}")



    #our streamers use these shortcuts to promote their streams
    @commands.command()
    async def streamer(self, ctx):
        await ctx.send("Streamer commands: \n%neon, %scrooge, %tabuu, %xylenes, %tgstream") #needs updating every once in a while

    @commands.command()
    async def neon(self, ctx):
        await ctx.send("https://www.twitch.tv/neonsurvivor")

    @commands.command()
    async def scrooge(self, ctx):
        await ctx.send("https://www.twitch.tv/scroogemcduk")
    
    @commands.command()
    async def tabuu(self, ctx):
        await ctx.send("https://www.twitch.tv/therealtabuu")

    @commands.command()
    async def xylenes(self, ctx):
        await ctx.send("https://www.twitch.tv/FamilyC0mputer")

    @commands.command()
    async def tgstream(self, ctx):
        await ctx.send("https://www.twitch.tv/ssbutraininggrounds")




    #error handling for the above
    @listrole.error
    async def listrole_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        raise error

    @roleinfo.error
    async def roleinfo_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        raise error
        

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        raise error

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        raise error

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a question, and then at least 2 options!")
        raise error


    @modmail.error
    async def modmail_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a message to the moderators. It should look something like:\n```%modmail (your message here)```")
        raise error

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
        raise error

    @countdown.error
    async def countdown_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a number!")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid number!")
        raise error

    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify an amount of time and the reminder message!")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.")
        raise error

    @emote.error
    async def emote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify an emoji!")
        if isinstance(error, commands.EmojiNotFound):
            await ctx.send("I couldn't find information on this emoji!")
        raise error

    @spotify.error
    async def spotify_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        raise error



def setup(bot):
    bot.add_cog(Usercommands(bot))
    print("Usercommands cog loaded")