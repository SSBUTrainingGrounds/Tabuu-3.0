import datetime
import random

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

import utils.check
from cogs.mute import Mute
from utils.ids import AdminVars, GuildIDs, TGChannelIDs


class Warn(commands.Cog):
    """Contains our custom warning system."""

    def __init__(self, bot):
        self.bot = bot

        self.warnloop.start()

    def cog_unload(self):
        self.warnloop.cancel()

    async def add_warn(
        self, author: discord.Member, member: discord.Member, reason: str
    ):
        """Adds a warning to the database.
        Also logs it to our infraction-logs channel.
        """
        # Assigning each warning a random 6 digit number, hope thats enough to not get duplicates.
        warn_id = random.randint(100000, 999999)
        warndate = int(discord.utils.utcnow().timestamp())

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

        # And this second part here logs the warn into the warning log discord channel.
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
        """Checks the amount of warnings a user has and executes the according action.

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

        if warns > 4:
            try:
                await member.send(
                    f"You have been automatically banned from the {guild.name} Server for reaching warning #***{warns}***.\n"
                    f"Check here to see the earliest you are able to appeal your ban (if at all): <{AdminVars.BAN_RECORDS}>\n\n"
                    f"Please use this form if you wish to appeal your ban: {AdminVars.APPEAL_FORM}"
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
        elif warns > 2:
            await Mute(self.bot).add_mute(member)
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

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to warn.", reason="The reason for the warning."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Warns a user."""
        if member.bot:
            await ctx.send("You can't warn bots, silly.")
            return

        await self.add_warn(ctx.author, member, reason)

        # Tries to dm user.
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

        # Checks warn count for further actions.
        await self.check_warn_count(ctx.guild, ctx.channel, member)

    @commands.hybrid_command(aliases=["warnings", "infractions"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to check the warning count of.")
    async def warns(self, ctx: commands.Context, member: discord.Member = None):
        """Checks the warning count of a user, or yourself."""
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

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to remove all warnings from.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        """Deletes all warnings of a user from the database."""
        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """DELETE FROM warnings WHERE user_id = :user_id""",
                {"user_id": member.id},
            )
            await db.commit()

        await ctx.send(f"Cleared all warnings for {member.mention}.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The member to see the warn details of.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def warndetails(self, ctx: commands.Context, user: discord.User):
        """Gets you the details of a Users warnings."""
        async with aiosqlite.connect("./db/database.db") as db:
            user_warnings = await db.execute_fetchall(
                """SELECT * FROM warnings WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        if len(user_warnings) == 0:
            await ctx.send(f"{user.mention} doesn't have any active warnings (yet).")
            return

        embed = discord.Embed(
            title=f"Active warnings for {str(user)} ({user.id}): {len(user_warnings)}",
            colour=discord.Colour.red(),
        )

        # We can add 25 warnings to the embed, you get banned at 5.
        for i, warning in enumerate(user_warnings, start=1):
            # The first one is the user id, but we dont need it here.
            (_, warn_id, mod_id, reason, timestamp) = warning
            if len(reason[150:]) > 0:
                reason = f"{reason[:147]}..."

            embed.add_field(
                name=f"#{i} - ID: {warn_id}",
                value=f"**Given by: <@{mod_id}> at <t:{timestamp}:F>\nReason:\n{reason}**",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to remove a warning of.",
        warn_id="The ID of the warning to remove.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def deletewarn(
        self, ctx: commands.Context, member: discord.Member, warn_id: str
    ):
        """Deletes a specific warning of a user, by the randomly generated warning ID.
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
        """This here checks if a warning is older than 30 days and has expired,
        if that is the case, deletes the expired warnings.
        """
        logger = self.bot.get_logger("bot.warn")

        expires_at = discord.utils.utcnow() - datetime.timedelta(days=30)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """DELETE FROM warnings WHERE timestamp < :expires_at""",
                {"expires_at": int(expires_at.timestamp())},
            )

            await db.commit()

        logger.info("Warnloop finished.")

    @warnloop.before_loop
    async def before_warnloop(self):
        await self.bot.wait_until_ready()

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
