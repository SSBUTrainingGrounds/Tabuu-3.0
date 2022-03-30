import asyncio
from datetime import datetime, timedelta

import aiosqlite
import discord
from discord.ext import commands

import utils.check
from utils.ids import AdminVars, BGRoleIDs, GuildIDs, GuildNames, TGRoleIDs
from utils.time import convert_time


class Mute(commands.Cog):
    """
    Contains the custom mute system for both of our servers.
    """

    def __init__(self, bot):
        self.bot = bot

    async def add_mute(self, member: discord.Member):
        """
        Adds the mute entry in the database,
        and tries to add the role in both servers.
        """
        # checks if the user is already flagged as muted in the file
        # if not, goes ahead and adds the mute.
        # no reason to have someone in there multiple times
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

        # first we add the mute on the tg server, or try to
        try:
            tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            tg_role = discord.utils.get(tg_guild.roles, id=TGRoleIDs.MUTED_ROLE)
            tg_member = tg_guild.get_member(member.id)
            await tg_member.add_roles(tg_role)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to add muted role in {GuildNames.TG} server but it failed: {exc}"
            )

        # then we add the mute on the bg server, or try to
        try:
            bg_guild = self.bot.get_guild(GuildIDs.BATTLEGROUNDS)
            bg_role = discord.utils.get(bg_guild.roles, id=BGRoleIDs.MUTED_ROLE)
            bg_member = bg_guild.get_member(member.id)
            await bg_member.add_roles(bg_role)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to add muted role in {GuildNames.BG} server but it failed: {exc}"
            )

    async def remove_mute(self, member: discord.Member):
        """
        Basically reverses the add_mute function.
        Removes the muted entry from the database
        and tries to remove the role in both servers.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """DELETE FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

            await db.commit()

        try:
            tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            tg_role = discord.utils.get(tg_guild.roles, id=TGRoleIDs.MUTED_ROLE)
            tg_member = tg_guild.get_member(member.id)
            await tg_member.remove_roles(tg_role)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to remove muted role in {GuildNames.TG} server but it failed: {exc}"
            )

        try:
            bg_guild = self.bot.get_guild(GuildIDs.BATTLEGROUNDS)
            bg_role = discord.utils.get(bg_guild.roles, id=BGRoleIDs.MUTED_ROLE)
            bg_member = bg_guild.get_member(member.id)
            await bg_member.remove_roles(bg_role)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to remove muted role in {GuildNames.BG} server but it failed: {exc}"
            )

    async def add_timeout(self, member: discord.Member, time: datetime):
        """
        Tries to add the timeout on both servers.
        """
        try:
            tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            tg_member = tg_guild.get_member(member.id)
            await tg_member.edit(timed_out_until=time)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to add timeout in {GuildNames.TG} server but it failed: {exc}"
            )

        try:
            bg_guild = self.bot.get_guild(GuildIDs.BATTLEGROUNDS)
            bg_member = bg_guild.get_member(member.id)
            await bg_member.edit(timed_out_until=time)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to add timeout in {GuildNames.BG} server but it failed: {exc}"
            )

    async def remove_timeout(self, member: discord.Member):
        """
        Tries to remove the timeout on both servers.
        """
        try:
            tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            tg_member = tg_guild.get_member(member.id)
            # setting it to None will remove the timeout
            await tg_member.edit(timed_out_until=None)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to remove timeout in {GuildNames.TG} server but it failed: {exc}"
            )

        try:
            bg_guild = self.bot.get_guild(GuildIDs.BATTLEGROUNDS)
            bg_member = bg_guild.get_member(member.id)
            await bg_member.edit(timed_out_until=None)
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to remove timeout in {GuildNames.BG} server but it failed: {exc}"
            )

    @commands.command()
    @utils.check.is_moderator()
    async def mute(self, ctx, member: discord.Member, *, reason):
        """
        Mutes a member in both servers indefinitely and DMs them the reason for it.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # we check again if the user is muted here because i dont want the user to get dm'd again if he already is muted
        # didn't wanna put a separate dm function as well because the dm's change depending on what command calls it
        if len(matching_user) == 0:
            await self.add_mute(member)
            await ctx.send(f"{member.mention} was muted!")
            try:
                await member.send(
                    f"You have been muted in the {ctx.guild.name} Server for the following reason: \n"
                    f"```{reason}```\n"
                    f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message mute reason to {str(member)}, but it failed: {exc}"
                )

        else:
            await ctx.send("This user was already muted!")

    @commands.command()
    @utils.check.is_moderator()
    async def unmute(self, ctx, member: discord.Member):
        """
        Unmutes a member in both servers and notifies them via DM.
        """
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

    @commands.command()
    @utils.check.is_moderator()
    async def tempmute(self, ctx, member: discord.Member, mute_time, *, reason):
        """
        Mutes a member in both servers, waits the specified time and unmutes them again.
        """
        # converts the input into the seconds, and also a human-readable-string
        seconds, time_muted = convert_time(mute_time)

        # just checking the duration is not at a crazy high/low value
        if seconds < 30:
            await ctx.send("Duration is too short! Minimum duration is 30 seconds.")
            return

        if seconds > 86401:
            await ctx.send("Duration is too long! Maximum duration is 1 day.")
            return

        # now this is basically just "%mute, wait specified time, %unmute" but automated into one command
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # the mute block from %mute, with the inclusion of time_muted
        if len(matching_user) == 0:
            await self.add_mute(member)
            await ctx.send(f"{member.mention} was muted for *{time_muted}*!")
            try:
                await member.send(
                    f"You have been muted in the {ctx.guild.name} Server for ***{time_muted}*** for the following reason: \n"
                    f"```{reason}```\n"
                    f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.mute")
                logger.warning(
                    f"Tried to message temp mute reason to {str(member)}, but it failed: {exc}"
                )

        else:
            await ctx.send("This user is already muted!")
            return

        # waits the specified time
        await asyncio.sleep(seconds)

        # need to refresh the contents of the database
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        # the unmute block from %unmute,
        # no need for another unmute confirmation if the user was unmuted before manually
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

    @commands.command()
    @utils.check.is_moderator()
    async def timeout(self, ctx, member: discord.Member, mute_time, *, reason):
        """
        Times out a member with the built in timeout function.
        Specify a time and a reason.
        The reason will get DM'd to the member.
        """
        # converts the time again, we dont need the read_time string though
        seconds, _ = convert_time(mute_time)
        if seconds > 2419199:
            await ctx.send(
                "The maximum allowed time for a timeout is just under 28 days."
            )
            return

        # gets the time for the timeout, needs to be a dt object
        timeout_dt = discord.utils.utcnow() + timedelta(seconds=seconds)
        # timezone aware dt object for sending out
        aware_dt = discord.utils.format_dt(timeout_dt, style="f")

        if member.is_timed_out():
            # if the member is already on timeout, we modify the message sent
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
                f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
            )
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.mute")
            logger.warning(
                f"Tried to message timeout message to {str(member)}, but it failed: {exc}"
            )

        await ctx.send(message)

    @commands.command(aliases=["untimeout"])
    @utils.check.is_moderator()
    async def removetimeout(self, ctx, member: discord.Member):
        """
        Removes a timeout from a member and notifies the member.
        """
        # we check first if the member is on timeout
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

    # error handling for the mute commands
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a reason for the mute!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @tempmute.error
    async def tempmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You need to mention a member, an amount of time, and a reason!"
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds."
            )
        else:
            raise error

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a member, a timeout length and a reason!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "Something went wrong! Either you used an invalid time format or I don't have the required permissons! "
                "Try using a number followed by d/h/m/s for days/hours/minutes/seconds."
            )
        else:
            raise error

    @removetimeout.error
    async def removetimeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Mute(bot))
    print("Mute cog loaded")
