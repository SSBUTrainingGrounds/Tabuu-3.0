import datetime
import os
import platform
import time
from functools import reduce
from io import StringIO

import aiosqlite
import discord
import psutil
from discord import app_commands
from discord.ext import commands
from stringmatch import Match

import utils.check
import utils.search
from utils.ids import GuildIDs, TGRoleIDs
from utils.image import get_dominant_colour


class Stats(commands.Cog):
    """Contains commands vaguely related to statistics.
    User stats, Bot stats, Server stats, Role stats, you name it.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(aliases=["user", "user-info", "info"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to get info about.")
    async def userinfo(
        self, ctx: commands.Context, member: discord.Member = None
    ) -> None:
        """Some information about a given user, or yourself."""
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

        colour = await get_dominant_colour(member.display_avatar)

        embed = discord.Embed(
            title=f"Userinfo of {str(member)} ({member.id})",
            colour=colour,
        )
        embed.add_field(name="Name:", value=member.mention, inline=True)
        embed.add_field(name="Top Role:", value=member.top_role.mention, inline=True)
        embed.add_field(
            # Gives the number of roles to prevent listing like 35 roles, -1 for the @everyone role.
            name="Number of Roles:",
            value=f"{(len(member.roles)-1)}",
            inline=True,
        )
        embed.add_field(
            # Timezone aware datetime object, F is long formatting.
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

    @commands.hybrid_command(aliases=["role"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        role="The role you want to get info about. Matches to your closest input."
    )
    async def roleinfo(self, ctx: commands.Context, *, role: str) -> None:
        """Basic information about a given role."""
        matching_role = utils.search.search_role(ctx.guild, role)

        embed = discord.Embed(
            title=f"Roleinfo of {matching_role.name} ({matching_role.id})",
            colour=matching_role.colour,
        )
        embed.add_field(name="Role Name:", value=matching_role.mention, inline=True)
        embed.add_field(
            name="Users with role:", value=len(matching_role.members), inline=True
        )
        embed.add_field(
            name="Created at:",
            value=discord.utils.format_dt(matching_role.created_at, style="F"),
        )
        embed.add_field(
            name="Mentionable:", value=matching_role.mentionable, inline=True
        )
        embed.add_field(
            name="Displayed Seperately:", value=matching_role.hoist, inline=True
        )
        embed.add_field(name="Colour:", value=matching_role.colour, inline=True)

        if matching_role.display_icon:
            # The display_icon could be an asset or a default emoji with the str type, so we have to check.
            # If its an asset, we display it in the thumbnail.
            if isinstance(matching_role.display_icon, discord.asset.Asset):
                embed.set_thumbnail(url=matching_role.display_icon.url)
            # If its an emoji we add it as the 2nd field.
            elif isinstance(matching_role.display_icon, str):
                embed.insert_field_at(
                    1, name="Role Emoji:", value=matching_role.display_icon, inline=True
                )

        await ctx.send(embed=embed)

    @roleinfo.autocomplete("role")
    async def roleinfo_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        return utils.search.autocomplete_choices(
            current, [role.name for role in interaction.guild.roles]
        )

    @commands.hybrid_command(aliases=["listroles"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        roles="The role, or roles, you want to search the members of. Matches to your closest input."
    )
    async def listrole(self, ctx: commands.Context, *, roles: str) -> None:
        """Lists every member of a role, or the overlap of members of multiple roles.
        If you want to search for multiple roles, separate them with a comma."""
        # First we match each role with an actual role using the search_role utility function.
        role_list = [
            utils.search.search_role(ctx.guild, role) for role in roles.split(",")
        ]

        def escape_everything(input: str) -> str:
            return discord.utils.escape_mentions(discord.utils.escape_markdown(input))

        # Need different messages for singular and plural.
        if len(role_list) == 1:
            role_message = f"{escape_everything(role_list[0].name)} role"
        else:
            role_message = (
                f"{', '.join(escape_everything(role.name) for role in role_list)} roles"
            )

        # Getting the overlap between all of the role's members.
        intersect = list(
            reduce(set.intersection, [set(role.members) for role in role_list])
        )

        members = [
            f"{i + 1}) {member.name} - <@{member.id}>"
            for (i, member) in enumerate(intersect)
        ]

        buffer = StringIO("\n".join(members))
        f = discord.File(buffer, filename=f"{role_message}_users.txt")

        # If there are too many or no members, we send a special message.
        if len(intersect) > 60:
            await ctx.send(
                f"Users with the {role_message} ({len(intersect)}):\n`Too many users to list!`",
                file=f,
            )
            return
        if not intersect:
            await ctx.send(f"No user currently has the {role_message}!")
            return

        await ctx.send(
            f"Users with the {role_message} ({len(intersect)}):\n{', '.join(escape_everything(str(member)) for member in intersect)}",
            file=f,
        )

    @listrole.autocomplete("roles")
    async def listrole_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        existing_roles = None
        choices = []

        if "," in current:
            existing_roles, current_role = current.rsplit(",", 1)
        else:
            current_role = current

        # We dont use the autocomplete function here from utils.search,
        # cause we need some customisation here.
        match = Match(ignore_case=True, include_partial=True, latinise=True)

        match_list = match.get_best_matches(
            current_role,
            [role.name for role in interaction.guild.roles],
            score=40,
            limit=25,
        )

        # We append the existing chars to the current choices,
        # so you can select multiple roles at once and the autocomplete still works.
        if existing_roles:
            choices.extend(
                # Choices can be up to 100 chars in length,
                # which we could exceed with enough roles, so we have to cut it off.
                app_commands.Choice(
                    name=f"{existing_roles}, {match}"[:100],
                    value=f"{existing_roles}, {match}"[:100],
                )
                for match in match_list
            )
        else:
            choices.extend(
                app_commands.Choice(name=match, value=match) for match in match_list
            )

        return choices[:25]

    @commands.hybrid_command(aliases=["serverinfo"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def server(self, ctx: commands.Context) -> None:
        """Various information about the server."""
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
            title=f"{ctx.guild.name} ({ctx.guild.id})", colour=discord.Colour.green()
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

    @commands.hybrid_command(aliases=["botstats"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def stats(self, ctx: commands.Context) -> None:
        """Statistics and information about this bot."""
        proc = psutil.Process(os.getpid())
        uptime_seconds = time.time() - proc.create_time()

        # They return byte values but we want gigabytes.
        ram_used = round(psutil.virtual_memory()[3] / (1024 * 1024 * 1024), 2)
        ram_total = round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)
        ram_percent = round((ram_used / ram_total) * 100, 1)

        async with aiosqlite.connect("./db/database.db") as db:
            macro_list = await db.execute_fetchall("""SELECT name FROM macros""")

            all_commands = await db.execute_fetchall(
                """SELECT SUM(uses) FROM commands"""
            )

        # This also walks through the subcommands of each group command .get_commands() would miss those.
        slash_commands = sum(
            len(
                list(
                    self.bot.tree.walk_commands(
                        guild=ctx.guild, type=discord.AppCommandType(i)
                    )
                )
            )
            # Each type of command, 1 = slash command, 2 = user command, 3 = context menu command.
            # We dont have any user commands and only one context command
            # but this might change in the future, you never know.
            for i in range(1, 4)
        )

        message_commands = len(list(self.bot.walk_commands()))

        # We use codeblocks with yml syntax highlighting
        # just cause it looks nice, in my opinion.
        # Well at least it does on desktop.
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
Number of Message Commands: {message_commands + len(macro_list)}
Number of Application Commands: {slash_commands}
Number of Events: {len(self.bot.extra_events)}
Commands executed: {all_commands[0][0]}
```
        """

        embed = discord.Embed(
            title="Tabuu 3.0 Stats",
            colour=self.bot.colour,
            url="https://github.com/SSBUTrainingGrounds/Tabuu-3.0",
        )
        embed.add_field(name="Bot", value=bot_description, inline=False)
        embed.add_field(name="Software", value=software_description, inline=False)
        embed.add_field(name="Hardware", value=hardware_description, inline=False)
        embed.add_field(name="Commands", value=listeners_description, inline=False)

        embed.set_footer(text="Creator: Phxenix, hosted on: Raspberry Pi 4")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    # Dictionary of all of hero's moves and their mana cost.
    mana_dict = {
        "acceleratle": 13,
        "psycheup": 14,
        "oomph": 16,
        "whack": 10,
        "thwack": 30,
        "sizz": 8,
        "bang": 9,
        "kaboom": 37,
        "magic burst": "all",
        "snooze": 16,
        "flame slash": 12,
        "kacrackle slash": 11,
        "kamikazee": 1,
        "bounce": 14,
        "hocus pocus": 4,
        "heal": 7,
        "zoom": 8,
        "hatchet man": 15,
        "kaclang": 6,
        "metal slash": 6,
        "frizz": 6,
        "frizzle": 16,
        "kafrizz": 36,
        "zap": 8,
        "zapple": 18,
        "kazap": 42,
        "woosh": 5,
        "swoosh": 9,
        "kaswoosh": 18,
    }

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(move="The move you want get the mana cost for.")
    async def mp4(self, ctx: commands.Context, *, move: str = None) -> None:
        """Gives you the amount of mana used for any of Hero's moves."""
        if not move:
            await ctx.send(
                f"To see the mana cost of a move, use `{ctx.prefix}mp4 <move>`.\n"
                f"Available moves: \n`{', '.join([m.title() for m in self.mana_dict])}`"
            )
            return

        if move.lower() in self.mana_dict:
            await ctx.send(
                f"The MP cost for *{move.title()}* is {self.mana_dict[move.lower()]} MP."
            )
            return

        match = Match(ignore_case=True)

        if closest_match := match.get_best_match(
            move.lower(), [x for x in self.mana_dict.keys()], score=40
        ):
            await ctx.send(
                f"Please input a valid move! Did you mean `{closest_match.title()}`?"
            )
        else:
            await ctx.send("Please input a valid move!")

    @mp4.autocomplete("move")
    async def mp4_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        return utils.search.autocomplete_choices(
            current, [m.title() for m in self.mana_dict]
        )

    @listrole.error
    async def listrole_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I could not find a good match for one or more roles you provided. "
                "Please be more specific, mention the role, or use the Role ID.\n"
                "If you are searching for multiple roles, be sure to separate them with a comma."
            )

    @roleinfo.error
    async def roleinfo_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )


async def setup(bot) -> None:
    await bot.add_cog(Stats(bot))
    print("Stats cog loaded")
