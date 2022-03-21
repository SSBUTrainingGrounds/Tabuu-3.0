import discord
from discord.ext import commands
import json
from cogs.matchmaking import Matchmaking
from cogs.ranking import Ranking
from utils.ids import TGArenaChannelIDs
import utils.check


class Pings(discord.ui.Select):
    """
    Handles the Pings and Threads of our Matchmaking System.
    Both Ranked and Unranked.
    Also contains the Recentpings command with the Dropdown Menu.
    """

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Singles",
                description="Singles Pings in the last 30 Minutes",
                emoji="🗡️",
            ),
            discord.SelectOption(
                label="Doubles",
                description="Doubles Pings in the last 30 Minutes",
                emoji="⚔️",
            ),
            discord.SelectOption(
                label="Funnies",
                description="Funnies Pings in the last 30 Minutes",
                emoji="😂",
            ),
            discord.SelectOption(
                label="Ranked",
                description="Ranked Pings in the last 30 Minutes",
                emoji="🏆",
            ),
        ]

        super().__init__(
            placeholder="Which pings do you want to see?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Singles":
            timestamp = discord.utils.utcnow().timestamp()

            searches = Matchmaking.get_recent_pings(self, "singles", timestamp)

            singles_embed = discord.Embed(
                title="Singles pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.dark_red(),
            )

            await interaction.response.send_message(embed=singles_embed, ephemeral=True)

        elif self.values[0] == "Doubles":
            timestamp = discord.utils.utcnow().timestamp()

            searches = Matchmaking.get_recent_pings(self, "doubles", timestamp)

            doubles_embed = discord.Embed(
                title="Doubles pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.dark_blue(),
            )

            await interaction.response.send_message(embed=doubles_embed, ephemeral=True)

        elif self.values[0] == "Funnies":
            timestamp = discord.utils.utcnow().timestamp()

            searches = Matchmaking.get_recent_pings(self, "funnies", timestamp)

            funnies_embed = discord.Embed(
                title="Funnies pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.green(),
            )

            await interaction.response.send_message(embed=funnies_embed, ephemeral=True)

        elif self.values[0] == "Ranked":
            timestamp = discord.utils.utcnow().timestamp()

            searches = Ranking.get_recent_ranked_pings(self, timestamp)

            ranked_embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.blue(),
            )

            await interaction.response.send_message(embed=ranked_embed, ephemeral=True)

        else:
            await interaction.response.send_message(
                "Something went wrong! Please try again.", ephemeral=True
            )


class DropdownPings(discord.ui.View):
    """
    Adds the items to the Dropdown menu.
    """

    def __init__(self):
        super().__init__()
        self.add_item(Pings())


class Matchmakingpings(commands.Cog):
    def __init__(self, bot):
        """
        Clears the Matchmaking Pings on Startup.
        """
        self.bot = bot

        self.clear_mmrequests()

    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        # if a matchmaking thread gets inactive, it gets deleted right away to clear space
        if before.archived is False and after.archived is True:
            if (
                after.parent_id in TGArenaChannelIDs.PUBLIC_ARENAS
                or after.parent_id in TGArenaChannelIDs.RANKED_ARENAS
            ):
                await after.delete()

    @commands.command()
    async def recentpings(self, ctx):
        """
        Contains the Recentpings Dropdown Menu, where you can select each Matchmaking Type
        and get the according Pings of the Last 30 Minutes.
        """
        await ctx.send("Here are all available ping types:", view=DropdownPings())

    @commands.command(aliases=["clearmmrequests", "clearmm", "clearmatchmaking"])
    @utils.check.is_moderator()
    async def clearmmpings(self, ctx):
        """
        Clears the Matchmaking Pings manually, just in case.
        """
        self.clear_mmrequests()
        await ctx.send("Cleared the matchmaking pings!")

    @clearmmpings.error
    async def clearmmpings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    def clear_mmrequests(self):
        """
        Clears every Matchmaking Ping in the Singles, Doubles, Funnies and Ranked Files.
        """
        logger = self.bot.get_logger("bot.mm")
        logger.info("Starting to delete pings in the matchmaking files...")

        # deleting singles file

        with open(r"./json/singles.json", "r", encoding="utf-8") as f:
            singles = json.load(f)

        singles_requests = []

        for user in singles:
            singles_requests.append(user)

        for user in singles_requests:
            del singles[user]

        with open(r"./json/singles.json", "w", encoding="utf-8") as f:
            json.dump(singles, f, indent=4)

        logger.info("Singles file cleared!")

        # deleting doubles file

        with open(r"./json/doubles.json", "r", encoding="utf-8") as f:
            doubles = json.load(f)

        doubles_requests = []

        for user in doubles:
            doubles_requests.append(user)

        for user in doubles_requests:
            del doubles[user]

        with open(r"./json/doubles.json", "w", encoding="utf-8") as f:
            json.dump(doubles, f, indent=4)

        logger.info("Doubles file cleared!")

        # deleting funnies file

        with open(r"./json/funnies.json", "r", encoding="utf-8") as f:
            funnies = json.load(f)

        funnies_requests = []

        for user in funnies:
            funnies_requests.append(user)

        for user in funnies_requests:
            del funnies[user]

        with open(r"./json/funnies.json", "w", encoding="utf-8") as f:
            json.dump(funnies, f, indent=4)

        logger.info("Funnies file cleared!")

        # deleting ranked file

        with open(r"./json/rankedpings.json", "r", encoding="utf-8") as f:
            ranked = json.load(f)

        ranked_requests = []

        for user in ranked:
            ranked_requests.append(user)

        for user in ranked_requests:
            del ranked[user]

        with open(r"./json/rankedpings.json", "w", encoding="utf-8") as f:
            json.dump(ranked, f, indent=4)

        logger.info("Ranked file cleared!")


async def setup(bot):
    await bot.add_cog(Matchmakingpings(bot))
    print("Matchmakingpings cog loaded")
