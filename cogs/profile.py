import json

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from stringmatch import Match

import utils.check
from cogs.ranking import Ranking
from utils.character import match_character
from utils.ids import Emojis, GuildIDs
from views.profile import CharacterView, ColourView, RegionView


class Profile(commands.Cog):
    """Contains the profile command and everything associated with it."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def get_badges(self, user: discord.User) -> list[str]:
        """Gets you all of the badges of a member."""
        badges = []

        # Quick check for ourselves.
        if user == self.bot.user:
            return badges

        # The badge roles are not in only one server.
        for guild in user.mutual_guilds:
            if member := guild.get_member(user.id):
                # Getting all of the role ids in a list.
                role_ids = [role.id for role in member.roles]
                # And then checking with the dict.
                badges.extend(
                    badge
                    for badge, role in Emojis.PROFILE_BADGES.items()
                    if role in role_ids
                )

        return badges

    async def make_new_profile(self, user: discord.User) -> None:
        """Creates a new profile for the user, if the user does not already have a profile set up."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_profile = await db.execute_fetchall(
                """SELECT * FROM profile WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

            if len(matching_profile) != 0:
                return

            await db.execute(
                """INSERT INTO profile VALUES (:user_id, :tag, :region, :mains, :secondaries, :pockets, :note, :colour)""",
                {
                    "user_id": user.id,
                    "tag": f"{str(user)}",
                    "region": "",
                    "mains": "",
                    "secondaries": "",
                    "pockets": "",
                    "note": "",
                    "colour": 0,
                },
            )

            await db.commit()

    def character_autocomplete(self, current: str) -> list[app_commands.Choice]:
        """Autocompletion for the Smash characters.
        We are using this for matching mains, secondaries and pockets.
        """
        with open(r"./files/characters.json", "r", encoding="utf-8") as f:
            characters = json.load(f)

        existing_chars = None
        choices = []
        character_names = [
            character["name"].title() for character in characters["Characters"]
        ]

        # We only wanna match the current char, so we split the input.
        if "," in current:
            existing_chars, current_char = current.rsplit(",", 1)

        else:
            current_char = current

        # We dont use the autocomplete function here from utils.search,
        # cause we need some customisation here.
        match = Match(ignore_case=True, include_partial=True, latinise=True)

        match_list = match.get_best_matches(
            current_char, character_names, score=40, limit=25
        )

        # We append the existing chars to the current choices,
        # so you can select multiple characters at once and the autocomplete still works.
        if existing_chars:
            choices.extend(
                # Choices can be up to 100 chars in length,
                # which we could exceed with 10 chars, so we have to cut it off.
                app_commands.Choice(
                    name=f"{existing_chars}, {match}"[:100],
                    value=f"{existing_chars}, {match}"[:100],
                )
                for match in match_list
            )
        else:
            choices.extend(
                app_commands.Choice(name=match, value=match) for match in match_list
            )

        return choices[:25]

    @commands.hybrid_command(aliases=["smashprofile", "profileinfo"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user you want to see the profile of.")
    async def profile(self, ctx: commands.Context, user: discord.User = None) -> None:
        """Returns the profile of a user, or yourself if you do not specify a user."""
        if user is None:
            user = ctx.author

        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM profile WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        if len(matching_user) == 0:
            await ctx.send("This user did not set up their profile yet.")
            return

        (_, tag, region, mains, secondaries, pockets, note, colour) = matching_user[0]

        badges = " ".join(self.get_badges(user))

        embed = discord.Embed(title=f"Smash profile of {str(user)}", colour=colour)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Tag:", value=tag, inline=True)

        if region:
            embed.add_field(name="Region:", value=region, inline=True)

        player, _, _, _ = await Ranking.get_player(self, user)

        embed.add_field(
            name="TabuuSkill",
            value=Ranking.get_display_rank(self, player),
            inline=True,
        )

        if mains:
            embed.add_field(name="Mains:", value=mains, inline=True)
        if secondaries:
            embed.add_field(name="Secondaries:", value=secondaries, inline=True)
        if pockets:
            embed.add_field(name="Pockets:", value=pockets, inline=True)
        if note:
            embed.add_field(name="Note:", value=note, inline=True)
        if badges:
            embed.add_field(name="Emblems:", value=badges, inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def deleteprofile(self, ctx: commands.Context) -> None:
        """Deletes your profile."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM profile WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

            if len(matching_user) == 0:
                await ctx.send("You have no profile saved.")
                return

            await db.execute(
                """DELETE FROM profile WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

            await db.commit()

        await ctx.send(f"Successfully deleted your profile, {ctx.author.mention}.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def forcedeleteprofile(
        self, ctx: commands.Context, user: discord.User
    ) -> None:
        """Deletes the profile of another user, just in case."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM profile WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

            if len(matching_user) == 0:
                await ctx.send("This user has no profile saved.")
                return

            await db.execute(
                """DELETE FROM profile WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

            await db.commit()

        await ctx.send(
            f"{ctx.author.mention}, I have successfully deleted the profile of {discord.utils.escape_markdown(str(user))}."
        )

    @commands.hybrid_command(aliases=["main", "setmain", "spmains", "profilemains"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def mains(self, ctx: commands.Context) -> None:
        """Sets your mains on your smash profile."""

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            matching_mains = await db.execute_fetchall(
                """SELECT mains FROM profile WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

        chars = matching_mains[0][0].split(" ") if len(matching_mains[0][0]) else []
        view = CharacterView(ctx.author, chars, "mains", 7)

        await ctx.send(
            "Choose your mains. Select them in order of desired appearance.\nYou have up to 7 choices.\nClick submit when you are done.",
            view=view,
        )

    @commands.hybrid_command(
        aliases=["secondary", "setsecondary", "spsecondaries", "profilesecondaries"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def secondaries(self, ctx: commands.Context) -> None:
        """Sets your secondaries on your smash profile."""
        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            matching_secondaries = await db.execute_fetchall(
                """SELECT secondaries FROM profile WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

        chars = (
            matching_secondaries[0][0].split(" ")
            if len(matching_secondaries[0][0])
            else []
        )

        view = CharacterView(ctx.author, chars, "secondaries", 7)

        await ctx.send(
            "Choose your secondaries. Select them in order of desired appearance.\nYou have up to 7 choices.\nClick submit when you are done.",
            view=view,
        )

    @commands.hybrid_command(
        aliases=["pocket", "setpocket", "sppockets", "profilepockets"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def pockets(self, ctx: commands.Context) -> None:
        """Sets your pockets on your smash profile."""
        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            matching_pockets = await db.execute_fetchall(
                """SELECT pockets FROM profile WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

        chars = matching_pockets[0][0].split(" ") if len(matching_pockets[0][0]) else []
        view = CharacterView(ctx.author, chars, "pockets", 10)

        await ctx.send(
            "Choose your pockets. Select them in order of desired appearance.\nYou have up to 10 choices.\nClick submit when you are done.",
            view=view,
        )

    @commands.hybrid_command(aliases=["smashtag", "sptag", "settag"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(tag="Your tag.")
    async def tag(self, ctx: commands.Context, *, tag: str = None) -> None:
        """Sets your tag on your smash profile.
        Up to 30 characters long.
        """
        # The default tag is just your discord tag.
        if tag is None:
            tag = str(ctx.author)

        # Think 30 chars for a tag is very fair.
        tag = tag[:30]

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET tag = :tag WHERE user_id = :user_id""",
                {"tag": tag, "user_id": ctx.author.id},
            )

            await db.commit()

        await ctx.send(
            f"{ctx.author.mention}, I have set your tag to: `{discord.utils.remove_markdown(tag)}`"
        )

    @commands.hybrid_command(aliases=["setregion", "spregion", "country"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def region(self, ctx: commands.Context) -> None:
        """Sets your region on your smash profile.
        Matches to commonly used regions, which are:
        North America, NA East, NA West, NA South, South America, Europe, Asia, Africa, Oceania.
        """

        await self.make_new_profile(ctx.author)

        await ctx.send("Please choose your region:", view=RegionView(ctx.author))

    @commands.hybrid_command(aliases=["setnote", "spnote"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(note="Your note you want to display on your profile.")
    async def note(self, ctx: commands.Context, *, note: str = None) -> None:
        """Sets your note on your smash profile.
        Up to 150 characters long.
        """
        if note is None:
            note = ""

        # For a note, 150 chars seem enough to me.
        note = note[:150]

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET note = :note WHERE user_id = :user_id""",
                {"note": note, "user_id": ctx.author.id},
            )

            await db.commit()

        if note == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your note.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your note to: `{discord.utils.remove_markdown(note)}`"
            )

    @commands.hybrid_command(
        aliases=["color", "spcolour", "spcolor", "setcolour", "setcolor", "hex"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def colour(self, ctx: commands.Context) -> None:
        """Sets your embed colour on your smash profile.
        Use a hex colour code with a leading #.
        """
        view = ColourView(ctx.author)

        await ctx.send(
            "Please choose your embed colour. Pick from one of the predefined options or select your own below.",
            view=view,
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(character="The character you are looking for.")
    async def players(self, ctx: commands.Context, *, character: str) -> None:
        """Looks up a character's players in the database.
        Sorted by mains, secondaries and pockets.
        """
        # This command can take a while, so this serves as an indicator that the bot is doing something.
        # Also for the slash command version, this defers the interaction which is nice.
        await ctx.typing()

        matching_character = " ".join(match_character(character)[:1])

        if not matching_character:
            await ctx.send("Please input a valid character!")
            return

        async with aiosqlite.connect("./db/database.db") as db:
            # We look for the players that have registered the character in their profile.
            # We sort it by the length of the mains, which does roughly correlate to the amount of mains.
            # So that a solo-main will show up near the top.
            matching_mains = await db.execute_fetchall(
                """SELECT user_id FROM profile WHERE INSTR(mains, :character) ORDER BY length(mains)""",
                {"character": matching_character},
            )

            matching_secondaries = await db.execute_fetchall(
                """SELECT user_id FROM profile WHERE INSTR(secondaries, :character) ORDER BY length(secondaries)""",
                {"character": matching_character},
            )

            matching_pockets = await db.execute_fetchall(
                """SELECT user_id FROM profile WHERE INSTR(pockets, :character) ORDER BY length(pockets)""",
                {"character": matching_character},
            )

        try:
            emoji_converter = commands.PartialEmojiConverter()
            emoji = await emoji_converter.convert(ctx, matching_character)

            if not emoji:
                raise commands.errors.EmojiNotFound

            embed = discord.Embed(
                title=f"{emoji.name} Players:", colour=self.bot.colour
            )
            embed.set_thumbnail(url=emoji.url)
        except (
            commands.errors.PartialEmojiConversionFailure,
            commands.errors.EmojiNotFound,
        ):
            embed = discord.Embed(
                title=f"{matching_character} Players:", colour=self.bot.colour
            )

        mains_list = []
        # We have to cap it off at some point, I think 50 sounds pretty reasonable for our server.
        for player in matching_mains[:50]:
            # First we see if the user is in the cache.
            user = self.bot.get_user(player[0])
            # If not we have to fetch the user, this can take some time.
            if not user:
                user = await self.bot.fetch_user(player[0])
            mains_list.append(discord.utils.escape_markdown(str(user)))

        secondaries_list = []
        for player in matching_secondaries[:50]:
            user = self.bot.get_user(player[0])
            if not user:
                user = await self.bot.fetch_user(player[0])
            secondaries_list.append(discord.utils.escape_markdown(str(user)))

        pockets_list = []
        for player in matching_pockets[:50]:
            user = self.bot.get_user(player[0])
            if not user:
                user = await self.bot.fetch_user(player[0])
            pockets_list.append(discord.utils.escape_markdown(str(user)))

        embed.add_field(
            name="Mains:",
            value=", ".join(mains_list)[:1000] if matching_mains else "None",
            inline=False,
        )

        embed.add_field(
            name="Secondaries:",
            value=", ".join(secondaries_list)[:1000]
            if matching_secondaries
            else "None",
            inline=False,
        )

        embed.add_field(
            name="Pockets:",
            value=", ".join(pockets_list)[:1000] if matching_pockets else "None",
            inline=False,
        )

        embed.set_footer(
            text=f"To see the individual profiles: {ctx.prefix}profile <player>"
        )

        await ctx.send(embed=embed)

    @players.autocomplete("character")
    async def players_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        return self.character_autocomplete(current)


async def setup(bot) -> None:
    await bot.add_cog(Profile(bot))
    print("Profile cog loaded")
