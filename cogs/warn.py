import random
import time
from datetime import datetime

import aiosqlite
import discord
from discord.ext import commands, tasks

import utils.check
from cogs.mute import Mute
from utils.ids import AdminVars, TGChannelIDs


class Warn(commands.Cog):
    """
    Contains our custom warning system.
    """

    def __init__(self, bot):
        self.bot = bot

        self.warnloop.start()

    def cog_unload(self):
        self.warnloop.cancel()

    async def add_warn(self, author: discord.Member, member: discord.Member, reason):
        """
        Adds a warning to the database.
        Also logs it to our infraction-logs channel.
        """
        # assigning each warning a random 6 digit number, hope thats enough to not get duplicates
        warn_id = random.randint(100000, 999999)
        warndate = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """INSERT INTO warnings VALUES (:user_id, :warn_id, :mod_id, :reason, :timestamp)""",
                {
                    "user_id": member.id,
                    "warn_id": warn_id,
                    "mod_id": author.id,
                    "reason": reason,
                    "timestamp": warndate,
                },
            )
            await db.commit()

        # and this second part here logs the warn into the warning log discord channel
        channel = self.bot.get_channel(TGChannelIDs.INFRACTION_LOGS)
        embed = discord.Embed(title="⚠️New Warning⚠️", color=discord.Color.dark_red())
        embed.add_field(name="Warned User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="ID", value=warn_id, inline=True)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    async def check_warn_count(
        self, guild: discord.Guild, channel: discord.TextChannel, member: discord.Member
    ):
        """
        Checks the amount of warnings a user has and executes the according action.

        3 warnings:
            User gets muted indefinitely.
        5 warnings:
            User gets kicked from the Server.
        7 warnings:
            User gets banned from the Server.

        Also DMs them informing the User of said action.
        """

        async with aiosqlite.connect("./db/database.db") as db:
            user_warnings = await db.execute_fetchall(
                """SELECT * FROM warnings WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        warns = len(user_warnings)

        if warns > 6:
            try:
                await member.send(
                    f"You have been automatically banned from the {guild.name} Server for reaching warning #***{warns}***.\n"
                    f"Please contact {AdminVars.GROUNDS_KEEPER} for an appeal.\n{AdminVars.BAN_RECORDS}"
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic ban reason to {str(member)}, but it failed: {exc}"
                )

            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically banned."
            )
            await member.ban(reason=f"Automatic ban for reaching {warns} warnings")
        elif warns > 4:
            try:
                await member.send(
                    f"You have been automatically kicked from the {guild.name} Server for reaching warning #***{warns}***.\n"
                    f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic kick reason to {str(member)}, but it failed: {exc}"
                )

            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically kicked."
            )
            await member.kick(reason=f"Automatic kick for reaching {warns} warnings")
        elif warns > 2:
            await Mute.add_mute(self, member)
            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically muted."
            )

            try:
                await member.send(
                    f"You have been automatically muted in the {guild.name} Server for reaching warning #***{warns}***.\n"
                    f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except discord.HTTPException as exc:
                logger = self.bot.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic mute reason to {str(member)}, but it failed: {exc}"
                )

    @commands.command()
    @utils.check.is_moderator()
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Warns a user.
        """
        if member.bot:
            await ctx.send("You can't warn bots, silly.")
            return

        # adds the warning
        await self.add_warn(ctx.author, member, reason)

        # tries to dm user
        try:
            await member.send(
                f"You have been warned in the {ctx.guild.name} Server for the following reason: \n"
                f"```{reason}```\n"
                f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
            )
        except discord.HTTPException as exc:
            logger = self.bot.get_logger("bot.warn")
            logger.warning(
                f"Tried to message warn reason to {str(member)}, but it failed: {exc}"
            )

        await ctx.send(f"{member.mention} has been warned!")

        # checks warn count for further actions
        await self.check_warn_count(ctx.guild, ctx.channel, member)

    @commands.command(aliases=["warnings", "infractions"])
    async def warns(self, ctx, member: discord.Member = None):
        """
        Checks the warnings of a user, or yourself.
        """
        if member is None:
            member = ctx.author

        async with aiosqlite.connect("./db/database.db") as db:
            user_warnings = await db.execute_fetchall(
                """SELECT * FROM warnings WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        warns = len(user_warnings)

        if warns == 0:
            await ctx.send(f"{member.mention} doesn't have any warnings (yet).")
        else:
            await ctx.send(f"{member.mention} has {warns} warning(s).")

    @commands.command()
    @utils.check.is_moderator()
    async def clearwarns(self, ctx, member: discord.Member):
        """
        Deletes all warnings of a user from the database.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """DELETE FROM warnings WHERE user_id = :user_id""",
                {"user_id": member.id},
            )
            await db.commit()

        await ctx.send(f"Cleared all warnings for {member.mention}.")

    @commands.command()
    @utils.check.is_moderator()
    async def warndetails(self, ctx, member: discord.Member):
        """
        Gets you the details of a Users warnings.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            user_warnings = await db.execute_fetchall(
                """SELECT * FROM warnings WHERE user_id = :user_id""",
                {"user_id": member.id},
            )

        if len(user_warnings) == 0:
            await ctx.send(f"{member.mention} doesn't have any active warnings (yet).")
            return

        embed_list = []
        for i, warning in enumerate(user_warnings, start=1):
            # the first one is the user id, but we dont need it here
            (_, warn_id, mod_id, reason, timestamp) = warning

            new_timestamp = datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")

            embed = discord.Embed(title=f"Warning #{i}", colour=discord.Colour.red())
            embed.add_field(name="Moderator: ", value=f"<@{mod_id}>")
            embed.add_field(name="Reason: ", value=f"{reason}")
            embed.add_field(name="ID:", value=f"{warn_id}")
            embed.add_field(
                name="Warning given out at:",
                value=discord.utils.format_dt(new_timestamp, style="F"),
            )
            embed_list.append(embed)

        # the maximum amount of embeds you can send is 10,
        # we do ban people at 7 warnings but you never know what might happen
        try:
            await ctx.send(
                f"Active warnings for {member.mention}: {len(user_warnings)}",
                embeds=embed_list,
            )
        except discord.HTTPException:
            await ctx.send(
                f"Active warnings for {member.mention}: {len(user_warnings)}\nCannot list warnings for this user!"
            )

    @commands.command()
    @utils.check.is_moderator()
    async def deletewarn(self, ctx, member: discord.Member, warn_id):
        """
        Deletes a specific warning of a user, by the randomly generated warning ID.
        Use warndetails to see these warning IDs.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            warning = await db.execute_fetchall(
                """SELECT * FROM warnings WHERE user_id = :user_id AND warn_id = :warn_id""",
                {"user_id": member.id, "warn_id": warn_id},
            )

            if len(warning) == 0:
                await ctx.send(
                    f"I couldnt find a warning with the ID {warn_id} for {member.mention}."
                )
                return

            await db.execute(
                """DELETE FROM warnings WHERE user_id = :user_id AND warn_id = :warn_id""",
                {"user_id": member.id, "warn_id": warn_id},
            )
            await db.commit()

        await ctx.send(f"Deleted warning {warn_id} for {member.mention}")

    @tasks.loop(hours=24)
    async def warnloop(self):
        """
        This here checks if a warning is older than 30 days and has expired,
        if that is the case, deletes the expired warnings.
        """
        logger = self.bot.get_logger("bot.warn")

        async with aiosqlite.connect("./db/database.db") as db:
            every_warning = await db.execute_fetchall("""SELECT * FROM warnings""")

            # we check for every warning if it is older than 30 days
            for warning in every_warning:
                # the underscores are mod_id and reason
                (user_id, warn_id, _, _, timestamp) = warning
                timediff = datetime.utcnow() - datetime.strptime(
                    timestamp, "%A, %B %d %Y @ %H:%M:%S %p"
                )
                if timediff.days > 29:
                    # user id and warn id should be enough to identify each warning (hopefully)
                    await db.execute(
                        """DELETE FROM warnings WHERE user_id = :user_id AND warn_id = :warn_id""",
                        {"user_id": user_id, "warn_id": warn_id},
                    )
                    logger.info(
                        f"Deleted Warning #{warn_id} for user {user_id} after 30 days."
                    )

            await db.commit()

        logger.info("Warnloop finished.")

    @warnloop.before_loop
    async def before_warnloop(self):
        await self.bot.wait_until_ready()

    # basic error handling for the above
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a reason!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @clearwarns.error
    async def clearwarns_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @deletewarn.error
    async def deletewarn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member and specify a warn_id.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warndetails.error
    async def warndetails_error(self, ctx, error):
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Warn(bot))
    print("Warn cog loaded")
