import datetime
from itertools import cycle
from zoneinfo import ZoneInfo

import aiosqlite
import discord
from discord.ext import commands, tasks
from stringmatch import Match

import utils.time
from utils.ids import (
    BGChannelIDs,
    BGRoleIDs,
    GuildIDs,
    TGChannelIDs,
    TGLevelRoleIDs,
    TGRoleIDs,
    TournamentReminders,
)


class Events(commands.Cog):
    """Contains the event listeners, Welcome/Booster messages,
    Autorole, Status updates, Tournament Pings and so on.
    """

    def __init__(self, bot: commands.Bot) -> None:
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

    # Status cycles through these, update these once in a while to keep it fresh.
    status = cycle(
        [
            "type {prefix}help",
            "Always watching 👀",
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
            "↑ ↑ ↓ ↓ ← → ← → B A Start",
            "{members} Members",
            "Version {version}",
        ]
    )

    @tasks.loop(seconds=600)
    async def change_status(self) -> None:
        """Changes the status every 10 Minutes."""
        await self.bot.change_presence(
            activity=discord.Game(
                next(self.status).format(
                    members=len(set(self.bot.get_all_members())),
                    version=self.bot.version_number,
                    prefix=self.bot.main_prefix,
                )
            )
        )

    @change_status.before_loop
    async def before_change_status(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        if member.guild.id == GuildIDs.TRAINING_GROUNDS:
            channel = self.bot.get_channel(TGChannelIDs.GENERAL_CHANNEL)
            rules = self.bot.get_channel(TGChannelIDs.RULES_CHANNEL)

            # Checking if the user is muted when he joins.
            if len(matching_user) != 0:
                # Getting both the cadet role and the muted role
                # since you dont really have to accept the rules if you come back muted.
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

            # If not this is the normal greeting.
            await channel.send(
                f"{member.mention} has joined the ranks! What's shaking?\n"
                f"Please take a look at the {rules.mention} channel for information about server events/functions!"
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
                f"{member.mention} has entered the battlegrounds. ⚔️\n"
                "If you are interested on getting in on some crew battle action, "
                f"head to {rules_channel.mention} to get familiar with how the server works!"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        # Adds/removes a VC role when you join/leave a VC channel.
        voice_channel = TGChannelIDs.GENERAL_VOICE_CHAT
        if (
            (before.channel is None or before.channel.id != voice_channel)
            and after.channel is not None
            and after.channel.id == voice_channel
        ):
            try:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
                await member.add_roles(vc_role)
            except discord.HTTPException:
                pass

        if (
            (after.channel is None or after.channel.id != voice_channel)
            and before.channel is not None
            and before.channel.id == voice_channel
        ):
            try:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
                await member.remove_roles(vc_role)
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        # For tracking the last 5 username updates.
        if before.name != after.name:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """INSERT INTO usernames VALUES (:user_id, :old_name, :timestamp)""",
                    {
                        "user_id": before.id,
                        "old_name": before.name,
                        "timestamp": int(discord.utils.utcnow().timestamp()),
                    },
                )

                # This will keep only the lastest 5 entries, in order to not flood the db too much.
                # I think the timestamp + user id will be enough to identify a unique entry,
                # not sure if you can even change your name twice in 1s, rate limit wise.
                await db.execute(
                    """DELETE FROM usernames WHERE user_id = :user_id AND timestamp NOT IN
                    (SELECT timestamp FROM usernames WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 5)""",
                    {"user_id": before.id},
                )

                await db.commit()

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        # For tracking the last 5 nickname updates.
        if before.display_name not in [after.display_name, before.name]:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """INSERT INTO nicknames VALUES (:user_id, :old_name, :guild_id, :timestamp)""",
                    {
                        "user_id": before.id,
                        "old_name": before.display_name,
                        "guild_id": before.guild.id,
                        "timestamp": int(discord.utils.utcnow().timestamp()),
                    },
                )

                await db.execute(
                    """DELETE FROM nicknames WHERE user_id = :user_id AND timestamp NOT IN
                    (SELECT timestamp FROM nicknames WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 5)""",
                    {"user_id": before.id},
                )

                await db.commit()

        # For announcing boosts/premium memberships.
        if len(before.roles) < len(after.roles):
            channel = self.bot.get_channel(TGChannelIDs.ANNOUNCEMENTS_CHANNEL)

            new_role = next(role for role in after.roles if role not in before.roles)

            # For a new boost.
            if new_role.id == TGRoleIDs.BOOSTER_ROLE:
                await channel.send(f"{after.mention} has boosted the server! 🥳🎉")

            # For when someone new subs to the premium thing.
            if new_role.id == TGRoleIDs.PREMIUM_ROLE:
                await channel.send(
                    f"{after.mention} is now a Premium Member of the server! 🥳🎉"
                )

        # We also take away the colour roles if you stop boosting.
        if len(before.roles) > len(after.roles):
            old_role = next(role for role in before.roles if role not in after.roles)

            if old_role.id == TGRoleIDs.BOOSTER_ROLE:
                for role in TGRoleIDs.COLOUR_ROLES:
                    try:
                        removerole = discord.utils.get(after.guild.roles, id=role)
                        if removerole in after.roles:
                            await after.remove_roles(removerole)
                    except discord.HTTPException:
                        pass

        # This here gives out the recruit role on a successful member screening,
        # on join was terrible because of the android app, for whatever reason.
        try:
            if before.bot or after.bot:
                return

            if (
                before.pending
                and not after.pending
                and before.guild.id == GuildIDs.TRAINING_GROUNDS
            ):
                cadetrole = discord.utils.get(
                    before.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE
                )
                await after.add_roles(cadetrole)
        except AttributeError:
            pass

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger = self.bot.get_logger("bot.commands")
        logger.warning(
            f"Command triggered an Error: {ctx.prefix}{ctx.invoked_with} "
            f"(invoked by {str(ctx.author)}) - Error message: {error}"
        )

        if isinstance(error, commands.CommandNotFound):
            command_list = [
                command.qualified_name for command in self.bot.walk_commands()
            ]

            async with aiosqlite.connect("./db/database.db") as db:
                all_macros = await db.execute_fetchall("""SELECT name FROM macros""")

            # Appending all macro names to the list to get those too.
            command_list.extend(m[0] for m in all_macros)

            if ctx.invoked_with in command_list:
                return

            match = Match(ignore_case=True, include_partial=True, latinise=True)
            if command_match := match.get_best_match(
                ctx.invoked_with, command_list, score=30
            ):
                await ctx.send(
                    "I could not find this command. "
                    f"Did you mean `{ctx.prefix}{command_match}`?\n"
                    f"Type `{ctx.prefix}help` for all available commands."
                )
            else:
                await ctx.send(
                    "I could not find this command.\n"
                    f"Type `{ctx.prefix}help` for all available commands."
                )
        elif ctx.command.has_error_handler() is False:
            raise error

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context) -> None:
        logger = self.bot.get_logger("bot.commands")
        logger.info(
            f"Command successfully ran: {ctx.prefix}{ctx.invoked_with} "
            f"(invoked by {str(ctx.author)})"
        )

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        self.bot.commands_ran += 1

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        logger = self.bot.get_logger("bot.app_commands")
        logger.info(
            f"Application Command successfully ran: {interaction.id} (invoked by {str(interaction.user)})"
        )
        self.bot.commands_ran += 1

    @commands.Cog.listener()
    async def on_socket_event_type(self, event_type: str) -> None:
        self.bot.events_listened_to += 1

    # These just log when the bot loses/regains connection
    @commands.Cog.listener()
    async def on_connect(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.info("Connected to discord.")

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.warning("Lost connection to discord.")

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.info("Resumed connection to discord.")

    # The times of the tournaments (or well 1 hour & 5 mins before it).
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
    async def so_ping(self) -> None:
        """This and the tos_ping tasks remind the Tournament People 1 hour before our Tournaments.
        I don't know why but we have to convert the Timezones ourselves,
        but the built-in method will not work for me.
        """
        if not TournamentReminders.PING_ENABLED:
            return

        # Runs every day, checks if it is the desired day in that timezone (utc could be off).
        # Stops this task from running the hour after the desired time in that timezone.
        # Have to do this because otherwise it would run again
        # if i were to restart the bot after the task has already been run.
        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.SMASH_OVERSEAS_DAY
        ) and (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
            <= TournamentReminders.SMASH_OVERSEAS_HOUR
        ):
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
            streamer_role = discord.utils.get(guild.roles, id=TGRoleIDs.STREAMER_ROLE)

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
    async def tos_ping(self) -> None:
        if not TournamentReminders.PING_ENABLED:
            return

        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.TRIALS_OF_SMASH_DAY
        ) and (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
            <= TournamentReminders.TRIALS_OF_SMASH_HOUR
        ):
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            streamer_channel = self.bot.get_channel(TGChannelIDs.STREAM_TEAM)
            streamer_role = discord.utils.get(guild.roles, id=TGRoleIDs.STREAMER_ROLE)

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
    async def dt_ping(self) -> None:
        if not TournamentReminders.PING_ENABLED:
            return

        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.DESIGN_TEAM_DAY
        ) and (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
            <= TournamentReminders.DESIGN_TEAM_HOUR
        ):
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            design_channel = self.bot.get_channel(TGChannelIDs.DESIGN_TEAM)
            design_role = discord.utils.get(guild.roles, id=TGRoleIDs.DESIGN_TEAM_ROLE)
            trial_role = discord.utils.get(guild.roles, id=TGRoleIDs.TRIAL_DESIGN_ROLE)

            await design_channel.send(
                f"{design_role.mention} & {trial_role.mention} Reminder that it is time to get to work on SO/ToS graphics! "
                "Who is able to take one or both?\n(Assuming alts have already been collected.)"
            )

    @so_ping.before_loop
    async def before_so_ping(self) -> None:
        await self.bot.wait_until_ready()

    @tos_ping.before_loop
    async def before_tos_ping(self) -> None:
        await self.bot.wait_until_ready()

    @dt_ping.before_loop
    async def before_dt_ping(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot) -> None:
    await bot.add_cog(Events(bot))
    print("Events cog loaded")
