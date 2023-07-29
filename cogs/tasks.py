import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

import utils.time
from utils.ids import GuildIDs, TGChannelIDs, TGRoleIDs, TournamentReminders


class Tasks(commands.Cog):
    """Contains tasks for weekly reminders."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.so_ping.start()
        self.tos_ping.start()
        self.dt_ping.start()
        self.lm_ping.start()

    def cog_unload(self) -> None:
        self.so_ping.cancel()
        self.tos_ping.cancel()
        self.dt_ping.cancel()
        self.lm_ping.cancel()

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
    # dt_time = datetime.time(
    #     TournamentReminders.DESIGN_TEAM_HOUR,
    #     TournamentReminders.DESIGN_TEAM_MINUTE,
    #     0,
    #     0,
    # )
    lm_time = datetime.time(
        TournamentReminders.LINK_REMINDER_HOUR,
        TournamentReminders.LINK_REMINDER_MINUTE,
        0,
        0,
    )

    @tasks.loop(time=utils.time.convert_to_utc(so_time, TournamentReminders.TIMEZONE))
    async def so_ping(self) -> None:
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

    # @tasks.loop(time=utils.time.convert_to_utc(dt_time, TournamentReminders.TIMEZONE))
    # async def dt_ping(self) -> None:
    #     if not TournamentReminders.PING_ENABLED:
    #         return

    #     if (
    #         datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
    #         == TournamentReminders.DESIGN_TEAM_DAY
    #     ) and (
    #         datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
    #         <= TournamentReminders.DESIGN_TEAM_HOUR
    #     ):
    #         guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
    #         design_channel = self.bot.get_channel(TGChannelIDs.DESIGN_TEAM)
    #         design_role = discord.utils.get(guild.roles, id=TGRoleIDs.DESIGN_TEAM_ROLE)
    #         trial_role = discord.utils.get(guild.roles, id=TGRoleIDs.TRIAL_DESIGN_ROLE)

    #         await design_channel.send(
    #             f"{design_role.mention} & {trial_role.mention} Reminder that it is time to get to work on SO/ToS graphics! "
    #             "Who is able to take one or both?\n(Assuming alts have already been collected.)"
    #         )

    @tasks.loop(time=utils.time.convert_to_utc(lm_time, TournamentReminders.TIMEZONE))
    async def lm_ping(self) -> None:
        if not TournamentReminders.PING_ENABLED:
            return

        if (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).weekday()
            == TournamentReminders.LINK_REMINDER_DAY
        ) and (
            datetime.datetime.now(ZoneInfo(TournamentReminders.TIMEZONE)).hour
            <= TournamentReminders.LINK_REMINDER_HOUR
        ):
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            design_channel = self.bot.get_channel(TGChannelIDs.TOURNAMENT_TEAM)
            tournament_role = discord.utils.get(
                guild.roles, id=TGRoleIDs.TOURNAMENT_HEAD_ROLE
            )

            await design_channel.send(
                f"{tournament_role.mention} Trials of Smash and Smash Overseas is this week! "
                "Have you posted the link in announcements?"
            )

    @so_ping.before_loop
    async def before_so_ping(self) -> None:
        await self.bot.wait_until_ready()

    @tos_ping.before_loop
    async def before_tos_ping(self) -> None:
        await self.bot.wait_until_ready()

    # @dt_ping.before_loop
    # async def before_dt_ping(self) -> None:
    #     await self.bot.wait_until_ready()

    @lm_ping.before_loop
    async def before_lm_ping(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot) -> None:
    await bot.add_cog(Tasks(bot))
    print("Tasks cog loaded")
