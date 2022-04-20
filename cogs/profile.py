import json

import aiosqlite
import discord
import fuzzywuzzy
from discord import app_commands
from discord.ext import commands

import utils.check
from utils.ids import Emojis, GuildIDs


class Profile(commands.Cog):
    """
    Contains the profile command and everything associated with it.
    """

    def __init__(self, bot):
        self.bot = bot

    def match_character(self, profile_input: str) -> list[str]:
        """
        Matches the input to one or multiple characters and returns the corresponding emoji.
        Separates the input by commas.
        Works with names, commonly used nicknames or Fighters ID Number.
        Example:
            Input: incin, wii fit trainer, 4e
            Output: [
                <:Incineroar:929086965763145828>,
                <:WiiFitTrainer:929086966115483748>,
                <:DarkSamus:929068123020202004>,
            ]
        """
        with open(r"./files/characters.json", "r", encoding="utf-8") as f:
            characters = json.load(f)

        output_characters = []

        if profile_input is None:
            return output_characters

        profile_input = profile_input.lower()
        input_characters = profile_input.split(",")

        for i_char in input_characters:
            # this strips leading and trailing whitespaces
            i_char = i_char.strip()

            for match_char in characters["Characters"]:
                # 2 characters (pt, aegis) have more than 1 id, so the ids need to be in a list
                if (
                    i_char == match_char["name"]
                    or i_char in match_char["id"]
                    or i_char in match_char["aliases"]
                ) and match_char["emoji"] not in output_characters:
                    output_characters.append(match_char["emoji"])

        return output_characters

    def get_badges(self, user: discord.User) -> list[str]:

        """
        Gets you all of the badges of a member.
        """
        badges = []

        # quick check for ourselves
        if user == self.bot.user:
            return badges

        # the badge roles are not in only one server
        for guild in user.mutual_guilds:
            if member := guild.get_member(user.id):
                # getting all of the role ids in a list
                role_ids = [role.id for role in member.roles]
                # and then checking with the dict
                badges.extend(
                    badge
                    for badge, role in Emojis.PROFILE_BADGES.items()
                    if role in role_ids
                )

        return badges

    async def make_new_profile(self, user: discord.User):
        """
        Creates a new profile for the user, if the user does not already have a profile set up.
        """
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

    async def character_autocomplete(self, current: str) -> list[app_commands.Choice]:
        """
        Autocompletion for the Smash characters.
        We are using this for matching mains, secondaries and pockets.
        """
        with open(r"./files/characters.json", "r", encoding="utf-8") as f:
            characters = json.load(f)

        existing_chars = None
        choices = []
        character_names = [
            character["name"].title() for character in characters["Characters"]
        ]

        # we only wanna match the current char, so we split the input
        if "," in current:
            existing_chars, current_char = current.rsplit(",", 1)

        else:
            current_char = current

        # we validate the input first, otherwise the console is
        # getting spammed with warnings on invalid or unmatchable inputs
        if fuzzywuzzy.utils.full_process(current_char):
            match_list = fuzzywuzzy.process.extractBests(
                current_char, character_names, limit=25, score_cutoff=60
            )

            # we append the existing chars to the current choices,
            # so you can select multiple characters at once and the autocomplete still works
            if existing_chars:
                choices.extend(
                    # choices can be up to 100 chars in length,
                    # which we could exceed with 10 chars, so we have to cut it off.
                    app_commands.Choice(
                        name=f"{existing_chars}, {match[0]}"[:100],
                        value=f"{existing_chars}, {match[0]}"[:100],
                    )
                    for match in match_list
                )
            else:
                choices.extend(
                    app_commands.Choice(name=match[0], value=match[0])
                    for match in match_list
                )

        return choices[:25]

    @commands.hybrid_command(aliases=["smashprofile", "profileinfo"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user you want to see the profile of.")
    async def profile(self, ctx, user: discord.User = None):
        """
        Returns the profile of a user, or yourself if you do not specify a user.
        """
        if user is None:
            user = ctx.author

        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM profile WHERE user_id = :user_id""",
                {"user_id": user.id},
            )
            matching_user_elo = await db.execute_fetchall(
                """SELECT elo FROM ranking WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        if len(matching_user) == 0:
            await ctx.send("This user did not set up their profile yet.")
            return

        (_, tag, region, mains, secondaries, pockets, note, colour) = matching_user[0]

        elo = 1000 if len(matching_user_elo) == 0 else matching_user_elo[0][0]
        badges = " ".join(self.get_badges(user))

        embed = discord.Embed(title=f"Smash profile of {str(user)}", colour=colour)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Tag:", value=tag, inline=True)

        if region:
            embed.add_field(name="Region:", value=region, inline=True)

        embed.add_field(name="Elo score:", value=elo, inline=True)

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
    async def deleteprofile(self, ctx):
        """
        Deletes your profile.
        """
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

    @commands.command()
    @utils.check.is_moderator()
    async def forcedeleteprofile(self, ctx, user: discord.User):
        """
        Deletes the profile of another user, just in case.
        """
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
    @app_commands.describe(mains="Your mains, separated by commas.")
    async def mains(self, ctx, *, mains: str = None):
        """
        Sets your mains on your smash profile.
        Separates the input by commas, and then matches with names, nicknames and fighter numbers.
        Echoes have an *e* behind their fighter number.
        """
        # only getting the first 7 chars, think thats a very generous cutoff
        chars = " ".join(self.match_character(mains)[:7])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET mains = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if mains is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your mains.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your mains to: {chars}")

    @mains.autocomplete("mains")
    async def mains_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self.character_autocomplete(current)

    @commands.hybrid_command(
        aliases=["secondary", "setsecondary", "spsecondaries", "profilesecondaries"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(secondaries="Your secondaries, separated by commas.")
    async def secondaries(self, ctx, *, secondaries: str = None):
        """
        Sets your secondaries on your smash profile.
        Separates the input by commas, and then matches with names, nicknames and fighter numbers.
        Echoes have an *e* behind their fighter number.
        """
        chars = " ".join(self.match_character(secondaries)[:7])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET secondaries = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if secondaries is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your secondaries.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your secondaries to: {chars}"
            )

    @secondaries.autocomplete("secondaries")
    async def secondaries_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        return await self.character_autocomplete(current)

    @commands.hybrid_command(
        aliases=["pocket", "setpocket", "sppockets", "profilepockets"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(pockets="Your pockets, separated by commas.")
    async def pockets(self, ctx, *, pockets: str = None):
        """
        Sets your pockets on your smash profile.
        Separates the input by commas, and then matches with names, nicknames and fighter numbers.
        Echoes have an *e* behind their fighter number.
        """
        # since you can have some more pockets, i put it at 10 max.
        # there could be a max of around 25 per embed field however
        chars = " ".join(self.match_character(pockets)[:10])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET pockets = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if pockets is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your pockets.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your pockets to: {chars}")

    @pockets.autocomplete("pockets")
    async def pockets_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        return await self.character_autocomplete(current)

    @commands.hybrid_command(aliases=["smashtag", "sptag", "settag"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(tag="Your tag.")
    async def tag(self, ctx, *, tag: str = None):
        """
        Sets your tag on your smash profile.
        Up to 30 characters long.
        """
        # the default tag is just your discord tag
        if tag is None:
            tag = str(ctx.author)

        # think 30 chars for a tag is fair
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

    # a dictionary of valid profile regions.
    # tried to be as broad as possible here, hope i didnt miss anything big.
    # outside of functions cause we need it in the autocomplete, too.
    # but at the same time i didnt think this should be in a json file or something.
    region_dict = {
        "North America": [
            "na",
            "north america",
            "usa",
            "us",
            "canada",
            "latin america",
            "america",
            "united states",
        ],
        "NA East": [
            "east coast",
            "us east",
            "east",
            "midwest",
            "na east",
            "canada east",
        ],
        "NA West": [
            "west coast",
            "us west",
            "west",
            "na west",
            "canada west",
        ],
        "NA South": [
            "mexico",
            "south",
            "us south",
            "na south",
            "texas",
            "southern",
        ],
        "South America": [
            "sa",
            "brazil",
            "argentina",
            "south america",
            "chile",
            "peru",
        ],
        "Europe": [
            "eu",
            "europe",
            "uk",
            "england",
            "france",
            "germany",
        ],
        "Asia": [
            "asia",
            "sea",
            "china",
            "japan",
            "india",
            "middle east",
        ],
        "Africa": [
            "africa",
            "south africa",
            "egypt",
            "nigeria",
            "maghreb",
            "north africa",
        ],
        "Oceania": [
            "australia",
            "new zealand",
            "nz",
            "au",
            "oceania",
        ],
    }

    @commands.hybrid_command(aliases=["setregion", "spregion", "country"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(region="Your region you want to display on your profile.")
    async def region(self, ctx, *, region: str = None):
        """
        Sets your region on your smash profile.
        Matches to commonly used regions, which are:
        North America, NA East, NA West, NA South, South America, Europe, Asia, Africa, Oceania.
        """
        if region is None:
            region = ""

        # matching the input to the dict
        for matching_region, input_regions in self.region_dict.items():
            if region.lower() in input_regions:
                region = matching_region

        # double checking if the input got matched and is not None
        if region and region not in self.region_dict:
            await ctx.send(
                f"Please choose a valid region. Example: `{self.bot.command_prefix}region Europe`"
            )
            return

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET region = :region WHERE user_id = :user_id""",
                {"region": region, "user_id": ctx.author.id},
            )

            await db.commit()

        if region == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your region.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your region to: `{region}`"
            )

    @region.autocomplete("region")
    async def region_autocomplete(self, interaction: discord.Interaction, current: str):
        valid_regions = list(self.region_dict.keys())

        # again, dont really need fuzzy search here, these are just some very basic regions.
        choices = [
            app_commands.Choice(name=region, value=region)
            for region in valid_regions
            if current in region.lower()
        ]

        return choices[:25]

    @commands.hybrid_command(aliases=["setnote", "spnote"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(note="Your note you want to display on your profile.")
    async def note(self, ctx, *, note: str = None):
        """
        Sets your note on your smash profile.
        Up to 150 characters long.
        """
        if note is None:
            note = ""

        # for a note, 150 chars seem enough to me
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
        aliases=["color", "spcolour", "spcolor", "setcolour", "setcolor"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(colour="The hex colour code for your smash profile.")
    async def colour(self, ctx, colour: str):
        """
        Sets your embed colour on your smash profile.
        Use a hex colour code with a leading #.
        """
        # hex colour codes are 7 digits long and start with #
        if not colour.startswith("#") or len(colour) != 7:
            await ctx.send(
                f"Please choose a valid hex colour code. Example: `{self.bot.command_prefix}colour #8a0f84`"
            )
            return

        colour = colour.replace("#", "0x")

        try:
            hex_colour = int(colour, 16)
        except ValueError:
            await ctx.send(
                f"Please choose a valid hex colour code. Example: `{self.bot.command_prefix}colour #8a0f84`"
            )
            return

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET colour = :colour WHERE user_id = :user_id""",
                {"colour": hex_colour, "user_id": ctx.author.id},
            )

            await db.commit()

        await ctx.send(f"{ctx.author.mention}, I have set your colour to: `{colour}`")

    # some basic error handling for the above
    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            await ctx.send(
                "I couldn't find this user, make sure you have the right one or just leave it blank."
            )
        else:
            raise error

    @forcedeleteprofile.error
    async def forcedeleteprofile_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify which profile to delete.")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                "I couldn't find this user, make sure you have the right one."
            )
        else:
            raise error

    @colour.error
    async def colour_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Please choose a valid hex colour code. Example: `{self.bot.command_prefix}colour #8a0f84`"
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Profile(bot))
    print("Profile cog loaded")
