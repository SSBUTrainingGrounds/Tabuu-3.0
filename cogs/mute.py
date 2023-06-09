import asyncio
from datetime import datetime, timedelta

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

import utils.check
from utils.ids import AdminVars, GetIDFunctions, GuildIDs
from utils.time import convert_time


class Mute(commands.Cog):
    """Contains the custom mute system."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def add_mute(self, member: discord.Member) -> None:
        """Adds the mute entry in the database,
        and tries to add the role in both servers.
        """
        # Checks if the user is already flagged as muted in the file.
        # If not, goes ahead and adds the mute.
        # No reason to have someone in there multiple times.
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

            if len(matching_user) == 0:
                await db.execute(
                    """INSERT INTO muted VALUES (:user_id, :muted)""",
                    {"user_id": member.id, "muted": True},
                )

                await db.commit()

        # Tries to add the muted roles in each server.
        for guild_id in GuildIDs.MOD_GUILDS:
            guild = self.bot.get_guild(guild_id)
            muted_role = discord.utils.get(
                guild.roles, id=GetIDFunctions.get_muted_role(guild_id)
            )
            guild_member = guild.get_member(member.id)
            if muted_role and guild_member:
                try:
                    await guild_member.add_roles(muted_role)
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.mute")
                    logger.warning(
                        f"Tried to add muted role in {guild.name} server but it failed: {exc}"
                    )

    async def remove_mute(self, member: discord.Member) -> None:
        """Basically reverses the add_mute function.
        Removes the muted entry from the database
        and tries to remove the role in both servers.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """DELETE FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

            await db.commit()

        # Tries to remove the muted roles in each server.
        for guild_id in GuildIDs.MOD_GUILDS:
            guild = self.bot.get_guild(guild_id)
            muted_role = discord.utils.get(
                guild.roles, id=GetIDFunctions.get_muted_role(guild_id)
            )
            guild_member = guild.get_member(member.id)
            if muted_role and guild_member:
                try:
                    await guild_member.remove_roles(muted_role)
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.mute")
                    logger.warning(
                        f"Tried to remove muted role in {guild.name} server but it failed: {exc}"
                    )

    async def add_timeout(self, member: discord.Member, time: datetime) -> None:
        """Tries to add the timeout on both servers."""

        for guild_id in GuildIDs.MOD_GUILDS:
            guild = self.bot.get_guild(guild_id)
            if guild_member := guild.get_member(member.id):
                try:
                    await guild_member.edit(timed_out_until=time)
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.mute")
                    logger.warning(
                        f"Tried to add timeout in {guild.name} server but it failed: {exc}"
                    )

    async def remove_timeout(self, member: discord.Member) -> None:
        """Tries to remove the timeout on both servers."""

        for guild_id in GuildIDs.MOD_GUILDS:
            guild = self.bot.get_guild(guild_id)
            if guild_member := guild.get_member(member.id):
                try:
                    # Setting it to None will remove the timeout.
                    await guild_member.edit(timed_out_until=None)
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.mute")
                    logger.warning(
                        f"Tried to remove timeout in {guild.name} server but it failed: {exc}"
                    )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to mute.", reason="The reason for the mute."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def mute(
        self, ctx: commands.Context, member: discord.Member, *, reason: str
    ) -> None:
        """Mutes a member in all servers indefinitely.
        Also tries to DM the member the reason for the mute."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # We check again if the user is muted here because i dont want the user to get dm'd again if he already is muted.
        # Didn't wanna put a separate dm function as well because the dm's change depending on what command calls it.
        if len(matching_user) == 0:
            await self.add_mute(member)
            await ctx.send(f"{member.mention} was muted!")
            try:
                await member.send(
                    f"You have been muted in the {ctx.guild.name} Server for the following reason: \n"
                    f"```{reason}```\n"
                    f"{AdminVars.APPEAL_MESSAGE}"
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message mute reason to {str(member)}, but it failed: {exc}"
                )

        else:
            await ctx.send("This user was already muted!")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to unmute.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def unmute(self, ctx: commands.Context, member: discord.Member) -> None:
        """Unmutes a member in all servers and tries to notify them via DM."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        if len(matching_user) != 0:
            await self.remove_mute(member)
            await ctx.send(f"{member.mention} was unmuted!")
            try:
                await member.send(
                    f"You have been unmuted in the {ctx.guild.name} Server! Don't break the rules again"
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message unmute message to {str(member)}, but it failed: {exc}"
                )
        else:
            await ctx.send("This user was not muted!")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to mute.",
        mute_time="How long the mute should last.",
        reason="The reason for the mute.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def tempmute(
        self,
        ctx: commands.Context,
        member: discord.Member,
        mute_time: str,
        *,
        reason: str,
    ) -> None:
        """Mutes a member in both servers, waits for a duration and unmutes them again."""
        # Converts the input into the seconds, and also a human-readable-string.
        seconds, time_muted = convert_time(mute_time)

        if not seconds:
            raise commands.CommandInvokeError("Invalid time format!")

        if seconds <= 0:
            await ctx.send("The end of the timeout cannot be in the past.")
            return

        # This is one day.
        if seconds > 86401:
            await ctx.send("Duration is too long! Maximum duration is 1 day.")
            return

        # Now this is basically just "%mute, wait specified time, %unmute" but automated into one command.
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # The mute block from %mute, with the inclusion of time_muted.
        if len(matching_user) == 0:
            await self.add_mute(member)
            await ctx.send(f"{member.mention} was muted for *{time_muted}*!")
            try:
                await member.send(
                    f"You have been muted in the {ctx.guild.name} Server for ***{time_muted}*** for the following reason: \n"
                    f"```{reason}```\n"
                    f"{AdminVars.APPEAL_MESSAGE}"
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message temp mute reason to {str(member)}, but it failed: {exc}"
                )

        else:
            await ctx.send("This user is already muted!")
            return

        await asyncio.sleep(seconds)

        # Need to refresh the contents of the database.
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # The unmute block from %unmute,
        # no need for another unmute confirmation if the user was unmuted before manually.
        if len(matching_user) != 0:
            await self.remove_mute(member)
            await ctx.send(f"{member.mention} was automatically unmuted!")
            try:
                await member.send(
                    f"You have been automatically unmuted in the {ctx.guild.name} Server! Don't break the rules again"
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message temp unmute message to {str(member)}, but it failed: {exc}"
                )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to time out.",
        mute_time="How long the time out should last.",
        reason="The reason for the time out.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def timeout(
        self,
        ctx: commands.Context,
        member: discord.Member,
        mute_time: str,
        *,
        reason: str,
    ) -> None:
        """Times out a member for a specified amount of time.
        Very similar to the mute command, but with the built in time out function."""
        # Converts the time again, we dont need the read_time string though.
        seconds, _ = convert_time(mute_time)

        if not seconds:
            raise commands.CommandInvokeError("Invalid time format!")

        if seconds <= 0:
            await ctx.send("The end of the timeout cannot be in the past.")
            return

        if seconds > 2419199:
            await ctx.send(
                "The maximum allowed time for a timeout is just under 28 days."
            )
            return

        # Gets the time for the timeout, needs to be a dt object.
        timeout_dt = discord.utils.utcnow() + timedelta(seconds=seconds)
        # Timezone aware dt object for sending out.
        aware_dt = discord.utils.format_dt(timeout_dt, style="f")

        if member.is_timed_out():
            # If the member is already on timeout, we modify the message sent.
            if member.timed_out_until < timeout_dt:
                message = (
                    f"The timeout of {member.mention} got prolonged until {aware_dt}."
                )
            else:
                message = (
                    f"The timeout of {member.mention} got shortened until {aware_dt}."
                )
        else:
            message = f"{member.mention} is on timeout until {aware_dt}."

        await self.add_timeout(member, timeout_dt)

        try:
            await member.send(
                f"You are on timeout in the {ctx.guild.name} Server until {aware_dt} for the following reason: \n"
                f"```{reason}```\n"
                f"{AdminVars.APPEAL_MESSAGE}"
            )
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to message timeout message to {str(member)}, but it failed: {exc}"
            )

        await ctx.send(message)

    @commands.hybrid_command(aliases=["untimeout"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to remove the time out from.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def removetimeout(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        """Removes a timeout from a member."""
        # We check first if the member is on timeout.
        if not member.is_timed_out():
            await ctx.send(f"{member.mention} is not on timeout!")
            return

        await self.remove_timeout(member)

        try:
            await member.send(
                f"Your timeout has been manually removed in the {ctx.guild.name} Server! Don't break the rules again"
            )
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to message remove timeout message to {str(member)}, but it failed: {exc}"
            )

        await ctx.send(f"Removed the timeout of {member.mention}")

    @tempmute.error
    async def tempmute_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds."
            )

    @timeout.error
    async def timeout_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Something went wrong! Either you used an invalid time format or I don't have the required permissons! "
                "Try using a number followed by d/h/m/s for days/hours/minutes/seconds."
            )


async def setup(bot) -> None:
    await bot.add_cog(Mute(bot))
    print("Mute cog loaded")
