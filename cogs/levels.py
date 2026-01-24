import asyncio
import random
from math import floor
from typing import Optional

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

import utils
from utils.ids import GuildIDs, GuildNames, TGChannelIDs, TGLevelRoleIDs
from utils.image import get_dominant_colour


class Levels(commands.Cog):
    """This class handles the Leveling System of the Bot.
    We used to use Mee6, but now we use a custom system.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def get_xp_till_next_level(self, current_level: int, current_xp: int) -> int:
        """Gets you the amount of XP you need to level up to the next level.
        Taken from: https://github.com/Mee6/Mee6-documentation/blob/master/docs/levels_xp.md
        Since we used to use Mee6, we decided to keep the same formula.
        """
        return max(5 * (current_level**2) + (50 * current_level) + 100 - current_xp, 0)

    def get_xp_for_level(self, level: int) -> int:
        """Gets you the amount of XP you need to reach a certain level."""
        if level < 0:
            return 0

        return sum(self.get_xp_till_next_level(i, 0) for i in range(level))

    def get_level_from_xp(self, xp: int) -> int:
        """Gets you the level you are at from a certain amount of XP."""
        level = 0
        while self.get_xp_for_level(level) <= xp:
            level += 1
        return max(level - 1, 0)

    async def create_new_profile(self, user: discord.User) -> None:
        """Creates a profile for a user."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_profile = await db.execute_fetchall(
                """SELECT * FROM level WHERE id = :id""",
                {"id": user.id},
            )

            if len(matching_profile) != 0:
                return

            await db.execute(
                """INSERT INTO level VALUES (:id, :level, :xp, :messages)""",
                {
                    "id": user.id,
                    "level": 0,
                    "xp": 0,
                    "messages": 0,
                },
            )
            await db.commit()

    async def add_xp(self, user_id: int, xp_gained: int) -> tuple[int, int, int]:
        """Adds XP to a user and returns the old level, new level and new XP."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_profile = await db.execute_fetchall(
                """SELECT * FROM level WHERE id = :id""",
                {"id": user_id},
            )

            old_level = matching_profile[0][1]
            old_xp = matching_profile[0][2]

            new_xp = old_xp + xp_gained
            new_level = self.get_level_from_xp(new_xp)

            await db.execute(
                """UPDATE level SET xp = :new_xp, messages = messages + 1, level = :new_level WHERE id = :id""",
                {
                    "new_xp": new_xp,
                    "new_level": new_level,
                    "id": user_id,
                },
            )

            await db.commit()

        return (old_level, new_level, new_xp)

    def get_all_level_roles(self, guild: discord.Guild) -> list[discord.Role]:
        defaultrole = discord.utils.get(guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)
        level10 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_10_ROLE)
        level25 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_25_ROLE)
        level50 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_50_ROLE)
        level75 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_75_ROLE)
        level100 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_100_ROLE)

        return [defaultrole, level10, level25, level50, level75, level100]

    async def assign_level_role(
        self,
        member: discord.Member,
        levelroles: list[discord.Role],
        assign_role: discord.Role,
    ) -> discord.Role:
        """Removes every other level role and assigns the correct one."""

        roles_to_remove = [role for role in levelroles if role is not assign_role]
        await member.remove_roles(*roles_to_remove)
        await member.add_roles(assign_role)
        return assign_role

    async def update_level_role(
        self, user: discord.User, level: int, guild: discord.Guild
    ) -> Optional[discord.Role]:
        """Assigns you a new role depending on your level and removes all of the other ones.
        Returns the new role.
        """
        rolegiven = None

        levelroles = self.get_all_level_roles(guild)

        [defaultrole, level10, level25, level50, level75, level100] = levelroles

        try:
            member = await guild.fetch_member(user.id)
        except discord.NotFound:
            return

        if level >= 100:
            if level100 not in member.roles:
                rolegiven = await self.assign_level_role(member, levelroles, level100)

        elif level >= 75:
            if level75 not in member.roles:
                rolegiven = await self.assign_level_role(member, levelroles, level75)

        elif level >= 50:
            if level50 not in member.roles:
                rolegiven = await self.assign_level_role(member, levelroles, level50)

        elif level >= 25:
            if level25 not in member.roles:
                rolegiven = await self.assign_level_role(member, levelroles, level25)

        elif level >= 10:
            if level10 not in member.roles:
                rolegiven = await self.assign_level_role(member, levelroles, level10)

        else:
            if defaultrole not in member.roles:
                rolegiven = await self.assign_level_role(
                    member, levelroles, defaultrole
                )

        return rolegiven

    def get_next_role(
        self, current_xp: int, current_level: int, guild: discord.Guild
    ) -> tuple[int, int, Optional[discord.Role]]:
        """Gets you the next role, if there is any, plus the levels and XP needed to get there."""
        levelroles = self.get_all_level_roles(guild)

        [_, level10, level25, level50, level75, level100] = levelroles

        if current_level >= 100:
            return (0, 0, None)

        if current_level >= 75:
            return (
                100 - current_level,
                self.get_xp_for_level(100),
                level100,
            )

        if current_level >= 50:
            return (75 - current_level, self.get_xp_for_level(75), level75)

        if current_level >= 25:
            return (50 - current_level, self.get_xp_for_level(50), level50)

        if current_level >= 10:
            return (25 - current_level, self.get_xp_for_level(25), level25)

        return (10 - current_level, self.get_xp_for_level(10), level10)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.guild.id != GuildIDs.TRAINING_GROUNDS:
            return

        if message.channel.id in TGChannelIDs.BLACKLISTED_CHANNELS:
            return

        if self.bot.recent_messages.get(message.author.id) is not None:
            return

        if message.is_system():
            return

        # Doesn't really matter what we set it to, as long as it's not None.
        self.bot.recent_messages[message.author.id] = True

        xp_amount = random.randint(15, 25)

        await self.create_new_profile(message.author)

        old_level, new_level, _ = await self.add_xp(message.author.id, xp_amount)

        if old_level != new_level:
            role = await self.update_level_role(
                message.author, new_level, message.guild
            )

            if role:
                sent_message = f"Congrats {message.author.mention}! You leveled up to level {new_level}! You gained the {role.name} role!"
            else:
                sent_message = f"Congrats {message.author.mention}! You leveled up to level {new_level}!"

            await message.channel.send(sent_message)

        # We wait 30 seconds before removing the user from the recent_messages dict.
        # This is to prevent the user from spamming messages and getting a lot of xp.
        # Maybe replace this with a loop that runs every X seconds and removes all users from the dict?
        await asyncio.sleep(30)

        try:
            self.bot.recent_messages.pop(message.author.id)
        except KeyError:
            pass

    @commands.hybrid_group()
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def xp(self, ctx: commands.Context):
        """Lists the xp commands."""
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{ctx.prefix}xp add @user <amount>`\n"
            f"`{ctx.prefix}xp remove @user <amount>`\n",
            colour=self.bot.colour,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @xp.command(name="add")
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.describe(
        user="The user to add the xp to.", amount="The amount of xp to add to the user."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def xp_add(
        self, ctx: commands.Context, user: discord.User, amount: int
    ) -> None:
        """Adds xp to a user."""

        if amount < 0:
            await ctx.send("To remove XP, please use the xp remove command.")
            return

        await self.create_new_profile(user)

        old_level, new_level, new_xp = await self.add_xp(user.id, amount)

        if old_level != new_level:
            await self.update_level_role(user, new_level, ctx.guild)

        await ctx.send(
            f"Added {amount}XP to {user.mention}. They are now level {new_level} with {new_xp}XP."
        )

    @xp.command(name="remove")
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.describe(
        user="The user to remove the xp from.",
        amount="The amount of xp to remove from the user.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def xp_remove(
        self, ctx: commands.Context, user: discord.User, amount: int
    ) -> None:
        """Removes xp from a user."""

        if amount < 0:
            await ctx.send("To add XP, please use the xp add command.")
            return

        await self.create_new_profile(user)

        old_level, new_level, new_xp = await self.add_xp(user.id, -amount)

        if old_level != new_level:
            await self.update_level_role(user, new_level, ctx.guild)

        await ctx.send(
            f"Removed {amount}XP from {user.mention}. They are now level {new_level} with {new_xp}XP."
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def rank(self, ctx: commands.Context, user: discord.User = None) -> None:
        """Shows your level and xp, or the level and xp of another user."""
        if user is None:
            user = ctx.author

        if user.bot:
            await ctx.send("This command cannot be used on bots.")
            return

        if not ctx.guild:
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS}"
            )
            return

        if ctx.guild.id != GuildIDs.TRAINING_GROUNDS:
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS}"
            )
            return

        await ctx.typing()

        colour = await get_dominant_colour(user.display_avatar)

        embed = discord.Embed(
            title=f"Level statistics for {str(user)}",
            colour=colour,
        )

        await self.create_new_profile(user)

        async with aiosqlite.connect("./db/database.db") as db:
            matching_profile = await db.execute_fetchall(
                """SELECT * FROM level WHERE id = :id""",
                {"id": user.id},
            )

            level = matching_profile[0][1]
            xp = matching_profile[0][2]
            messages = matching_profile[0][3]

            leaderboard_rank = await db.execute_fetchall(
                """SELECT row_number() OVER (ORDER BY xp DESC) AS rank, id, level, xp, messages FROM level""",
            )
            rank = next((i[0] for i in leaderboard_rank if i[1] == user.id), 0)
            next_user = next((i for i in leaderboard_rank if i[0] == rank + 1), None)
            prev_user = next((i for i in leaderboard_rank if i[0] == rank - 1), None)

            await db.commit()

        xp_progress = xp - self.get_xp_for_level(level)
        xp_needed = self.get_xp_for_level(level + 1) - self.get_xp_for_level(level)

        [next_role_level, next_role_xp, next_role] = self.get_next_role(
            xp, level, ctx.guild
        )

        percent_next = round((xp_progress / xp_needed) * 100, 2)
        # I wanted to do this with 20 characters, but it cuts off on mobile at 17.
        progress_bar_next = ("█" * floor(percent_next / 6.25)).ljust(16, "░")

        percent_level = round((xp / next_role_xp) * 100, 2)
        progress_bar_level = ("█" * floor(percent_level / 6.25)).ljust(16, "░")

        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(
            name="Rank",
            value=f"**#{rank}**",
            inline=True,
        )
        embed.add_field(name="XP", value=f"**{xp:,}**", inline=True)
        embed.add_field(
            name="Progress to next level",
            value=f"{xp_progress:,}XP/{xp_needed:,}XP *({percent_next}%)*\n{progress_bar_next}",
            inline=False,
        )
        if next_role:
            embed.add_field(
                name="Progress to next role",
                value=f"{next_role.mention} *({next_role_level} Level needed)*\n"
                f"{xp:,}XP/{next_role_xp:,}XP *({percent_level}%)*\n{progress_bar_level}",
                inline=False,
            )
        else:
            embed.add_field(
                name="Progress to next role",
                value="No more roles to unlock!",
                inline=False,
            )

        if prev_user is not None:
            prev_member = self.bot.get_user(prev_user[1])
            if prev_member is None:
                try:
                    prev_member = await self.bot.fetch_user(prev_user[1])
                except (discord.NotFound, discord.HTTPException):
                    prev_member = "Unknown User"

            embed.add_field(
                name="User above",
                value=f"**{str(prev_member)}** - Level {prev_user[2]} *({prev_user[3]:,}XP)*\n{(prev_user[3] - xp):,}XP behind",
                inline=False,
            )

        if next_user is not None:
            next_member = self.bot.get_user(next_user[1])
            if next_member is None:
                try:
                    next_member = await self.bot.fetch_user(next_user[1])
                except (discord.NotFound, discord.HTTPException):
                    next_member = "Unknown User"

            embed.add_field(
                name="User below",
                value=f"**{str(next_member)}** - Level {next_user[2]} *({next_user[3]:,}XP)*\n{(xp - next_user[3]):,}XP ahead",
                inline=False,
            )

        embed.add_field(
            name="Messages sent",
            value=f"{messages:,}",
            inline=False,
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def levels(self, ctx: commands.Context) -> None:
        """Shows the leaderboard for levels."""

        if not ctx.guild:
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS}"
            )
            return

        if ctx.guild.id != GuildIDs.TRAINING_GROUNDS:
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS}"
            )
            return

        await ctx.typing()

        embed = discord.Embed(
            title=f"Level leaderboard of {GuildNames.TRAINING_GROUNDS}",
            colour=self.bot.colour,
        )

        async with aiosqlite.connect("./db/database.db") as db:
            leaderboard = await db.execute_fetchall(
                """SELECT row_number() OVER (ORDER BY xp DESC) AS rank, id, level, xp, messages FROM level""",
            )

            total_messages = await db.execute_fetchall(
                """SELECT SUM(messages) FROM level""",
            )

            total_xp = await db.execute_fetchall(
                """SELECT SUM(xp) FROM level""",
            )

            await db.commit()

        for rank, user_id, level, xp, messages in leaderboard[:25]:
            user = self.bot.get_user(user_id)
            if user is None:
                user = await self.bot.fetch_user(user_id)

            embed.add_field(
                name=f"#{rank} - {discord.utils.escape_markdown(str(user))}",
                value=f"Level {level} - {xp:,}XP ({messages:,} messages)",
                inline=False,
            )

        embed.set_footer(
            text=f"Total server stats: {total_xp[0][0]:,}XP - {total_messages[0][0]:,} messages",
        )

        embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)

    @xp_add.error
    async def xp_add_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid amount of XP to add.")

    @xp_remove.error
    async def xp_remove_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid amount of XP to remove.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Levels(bot))
    print("Levels cog loaded")
