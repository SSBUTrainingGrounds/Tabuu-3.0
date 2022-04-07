import datetime
import os
import platform
import time

import aiosqlite
import discord
import psutil
from discord.ext import commands

import utils.check
from utils.ids import GuildIDs, TGRoleIDs
from utils.role import search_role


class Stats(commands.Cog):
    """
    Contains commands vaguely related to statistics.
    User stats, Bot stats, Server stats, Role stats, you name it.
    """

    def __init__(self, bot):
        self.bot = bot

    async def new_profile(self, user: discord.User):
        """
        Creates a new userbadges profile entry, if the user is not found in the database.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            matching_users = await db.execute_fetchall(
                """SELECT * FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            if len(matching_users) != 0:
                return

            await db.execute(
                """INSERT INTO userbadges VALUES (:user_id, :badges)""",
                {"user_id": user.id, "badges": ""},
            )

            await db.commit()

    @commands.command(aliases=["addbadge"])
    @utils.check.is_moderator()
    async def addbadges(self, ctx, user: discord.User, *badge_list):
        """
        Adds multiple emoji badges to a user.
        Emojis must be a default emoji or a custom emoji the bot can use.
        """
        if not badge_list:
            await ctx.send("Please specify the badge(s) you want to add.")
            return

        for badge in badge_list:
            try:
                await ctx.message.add_reaction(badge)
            except discord.errors.HTTPException:
                await ctx.send("Please use only valid emojis as badges!")
                return

        await self.new_profile(user)

        added_badges = []

        async with aiosqlite.connect("./db/database.db") as db:
            badges = await db.execute_fetchall(
                """SELECT badges FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            badges = badges[0][0].split(" ")

            added_badges.extend(badge for badge in badge_list if badge not in badges)
            badges = badges + added_badges

            badges = " ".join(badges)

            await db.execute(
                """UPDATE userbadges SET badges = :badges WHERE user_id = :user_id""",
                {"badges": badges, "user_id": user.id},
            )

            await db.commit()

        await ctx.send(f"Added badge(s) {' '.join(added_badges)} to {user.mention}.")

    @commands.command(aliases=["removebadges"])
    @utils.check.is_moderator()
    async def removebadge(self, ctx, user: discord.User, badge):
        """
        Removes a badge from a user.
        """
        # no emoji check here, since the bot could lose access in the meantime

        async with aiosqlite.connect("./db/database.db") as db:
            matching_users = await db.execute_fetchall(
                """SELECT * FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            if len(matching_users) == 0:
                await ctx.send("This user did not have any badges.")
                return

            badges = await db.execute_fetchall(
                """SELECT badges FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            badges = badges[0][0].split(" ")

            if badge not in badges:
                await ctx.send("This user did not have this badge.")
                return

            badges.remove(badge)

            badges = " ".join(badges)

            await db.execute(
                """UPDATE userbadges SET badges = :badges WHERE user_id = :user_id""",
                {"badges": badges, "user_id": user.id},
            )

            await db.commit()

        await ctx.send(f"Removed badge {badge} from {user.mention}.")

    @commands.command()
    @utils.check.is_moderator()
    async def clearbadges(self, ctx, user: discord.User):
        """
        Removes all badges from a user.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            matching_users = await db.execute_fetchall(
                """SELECT * FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            if len(matching_users) == 0:
                await ctx.send("This user did not have any badges.")
                return

            await db.execute(
                """DELETE FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            await db.commit()

        await ctx.send(f"Cleared all badges from {user.mention}.")

    @commands.command(aliases=["user", "user-info", "info"])
    async def userinfo(self, ctx, member: discord.Member = None):
        """
        Some information about a given user, or yourself.
        """
        if member is None:
            member = ctx.author

        try:
            activity = member.activity.name
        except AttributeError:
            activity = "None"

        if not ctx.guild:
            await ctx.send("This command is only available on servers.")
            return

        sorted_members = sorted(ctx.guild.members, key=lambda x: x.joined_at)
        index = sorted_members.index(member)

        async with aiosqlite.connect("./db/database.db") as db:
            badges = await db.execute_fetchall(
                """SELECT badges FROM userbadges WHERE :user_id = user_id""",
                {"user_id": member.id},
            )

        badges = "None" if len(badges) == 0 or badges[0][0] == "" else badges[0][0]

        embed = discord.Embed(
            title=f"Userinfo of {member.name}#{member.discriminator} ({member.id})",
            color=member.top_role.color,
        )
        embed.add_field(name="Name:", value=member.mention, inline=True)
        embed.add_field(name="Top Role:", value=member.top_role.mention, inline=True)
        embed.add_field(
            # gives the number of roles to prevent listing like 35 roles, -1 for the @everyone role
            name="Number of Roles:",
            value=f"{(len(member.roles)-1)}",
            inline=True,
        )
        embed.add_field(
            # timezone aware datetime object, F is long formatting
            name="Joined Server on:",
            value=discord.utils.format_dt(member.joined_at, style="F"),
            inline=True,
        )
        embed.add_field(
            name="Join Rank:",
            value=f"{(index+1)}/{len(ctx.guild.members)}",
            inline=True,
        )
        embed.add_field(
            name="Joined Discord on:",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=True,
        )
        embed.add_field(name="Online Status:", value=member.status, inline=True)
        embed.add_field(name="Activity Status:", value=activity, inline=True)
        embed.add_field(name="Badges:", value=badges)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["role"])
    async def roleinfo(self, ctx, *, input_role):
        """
        Basic information about a given role.
        """
        role = search_role(ctx.guild, input_role)

        embed = discord.Embed(
            title=f"Roleinfo of {role.name} ({role.id})", color=role.colour
        )
        embed.add_field(name="Role Name:", value=role.mention, inline=True)
        embed.add_field(name="Users with role:", value=len(role.members), inline=True)
        embed.add_field(
            name="Created at:",
            value=discord.utils.format_dt(role.created_at, style="F"),
        )
        embed.add_field(name="Mentionable:", value=role.mentionable, inline=True)
        embed.add_field(name="Displayed Seperately:", value=role.hoist, inline=True)
        embed.add_field(name="Color:", value=role.color, inline=True)

        if role.display_icon:
            # the display_icon could be an asset or a default emoji with the str type, so we have to check
            # if its an asset, we display it in the thumbnail
            if isinstance(role.display_icon, discord.asset.Asset):
                embed.set_thumbnail(url=role.display_icon.url)
            # if its an emoji we add it as the 2nd field
            elif isinstance(role.display_icon, str):
                embed.insert_field_at(
                    1, name="Role Emoji:", value=role.display_icon, inline=True
                )

        await ctx.send(embed=embed)

    @commands.command(aliases=["listroles"])
    async def listrole(self, ctx, *, input_role):
        """
        Lists every member of a role.
        Well up to 60 members at least.
        """
        role = search_role(ctx.guild, input_role)

        members = role.members
        if len(members) > 60:
            await ctx.send(
                f"Users with the {role} role ({len(role.members)}):\n`Too many users to list!`"
            )
            return
        if len(members) == 0:
            await ctx.send(f"No user currently has the {role} role!")
            return

        memberlist = [
            f"{discord.utils.escape_markdown(member.name)}#{member.discriminator}"
            for member in members
        ]

        all_members = ", ".join(memberlist)

        await ctx.send(
            f"Users with the {role} role ({len(role.members)}):\n{all_members}"
        )

    @commands.command(aliases=["serverinfo"])
    async def server(self, ctx):
        """
        Various information about the server.
        """
        if not ctx.guild:
            await ctx.send("This command is only available on servers.")
            return

        invites = await ctx.guild.invites()

        ssbu_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
        staff_role = discord.utils.get(ssbu_guild.roles, id=TGRoleIDs.MOD_ROLE)
        staff_online = [
            member
            for member in staff_role.members
            if member.status != discord.Status.offline
        ]

        embed = discord.Embed(
            title=f"{ctx.guild.name} ({ctx.guild.id})", color=discord.Color.green()
        )
        embed.add_field(
            name="Created on:",
            value=discord.utils.format_dt(ctx.guild.created_at, style="F"),
            inline=True,
        )
        embed.add_field(name="Owner:", value=ctx.guild.owner.mention, inline=True)
        embed.add_field(name="Staff Online:", value=len(staff_online), inline=True)

        embed.add_field(
            name="Members:",
            value=f"{len(ctx.guild.members)} (Bots: {sum(member.bot for member in ctx.guild.members)})",
            inline=True,
        )
        embed.add_field(
            name="Boosts:",
            value=f"{ctx.guild.premium_subscription_count} (Boosters: {len(ctx.guild.premium_subscribers)})",
            inline=True,
        )
        embed.add_field(name="Active Invites:", value=len(invites), inline=True)

        embed.add_field(name="Roles:", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Emojis:", value=f"{len(ctx.guild.emojis)}", inline=True)
        embed.add_field(
            name="Stickers:", value=f"{len(ctx.guild.stickers)}", inline=True
        )

        embed.add_field(
            name="Text Channels:", value=len(ctx.guild.text_channels), inline=True
        )
        embed.add_field(
            name="Voice Channels:", value=len(ctx.guild.voice_channels), inline=True
        )
        embed.add_field(
            name="Active Threads:", value=len(ctx.guild.threads), inline=True
        )

        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["botstats"])
    async def stats(self, ctx):
        """
        Statistics and information about this bot.
        """
        proc = psutil.Process(os.getpid())
        uptime_seconds = time.time() - proc.create_time()

        # they return byte values but we want gigabytes
        ram_used = round(psutil.virtual_memory()[3] / (1024 * 1024 * 1024), 2)
        ram_total = round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)
        ram_percent = round((ram_used / ram_total) * 100, 1)

        async with aiosqlite.connect("./db/database.db") as db:
            macro_list = await db.execute_fetchall("""SELECT name FROM macros""")

        # adds all type of app commands together
        all_app_commands = (
            self.bot.tree.get_commands(type=discord.AppCommandType(1))
            + self.bot.tree.get_commands(type=discord.AppCommandType(2))
            + self.bot.tree.get_commands(type=discord.AppCommandType(3)),
        )

        # we use codeblocks with yml syntax highlighting
        # just cause it looks nice, in my opinion.
        # well at least on desktop.
        bot_description = f"""
```yml
Servers: {len(self.bot.guilds)}
Total Users: {len(set(self.bot.get_all_members()))}
Latency: {round(self.bot.latency * 1000)}ms
Uptime: {str(datetime.timedelta(seconds=uptime_seconds)).split('.', maxsplit=1)[0]}
```
        """

        software_description = f"""
```yml
Tabuu 3.0: {self.bot.version_number}
Python: {platform.python_version()}
discord.py: {discord.__version__}
```
        """

        hardware_description = f"""
```yml
CPU Usage: {psutil.cpu_percent(interval=None)}%
CPU Frequency: {round(psutil.cpu_freq()[0])} MHz
RAM Usage: {ram_used}GB/{ram_total}GB ({ram_percent}%)
```
        """

        listeners_description = f"""
```yml
Number of Message Commands: {(len(self.bot.commands) + len(macro_list))}
Number of Application Commands: {len(all_app_commands)}
Number of Events: {len(self.bot.extra_events)}
```
        """

        interactions_description = f"""
```yml
Commands executed: {(self.bot.commands_ran + 1)}
Events parsed: {self.bot.events_listened_to}
```
        """

        embed = discord.Embed(
            title="Tabuu 3.0 Stats",
            color=0x007377,
            url="https://github.com/atomflunder/Tabuu-3.0-Bot",
        )
        embed.add_field(name="Bot", value=bot_description, inline=False)
        embed.add_field(
            name="Software Versions", value=software_description, inline=False
        )
        embed.add_field(name="Hardware", value=hardware_description, inline=False)
        embed.add_field(name="Listeners", value=listeners_description, inline=False)
        embed.add_field(
            name="Interactions since last reboot",
            value=interactions_description,
            inline=False,
        )

        embed.set_footer(text="Creator: Phxenix#1104, hosted on: Raspberry Pi 4")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    # error handling
    @addbadges.error
    async def addbadges_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specifiy the user and badge to add!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @removebadge.error
    async def removebadge_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specifiy the user and badge to remove!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @clearbadges.error
    async def clearbadges_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.UserNotFound)
        ):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @listrole.error
    async def listrole_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )
        else:
            raise error

    @roleinfo.error
    async def roleinfo_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Stats(bot))
    print("Stats cog loaded")
