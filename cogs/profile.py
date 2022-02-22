import discord
from discord.ext import commands
import aiosqlite
import json
import utils.check


class Profile(commands.Cog):
    """
    Contains the profile command and everything associated with it.
    """

    def __init__(self, bot):
        self.bot = bot

    def match_character(self, input):
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
        with open(r"./files/characters.json", "r") as f:
            characters = json.load(f)

        output_characters = []

        if input is None:
            return output_characters

        input = input.lower()
        input_characters = input.split(",")

        for i_char in input_characters:
            # this strips leading and trailing whitespaces
            i_char = i_char.strip()

            for match_char in characters["Characters"]:
                # 2 characters (pt, aegis) have more than 1 id, so the ids need to be in a list
                if (
                    i_char == match_char["name"]
                    or i_char in match_char["id"]
                    or i_char in match_char["aliases"]
                ):
                    if match_char["emoji"] not in output_characters:
                        output_characters.append(match_char["emoji"])

        return output_characters

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

    @commands.command(aliases=["smashprofile", "profileinfo"])
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
        if len(matching_user_elo) == 0:
            elo = 1000
        else:
            elo = matching_user_elo[0][0]

        embed = discord.Embed(title=f"Smash profile of {str(user)}", colour=colour)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Tag", value=tag, inline=True)

        if region != "":
            embed.add_field(name="Region", value=region, inline=True)

        embed.add_field(name="Elo score", value=elo, inline=True)

        if mains != "":
            embed.add_field(name="Mains", value=mains, inline=True)
        if secondaries != "":
            embed.add_field(name="Secondaries", value=secondaries, inline=True)
        if pockets != "":
            embed.add_field(name="Pockets", value=pockets, inline=True)
        if note != "":
            embed.add_field(name="Note", value=note, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
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

    @commands.command(aliases=["main", "setmain", "spmains", "profilemains"])
    async def mains(self, ctx, *, input=None):
        """
        Sets your mains on your smash profile.
        """
        # only getting the first 7 chars, think thats a very generous cutoff
        chars = " ".join(self.match_character(input)[:7])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET mains = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your mains.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your mains to: {chars}")

    @commands.command(
        aliases=["secondary", "setsecondary", "spsecondaries", "profilesecondaries"]
    )
    async def secondaries(self, ctx, *, input=None):
        """
        Sets your secondaries on your smash profile.
        """
        chars = " ".join(self.match_character(input)[:7])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET secondaries = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your secondaries.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your secondaries to: {chars}"
            )

    @commands.command(aliases=["pocket", "setpocket", "sppockets", "profilepockets"])
    async def pockets(self, ctx, *, input=None):
        """
        Sets your pockets on your smash profile.
        """
        # since you can have some more pockets, i put it at 10 max. there could be a max of around 25 per embed field however
        chars = " ".join(self.match_character(input)[:7])

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET pockets = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": ctx.author.id},
            )

            await db.commit()

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your pockets.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your pockets to: {chars}")

    @commands.command(aliases=["smashtag", "sptag", "settag"])
    async def tag(self, ctx, *, input=None):
        """
        Sets your tag on your smash profile.
        """
        # the default tag is just your discord tag
        if input is None:
            input = str(ctx.author)

        # think 30 chars for a tag is fair
        input = input[:30]

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET tag = :tag WHERE user_id = :user_id""",
                {"tag": input, "user_id": ctx.author.id},
            )

            await db.commit()

        await ctx.send(
            f"{ctx.author.mention}, I have set your tag to: `{discord.utils.remove_markdown(input)}`"
        )

    @commands.command(aliases=["setregion", "spregion", "country"])
    async def region(self, ctx, *, input=None):
        """
        Sets your region on your smash profile.
        """
        if input is None:
            input = ""

        # tried to be as broad as possible here, hope thats enough
        if input.lower() in (
            "na",
            "north america",
            "usa",
            "us",
            "canada",
            "latin america",
            "america",
            "united states",
        ):
            input = "North America"
        elif input.lower() in (
            "east coast",
            "us east",
            "east",
            "midwest",
            "na east",
            "canada east",
        ):
            input = "NA East"
        elif input.lower() in (
            "west coast",
            "us west",
            "west",
            "na west",
            "canada west",
        ):
            input = "NA West"
        elif input.lower() in (
            "mexico",
            "south",
            "us south",
            "na south",
            "texas",
            "southern",
        ):
            input = "NA South"
        elif input.lower() in (
            "sa",
            "brazil",
            "argentina",
            "south america",
            "chile",
            "peru",
        ):
            input = "South America"
        elif input.lower() in ("eu", "europe", "uk", "england", "france", "germany"):
            input = "Europe"
        elif input.lower() in ("asia", "sea", "china", "japan", "india", "middle east"):
            input = "Asia"
        elif input.lower() in ("africa", "south africa", "egypt"):
            input = "Africa"
        elif input.lower() in ("australia", "new zealand", "nz", "au", "oceania"):
            input = "Oceania"
        elif input == "":
            pass
        else:
            await ctx.send("Please choose a valid region. Example: `%region Europe`")
            return

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET region = :region WHERE user_id = :user_id""",
                {"region": input, "user_id": ctx.author.id},
            )

            await db.commit()

        if input == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your region.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your region to: `{input}`"
            )

    @commands.command(aliases=["setnote", "spnote"])
    async def note(self, ctx, *, input=None):
        """
        Sets your note on your smash profile.
        """
        if input is None:
            input = ""

        # for a note, 150 chars seem enough to me
        input = input[:150]

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET note = :note WHERE user_id = :user_id""",
                {"note": input, "user_id": ctx.author.id},
            )

            await db.commit()

        if input == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your note.")
        else:
            await ctx.send(
                f"{ctx.author.mention}, I have set your note to: `{discord.utils.remove_markdown(input)}`"
            )

    @commands.command(aliases=["color", "spcolour", "spcolor", "setcolour", "setcolor"])
    async def colour(self, ctx, input):
        """
        Sets your embed colour on your smash profile.
        Uses a hex colour code.
        """
        # hex colour codes are 7 digits long and start with #
        if not input.startswith("#") or not len(input) == 7:
            await ctx.send(
                "Please choose a valid hex colour code. Example: `%colour #8a0f84`"
            )
            return

        input = input.replace("#", "0x")

        try:
            colour = int(input, 16)
        except ValueError:
            await ctx.send(
                "Please choose a valid hex colour code. Example: `%colour #8a0f84`"
            )
            return

        await self.make_new_profile(ctx.author)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET colour = :colour WHERE user_id = :user_id""",
                {"colour": colour, "user_id": ctx.author.id},
            )

            await db.commit()

        await ctx.send(f"{ctx.author.mention}, I have set your colour to: `{input}`")

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
                "Please choose a valid hex colour code. Example: `%colour #8a0f84`"
            )
        else:
            raise error


def setup(bot):
    bot.add_cog(Profile(bot))
    print("Profile cog loaded")
