import discord
from discord.ext import commands, tasks
import json
from itertools import cycle
from fuzzywuzzy import process, fuzz
import datetime


#
#this file here contains our event listeners, the welcome/booster messages, autorole and status updates
#

#status cycles through these, update these once in a while to keep it fresh
status = cycle(["type %help",
"Always watching 👀",
"Use the %modmail command in my DM's to privately contact the moderator team",
"What is love?",
"Harder, better, faster, stronger"])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self): #the pylint below is required, so that we dont get a false error
        self.change_status.start() #pylint: disable=no-member
        self.so_ping.start()
        self.tos_ping.start()
        
    @tasks.loop(seconds=300) #the status loop, every 5 mins, could maybe increase it further
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(next(status)))

    
    
    #member join msg
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(739299507937738849) #ssbutg general: 739299507937738849
        rules = self.bot.get_channel(739299507937738843) #rules-and-info channel on ssbutg

        with open(r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)  

        #checking if the user is muted when he joins
        if f'{member.id}' in muted_users:
            #getting both the cadet role too since you dont really have to accept the rules if you come back muted
            muted_role = discord.utils.get(member.guild.roles, id=739391329779581008)
            cadet = discord.utils.get(member.guild.roles, id=739299507799326843)

            await member.add_roles(muted_role)
            await member.add_roles(cadet)
            await channel.send(f"Welcome back, {member.mention}! You are still muted, so maybe check back later.")
            return

        #if not this is the normal greeting
        await channel.send(f"{member.mention} has joined the ranks! What's shaking?\nPlease take a look at the {rules.mention} channel for information about server events/functions!")


    #if you join a voice channel, you get this role here
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_channel = 765625841861394442
        guild = self.bot.get_guild(739299507795132486)
        vc_role = discord.utils.get(guild.roles, id=824258210101198889)
        if before.channel is None or before.channel.id != voice_channel:
            if after.channel is not None and after.channel.id == voice_channel: #have to do the not None thing in both occasions, otherwise the console gets flooded with errors
                try:
                    await member.add_roles(vc_role)
                except:
                    pass

        #and if you leave, the role gets removed
        if after.channel is None or after.channel.id != voice_channel:
            if before.channel is not None and before.channel.id == voice_channel:
                try:
                    await member.remove_roles(vc_role)
                except:
                    pass




    #if a new booster boosts the server, checks role changes
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(739299507937738844) #ssbutg announcements channel: 739299507937738844 
        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles) #gets the new role

            if newRole.id == 739344833738571868: #checks if its the booster role
                await channel.send(f"{after.mention} has boosted the server!🥳🎉")


        if len(before.roles) > len(after.roles): #if you stop boosting, your color roles get removed
            color_roles = (774290821842862120, 774290823340359721, 774290825927458816, 774290826896605184, 774290829128105984, 774290831271002164, 794726232616206378, 794726234231013437, 794726235518795797)
            oldRole = next(role for role in before.roles if role not in after.roles) #gets the removed role

            if oldRole.id == 739344833738571868: #if its the booster role, all of the above color roles will get removed
                for role in color_roles:
                    try:
                        removerole = discord.utils.get(after.guild.roles, id=role)
                        if removerole in after.roles:
                            await after.remove_roles(removerole)
                    except:
                        pass
        
        #this here gives out the cadet role on a successful member screening, on join was terrible because of shitty android app
        try:
            if before.bot or after.bot:
                return
            else:
                if before.pending == True:
                    if after.pending == False:
                        cadetrole = discord.utils.get(before.guild.roles, id=739299507799326843)
                        await after.add_roles(cadetrole)
        except AttributeError:
            pass


    #general error if the bot didnt find the command specified, searches for the closest match
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            command_list = [command.name for command in self.bot.commands] #every command registered. note that this will not include aliases

            #makes sure the macros are in that list as well
            with open(r'./json/macros.json', 'r') as f:
                macros = json.load(f)
            for name in macros:
                command_list.append(name)
            
            if ctx.invoked_with in command_list:
                return

            try:
                match = process.extractOne(ctx.invoked_with, command_list, score_cutoff=30, scorer=fuzz.token_set_ratio)[0]
                await ctx.send(f"I could not find this command. Did you mean `%{match}`?\nType `%help` for all available commands.")
            except TypeError:
                await ctx.send(f"I could not find this command.\nType `%help` for all available commands.")
        else:
            if ctx.command.has_error_handler() is False:
                raise error


    #this here pings the streamers and TOs 1 hour before each weekly tournament, times are in utc
    so_time = datetime.time(18, 0, 0, 0)
    tos_time = datetime.time(23, 0, 0, 0)

    @tasks.loop(time=so_time)
    async def so_ping(self):
        #runs every day, checks if it is friday in utc
        if datetime.datetime.utcnow().weekday() == 4:
            guild = self.bot.get_guild(739299507795132486)
            streamer_channel = self.bot.get_channel(766721811962396672)
            streamer_role = discord.utils.get(guild.roles, id=752291084058755192)

            to_channel = self.bot.get_channel(812433498013958205)
            to_role = discord.utils.get(guild.roles, id=739299507816366104)

            await streamer_channel.send(f"{streamer_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available to stream?")
            await to_channel.send(f"{to_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available?")

    @tasks.loop(time=tos_time)
    async def tos_ping(self):
        #runs every day, checks if it is saturday in utc (might wanna keep watching that event cause timezones could be weird here since its sunday for me)
        if datetime.datetime.utcnow().weekday() == 5:
            guild = self.bot.get_guild(739299507795132486)
            streamer_channel = self.bot.get_channel(766721811962396672)
            streamer_role = discord.utils.get(guild.roles, id=752291084058755192)

            to_channel = self.bot.get_channel(812433498013958205)
            to_role = discord.utils.get(guild.roles, id=739299507816366104)

            await streamer_channel.send(f"{streamer_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available to stream?")
            await to_channel.send(f"{to_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available?")



def setup(bot):
    bot.add_cog(Events(bot))
    print("Events cog loaded")