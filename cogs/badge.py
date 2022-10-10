import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from stringmatch import Match

import utils.check
import utils.search
from utils.ids import GuildIDs


class Badge(commands.Cog):
    """Contains commands related to the user badge system."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def new_profile(self, user: discord.User) -> None:
        """Creates a new userbadges profile entry, if the user is not found in the database."""
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

    @commands.hybrid_group()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def badge(self, ctx: commands.Context) -> None:
        """Lists the group commands for the badge related commands.
        Excludes %badgeinfo because that is a freely available command,
        without admin privileges needed."""
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{ctx.prefix}badge add <user> <badge(s)>`\n"
            f"`{ctx.prefix}badge remove <user> <badge>`\n"
            f"`{ctx.prefix}badge clear <user>`\n"
            f"`{ctx.prefix}badge setinfo <badge> <info text>`\n",
            colour=self.bot.colour,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @badge.command(name="add")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user="The user to add the badges to.", badges="The badge(s) to add."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def badge_add(
        self, ctx: commands.Context, user: discord.User, *, badges: str
    ) -> None:
        """Adds multiple emoji badges to a user.
        Emojis must be a default emoji or a custom emoji the bot can use.
        """

        if ctx.interaction:
            await ctx.defer()
            message = await ctx.interaction.original_response()
        else:
            message = ctx.message

        badge_list = badges.split(" ")

        if not badge_list:
            await ctx.send("Please specify the badge(s) you want to add.")
            return

        for badge in badge_list:
            try:
                await message.add_reaction(badge)
            except discord.errors.HTTPException:
                await ctx.send("Please use only valid emojis as badges!")
                return

        await self.new_profile(user)

        added_badges = []

        async with aiosqlite.connect("./db/database.db") as db:
            user_badges = await db.execute_fetchall(
                """SELECT badges FROM userbadges WHERE :user_id = user_id""",
                {"user_id": user.id},
            )

            user_badges = user_badges[0][0].split(" ")

            added_badges.extend(
                badge for badge in badge_list if badge not in user_badges
            )
            user_badges = user_badges + added_badges

            user_badges = " ".join(user_badges)

            await db.execute(
                """UPDATE userbadges SET badges = :badges WHERE user_id = :user_id""",
                {"badges": user_badges, "user_id": user.id},
            )

            await db.commit()

        await ctx.send(f"Added badge(s) {' '.join(added_badges)} to {user.mention}.")

    @badge.command(name="remove")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user="The user to remove the badge from.", badge="The badge to remove."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def badge_remove(
        self, ctx: commands.Context, user: discord.User, badge: str
    ) -> None:
        """Removes a badge from a user."""
        # No emoji check here, since the bot could lose access in the meantime.
        # Also it doesnt really work with slash commands anyways.

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

    @badge.command(name="clear")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user to remove all badges from.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def badge_clear(self, ctx: commands.Context, user: discord.User) -> None:
        """Removes all badges from a user."""
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

    @badge.command(name="setinfo")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        badge="The badge you want to add information about.",
        info_text="The new information text for the badge.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def badge_setinfo(
        self, ctx: commands.Context, badge: str, *, info_text: str = None
    ) -> None:
        """Sets a new info text on a given badge."""
        # We first check if its a valid emoji by just reacting to the message.
        if ctx.interaction:
            await ctx.defer()
            message = await ctx.interaction.original_response()
        else:
            message = ctx.message

        try:
            await message.add_reaction(badge)
        except discord.errors.HTTPException:
            await ctx.send("Please use only valid emojis as badges!")
            return

        if not info_text:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """DELETE FROM badgeinfo WHERE badge = :badge""", {"badge": badge}
                )

                await db.commit()

            await ctx.send(f"Deleted the info text for {badge}.")
            return

        # 1000 characters seems like a good limit.
        info_text = info_text[:1000]

        async with aiosqlite.connect("./db/database.db") as db:
            # We just delete the entry to make sure that no duplicates sneak in.
            await db.execute(
                """DELETE FROM badgeinfo WHERE badge = :badge""", {"badge": badge}
            )

            await db.execute(
                """INSERT INTO badgeinfo (badge, info) VALUES (:badge, :info)""",
                {"badge": badge, "info": info_text},
            )

            await db.commit()

        await ctx.send(f"Updated badgeinfo of {badge} to: \n`{info_text}`")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(badge="The badge you want to see the details of.")
    async def badgeinfo(self, ctx: commands.Context, badge: str) -> None:
        """Gets you information about a given badge."""
        match = Match(latinise=True, ignore_case=True, include_partial=True)

        async with aiosqlite.connect("./db/database.db") as db:
            # Searching for the matching badge, since our badges are mostly animated
            # this would mean that otherwise only nitro users could search for them.
            all_badges = await db.execute_fetchall("""SELECT badge FROM badgeinfo""")

            matching_badge = match.get_best_match(
                badge, [b[0] for b in all_badges], score=40
            )

            result_badge = await db.execute_fetchall(
                """SELECT info FROM badgeinfo WHERE badge = :badge""",
                {"badge": matching_badge},
            )

            matching_users = await db.execute_fetchall(
                """SELECT user_id from userbadges WHERE INSTR(badges, :badge) > 0""",
                {"badge": matching_badge},
            )

        if len(result_badge) == 0:
            await ctx.send(
                "I could not find a matching badge in the database! Make sure you have the right one."
            )
            return

        # If its a custom emoji we set the embed thumbnail to the emoji url.
        try:
            emoji_converter = commands.PartialEmojiConverter()
            emoji = await emoji_converter.convert(ctx, matching_badge)

            if not emoji:
                raise commands.errors.EmojiNotFound

            embed = discord.Embed(title=f"Badgeinfo of {emoji}", colour=self.bot.colour)
            embed.set_thumbnail(url=emoji.url)
        except (
            commands.errors.PartialEmojiConversionFailure,
            commands.errors.EmojiNotFound,
        ):
            embed = discord.Embed(title=f"Badgeinfo of {badge}", colour=self.bot.colour)

        users = [f"<@{user_id[0]}>" for user_id in matching_users]

        embed.add_field(name="Information:", value=result_badge[0][0], inline=False)
        embed.add_field(
            name=f"Users with this badge ({len(users)}):",
            value=f"{', '.join(users) if users else 'None'}",
        )

        await ctx.send(embed=embed)

    @badge_add.error
    async def badge_add_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the user and badge to add!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @badge_remove.error
    async def badge_remove_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the user and badge to remove!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @badge_clear.error
    async def badge_clear_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.UserNotFound)
        ):
            await ctx.send("Please mention a valid user!")
        else:
            raise error

    @badge_setinfo.error
    async def badge_setinfo_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the badge and badge information!")
        else:
            raise error

    @badgeinfo.error
    async def badgeinfo_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify the badge you want to see the information of!"
            )
        else:
            raise error


async def setup(bot) -> None:
    await bot.add_cog(Badge(bot))
    print("Badge cog loaded")
