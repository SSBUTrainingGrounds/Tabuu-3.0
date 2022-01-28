import discord
from discord.ext import commands, tasks
import json
from itertools import cycle
from fuzzywuzzy import process, fuzz
import datetime
from utils.ids import GuildIDs, TGChannelIDs, TGRoleIDs, TGLevelRoleIDs, BGChannelIDs, BGRoleIDs
import utils.logger


#
#this file here contains our event listeners, the welcome/booster messages, autorole and status updates
#

#status cycles through these, update these once in a while to keep it fresh
status = cycle(["type %help",
"Always watching 👀",
"%modmail in my DM's to contact the mod team privately",
"What is love?",
"Harder, better, faster, stronger",
"Reading menu..."])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.change_status.start()
        self.so_ping.start()
        self.tos_ping.start()
        
    #stops the tasks on cog unload, so that they wont get executed multiple times
    def cog_unload(self):
        self.change_status.cancel()
        self.so_ping.cancel()
        self.tos_ping.cancel()


    #changes the status every now and then
    @tasks.loop(seconds=300)
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(next(status)))

    #need to wait until the bot is ready
    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()

    

    #member join msg
    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open(r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)

        if member.guild.id == GuildIDs.TRAINING_GROUNDS:
            channel = self.bot.get_channel(TGChannelIDs.GENERAL_CHANNEL) #ssbutg general: 739299507937738849
            rules = self.bot.get_channel(TGChannelIDs.RULES_CHANNEL) #rules-and-info channel on ssbutg

            #checking if the user is muted when he joins
            if f'{member.id}' in muted_users:
                #getting both the cadet role and the muted role since you dont really have to accept the rules if you come back muted
                muted_role = discord.utils.get(member.guild.roles, id=TGRoleIDs.MUTED_ROLE)
                cadet = discord.utils.get(member.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)

                await member.add_roles(muted_role)
                await member.add_roles(cadet)
                await channel.send(f"Welcome back, {member.mention}! You are still muted, so maybe check back later.")
                return

            #if not this is the normal greeting
            await channel.send(f"{member.mention} has joined the ranks! What's shaking?\nPlease take a look at the {rules.mention} channel for information about server events/functions!")

        elif member.guild.id == GuildIDs.BATTLEGROUNDS:
            channel = self.bot.get_channel(BGChannelIDs.OFF_TOPIC_CHANNEL)
            rules_channel = self.bot.get_channel(BGChannelIDs.RULES_CHANNEL)
            traveller = discord.utils.get(member.guild.roles, id=BGRoleIDs.TRAVELLER_ROLE)

            if f'{member.id}' in muted_users:
                muted_role = discord.utils.get(member.guild.roles, id=BGRoleIDs.MUTED_ROLE)
                await member.add_roles(muted_role)
                await member.add_roles(traveller)
                await channel.send(f"Welcome back, {member.mention}! You are still muted, so maybe check back later.")
                return
            
            await member.add_roles(traveller)
            await channel.send(f"{member.mention} has entered the battlegrounds. ⚔️\nIf you are interested on getting in on some crew battle action, head to {rules_channel.mention} to get familiar with how the server works!")


    #if you join a voice channel, you get this role here
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_channel = TGChannelIDs.GENERAL_VOICE_CHAT
        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
        vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
        if before.channel is None or before.channel.id != voice_channel:
            if after.channel is not None and after.channel.id == voice_channel:
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
        channel = self.bot.get_channel(TGChannelIDs.ANNOUNCEMENTS_CHANNEL)
        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles) #gets the new role

            if newRole.id == TGRoleIDs.BOOSTER_ROLE:
                await channel.send(f"{after.mention} has boosted the server!🥳🎉")


        if len(before.roles) > len(after.roles):
            oldRole = next(role for role in before.roles if role not in after.roles)

            if oldRole.id == TGRoleIDs.BOOSTER_ROLE:
                for role in TGRoleIDs.COLOUR_ROLES:
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
                        if before.guild.id == GuildIDs.TRAINING_GROUNDS:
                            cadetrole = discord.utils.get(before.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)
                            await after.add_roles(cadetrole)
        except AttributeError:
            pass



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger = utils.logger.get_logger("bot.commands")
        logger.warning(f"Command triggered an Error: %{ctx.invoked_with} (invoked by {str(ctx.author)}) - Error message: {error}")

        if isinstance(error, commands.CommandNotFound):
            command_list = [command.name for command in self.bot.commands]

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

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logger = utils.logger.get_logger("bot.commands")
        logger.info(f"Command successfully ran: %{ctx.invoked_with} (invoked by {str(ctx.author)})")

    
    #these just log when the bot loses/regains connection
    @commands.Cog.listener()
    async def on_connect(self):
        logger = utils.logger.get_logger("bot.connection")
        logger.info("Connected to discord.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger = utils.logger.get_logger("bot.connection")
        logger.error("Lost connection to discord.")

    @commands.Cog.listener()
    async def on_resumed(self):
        logger = utils.logger.get_logger("bot.connection")
        logger.info("Resumed connection to discord.")



    #this here pings the streamers and TOs 1 hour before each weekly tournament
    #when DST is in effect (summer), the values should be: smash overseas: (17, 0, 0, 0) and trials of smash: (22, 0, 0, 0)
    #without DST in effect (winter), the values should be: smash overseas: (18, 0, 0, 0) and trials of smash: (23, 0, 0, 0)
    #there seems to be no good way to do this since time objects do not support timezones with DST?
    so_time = datetime.time(18, 0, 0, 0)
    tos_time = datetime.time(23, 0, 0, 0)

    @tasks.loop(time=so_time)
    async def so_ping(self):
        #runs every day, checks if it is friday in utc
        if datetime.datetime.utcnow().weekday() == 4:
            #stops this task from running 1 hour after the desired time. 
            #have to do this because otherwise it would run again if i were to restart the bot after 19:00 utc fridays
            if datetime.datetime.utcnow().hour <= 18:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
                streamer_role = discord.utils.get(guild.roles, id=TGRoleIDs.STREAMER_ROLE)

                to_channel = self.bot.get_channel(TGChannelIDs.TOURNAMENT_TEAM)
                to_role = discord.utils.get(guild.roles, id=TGRoleIDs.TOURNAMENT_OFFICIAL_ROLE)

                await streamer_channel.send(f"{streamer_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available to stream?")
                await to_channel.send(f"{to_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available?")

    @tasks.loop(time=tos_time)
    async def tos_ping(self):
        #runs every day, checks if it is saturday in utc (might wanna keep watching that event cause timezones could be weird here since its sunday for me)
        if datetime.datetime.utcnow().weekday() == 5:
            if datetime.datetime.utcnow().hour <= 23:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
                streamer_role = discord.utils.get(guild.roles, id=TGRoleIDs.STREAMER_ROLE)

                to_channel = self.bot.get_channel(TGChannelIDs.TOURNAMENT_TEAM)
                to_role = discord.utils.get(guild.roles, id=TGRoleIDs.TOURNAMENT_OFFICIAL_ROLE)

                await streamer_channel.send(f"{streamer_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available to stream?")
                await to_channel.send(f"{to_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available?")

    @so_ping.before_loop
    async def before_so_ping(self):
        await self.bot.wait_until_ready()

    @tos_ping.before_loop
    async def before_tos_ping(self):
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(Events(bot))
    print("Events cog loaded")