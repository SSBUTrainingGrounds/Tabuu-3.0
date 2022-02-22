import discord
from discord.ext import commands, tasks
import aiosqlite
from itertools import cycle
from fuzzywuzzy import process, fuzz
import datetime
from zoneinfo import ZoneInfo
from utils.ids import (
    GuildIDs,
    TGChannelIDs,
    TGRoleIDs,
    TGLevelRoleIDs,
    BGChannelIDs,
    BGRoleIDs,
    TournamentReminders,
)
import utils.time


class Events(commands.Cog):
    """
    Contains the event listeners, Welcome/Booster messages,
    Autorole, Status updates, Tournament Pings and so on.
    """

    def __init__(self, bot):
        self.bot = bot

        self.change_status.start()
        self.so_ping.start()
        self.tos_ping.start()
        self.dt_ping.start()

    def cog_unload(self):
        self.change_status.cancel()
        self.so_ping.cancel()
        self.tos_ping.cancel()
        self.dt_ping.cancel()

    # status cycles through these, update these once in a while to keep it fresh
    status = cycle(
        [
            "type %help",
            "Always watching 👀",
            "%modmail in my DM's to contact the mod team privately",
            "What is love?",
            "Executing Plan Z.",
            "...with your heart.",
            "Harder, better, faster, stronger.",
            "Reading menu...",
            "Read the rules!",
            "I'm in your area.",
            "Join the Battlegrounds!",
            "Gambling... 🎰",
            "1% Evil, 99% Hot Gas.",
            "⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️",
            "{members} Members",
            "Version {version}",
        ]
    )

    @tasks.loop(seconds=600)
    async def change_status(self):
        """
        Changes the status every 10 Minutes.
        """
        await self.bot.change_presence(
            activity=discord.Game(
                next(self.status).format(
                    members=len(set(self.bot.get_all_members())),
                    version=self.bot.version_number,
                )
            )
        )

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        if member.guild.id == GuildIDs.TRAINING_GROUNDS:
            channel = self.bot.get_channel(TGChannelIDs.GENERAL_CHANNEL)
            rules = self.bot.get_channel(TGChannelIDs.RULES_CHANNEL)

            # checking if the user is muted when he joins
            if len(matching_user) != 0:
                # getting both the cadet role and the muted role since you dont really have to accept the rules if you come back muted
                muted_role = discord.utils.get(
                    member.guild.roles, id=TGRoleIDs.MUTED_ROLE
                )
                cadet = discord.utils.get(
                    member.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE
                )

                await member.add_roles(muted_role)
                await member.add_roles(cadet)
                await channel.send(
                    f"Welcome back, {member.mention}! You are still muted, so maybe check back later."
                )
                return

            # if not this is the normal greeting
            await channel.send(
                f"{member.mention} has joined the ranks! What's shaking?\nPlease take a look at the {rules.mention} channel for information about server events/functions!"
            )

        elif member.guild.id == GuildIDs.BATTLEGROUNDS:
            channel = self.bot.get_channel(BGChannelIDs.OFF_TOPIC_CHANNEL)
            rules_channel = self.bot.get_channel(BGChannelIDs.RULES_CHANNEL)
            traveller = discord.utils.get(
                member.guild.roles, id=BGRoleIDs.TRAVELLER_ROLE
            )

            if len(matching_user) != 0:
                muted_role = discord.utils.get(
                    member.guild.roles, id=BGRoleIDs.MUTED_ROLE
                )
                await member.add_roles(muted_role)
                await member.add_roles(traveller)
                await channel.send(
                    f"Welcome back, {member.mention}! You are still muted, so maybe check back later."
                )
                return

            await member.add_roles(traveller)
            await channel.send(
                f"{member.mention} has entered the battlegrounds. ⚔️\nIf you are interested on getting in on some crew battle action, head to {rules_channel.mention} to get familiar with how the server works!"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # adds/removes a VC role when you join/leave a VC channel
        voice_channel = TGChannelIDs.GENERAL_VOICE_CHAT
        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
        vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
        if before.channel is None or before.channel.id != voice_channel:
            if after.channel is not None and after.channel.id == voice_channel:
                try:
                    await member.add_roles(vc_role)
                except:
                    pass

        if after.channel is None or after.channel.id != voice_channel:
            if before.channel is not None and before.channel.id == voice_channel:
                try:
                    await member.remove_roles(vc_role)
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # this here announces whenever someone new boosts the server
        channel = self.bot.get_channel(TGChannelIDs.ANNOUNCEMENTS_CHANNEL)
        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles)

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

        # this here gives out the recruit role on a successful member screening, on join was terrible because of shitty android app
        try:
            if before.bot or after.bot:
                return
            else:
                if before.pending == True:
                    if after.pending == False:
                        if before.guild.id == GuildIDs.TRAINING_GROUNDS:
                            cadetrole = discord.utils.get(
                                before.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE
                            )
                            await after.add_roles(cadetrole)
        except AttributeError:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger = self.bot.get_logger("bot.commands")
        logger.warning(
            f"Command triggered an Error: %{ctx.invoked_with} (invoked by {str(ctx.author)}) - Error message: {error}"
        )

        if isinstance(error, commands.CommandNotFound):
            command_list = [command.name for command in self.bot.commands]

            async with aiosqlite.connect("./db/database.db") as db:
                all_macros = await db.execute_fetchall("""SELECT name FROM macros""")

            # appending all macro names to the list to get those too
            for m in all_macros:
                command_list.append(m[0])

            if ctx.invoked_with in command_list:
                return

            try:
                match = process.extractOne(
                    ctx.invoked_with,
                    command_list,
                    score_cutoff=30,
                    scorer=fuzz.token_set_ratio,
                )[0]
                await ctx.send(
                    f"I could not find this command. Did you mean `%{match}`?\nType `%help` for all available commands."
                )
            except TypeError:
                await ctx.send(
                    f"I could not find this command.\nType `%help` for all available commands."
                )
        else:
            if ctx.command.has_error_handler() is False:
                raise error

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logger = self.bot.get_logger("bot.commands")
        logger.info(
            f"Command successfully ran: %{ctx.invoked_with} (invoked by {str(ctx.author)})"
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.commands_ran += 1

    @commands.Cog.listener()
    async def on_socket_event_type(self, event_type):
        self.bot.events_listened_to += 1

    # these just log when the bot loses/regains connection
    @commands.Cog.listener()
    async def on_connect(self):
        logger = self.bot.get_logger("bot.connection")
        logger.info("Connected to discord.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger = self.bot.get_logger("bot.connection")
        logger.error("Lost connection to discord.")

    @commands.Cog.listener()
    async def on_resumed(self):
        logger = self.bot.get_logger("bot.connection")
        logger.info("Resumed connection to discord.")

    # the times of the tournaments (or well 1 hour & 5 mins before it)
    so_time = datetime.time(
        TournamentReminders.SMASH_OVERSEAS_HOUR,
        TournamentReminders.SMASH_OVERSEAS_MINUTE,
        0,
        0,
    )
    tos_time = datetime.time(
        TournamentReminders.TRIALS_OF_SMASH_HOUR,
        TournamentReminders.TRIALS_OF_SMASH_MINUTE,
        0,
        0,
    )
    dt_time = datetime.time(
        TournamentReminders.DESIGN_TEAM_HOUR,
        TournamentReminders.DESIGN_TEAM_MINUTE,
        0,
        0,
    )

    @tasks.loop(time=utils.time.convert_to_utc(so_time, TournamentReminders.TIMEZONE))
    async def so_ping(self):
        """
        This and the tos_ping tasks remind the Tournament People 1 hour before our Tournaments.
        I don't know why but we have to convert the Timezones ourselves, since the built-in method does not work for me.
        """
        if not TournamentReminders.PING_ENABLED:
            return

        # runs every day, checks if it is the desired day in that timezone (utc could be off)
        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.SMASH_OVERSEAS_DAY
        ):
            # stops this task from running the hour after the desired time in that timezone.
            # have to do this because otherwise it would run again if i were to restart the bot after the task has already been run
            if (
                datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
                <= TournamentReminders.SMASH_OVERSEAS_HOUR
            ):
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
                streamer_role = discord.utils.get(
                    guild.roles, id=TGRoleIDs.STREAMER_ROLE
                )

                to_channel = self.bot.get_channel(TGChannelIDs.TOURNAMENT_TEAM)
                to_role = discord.utils.get(
                    guild.roles, id=TGRoleIDs.TOURNAMENT_OFFICIAL_ROLE
                )

                await streamer_channel.send(
                    f"{streamer_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available to stream?"
                )
                await to_channel.send(
                    f"{to_role.mention} Reminder that Smash Overseas begins in 1 hour, who is available?"
                )

    @tasks.loop(time=utils.time.convert_to_utc(tos_time, TournamentReminders.TIMEZONE))
    async def tos_ping(self):
        if not TournamentReminders.PING_ENABLED:
            return

        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.TRIALS_OF_SMASH_DAY
        ):
            if (
                datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
                <= TournamentReminders.TRIALS_OF_SMASH_HOUR
            ):
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
                streamer_role = discord.utils.get(
                    guild.roles, id=TGRoleIDs.STREAMER_ROLE
                )

                to_channel = self.bot.get_channel(TGChannelIDs.TOURNAMENT_TEAM)
                to_role = discord.utils.get(
                    guild.roles, id=TGRoleIDs.TOURNAMENT_OFFICIAL_ROLE
                )

                await streamer_channel.send(
                    f"{streamer_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available to stream?"
                )
                await to_channel.send(
                    f"{to_role.mention} Reminder that Trials of Smash begins in 1 hour, who is available?"
                )

    @tasks.loop(time=utils.time.convert_to_utc(dt_time, TournamentReminders.TIMEZONE))
    async def dt_ping(self):
        """
        This pings the design team sundays to start working on the tournament graphics
        """

        if not TournamentReminders.PING_ENABLED:
            return

        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.DESIGN_TEAM_DAY
        ):
            if (
                datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
                <= TournamentReminders.DESIGN_TEAM_HOUR
            ):
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                design_channel = self.bot.get_channel(TGChannelIDs.DESIGN_TEAM)
                design_role = discord.utils.get(
                    guild.roles, id=TGRoleIDs.DESIGN_TEAM_ROLE
                )

                await design_channel.send(
                    f"{design_role.mention} Reminder that it is time to get to work on SO/ToS graphics! Who is able to take one or both?\n(Assuming alts have already been collected.)"
                )

    @so_ping.before_loop
    async def before_so_ping(self):
        await self.bot.wait_until_ready()

    @tos_ping.before_loop
    async def before_tos_ping(self):
        await self.bot.wait_until_ready()

    @dt_ping.before_loop
    async def before_dt_ping(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Events(bot))
    print("Events cog loaded")
