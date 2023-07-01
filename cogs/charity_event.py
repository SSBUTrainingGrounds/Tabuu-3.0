import discord
from discord.ext import commands
from stringmatch import Match

import utils.check


class CharityEvent(commands.Cog):
    """This is a temporary cog for our 3 year anniversary charity event (August 2023).
    Lots of hardcoded stuff, because it's only meant to be temporary.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id = "1124740407721467995"
        self.message_id = "1124753047839588452"
        self.log_channel_id = "1124740470535360562"
        self.power_emoji = "<:2YR_POWER:1014906990851526727>"
        self.elegance_emoji = "<:2YR_ELEGANCE:1014906986657226813>"
        self.technique_emoji = "<:2YR_TECHNIQUE:1014906994664153088>"
        self.power_colour = discord.Colour.red()
        self.elegance_colour = discord.Colour.purple()
        self.technique_colour = discord.Colour.blue()

    async def edit_embed(
        self,
        guild_icon_url: str,
        input_house: str,
        points: int,
        set_points: bool = False,
    ) -> (str, int, int):
        match = Match(ignore_case=True, include_partial=True, latinise=True)

        all_houses = ["House of Power", "House of Elegance", "House of Technique"]

        house_match = match.get_best_match(input_house, all_houses, score=55)

        channel = await self.bot.fetch_channel(self.channel_id)
        message = await channel.fetch_message(self.message_id)

        embed = message.embeds[0]

        if house_match == "House of Power":
            index = 0
        elif house_match == "House of Elegance":
            index = 1
        else:
            index = 2

        points_field = embed.fields[index].value.split(" ")[0].replace("**", "")

        new_points = int(points_field) + points if not set_points else points

        embed.set_field_at(
            index=index,
            name=f"{embed.fields[index].name}",
            value=f"**{new_points}** Points",
        )

        embed.description = (
            "The current leaderboard for the Charity Event of August 2023.\n"
            f"*Last updated: {discord.utils.format_dt(discord.utils.utcnow())}*"
        )

        embed.set_thumbnail(url=guild_icon_url)

        await message.edit(embed=embed)

        return (house_match, int(points_field), new_points)

    async def log_point_changes(
        self,
        house: str,
        old_points: int,
        new_points: int,
        reason: str,
        author: discord.Member,
    ) -> None:
        channel = await self.bot.fetch_channel(self.log_channel_id)

        description = (
            f"**{house}**\n**Old Points:** {old_points}\n**New Points:** {new_points}"
        )

        if house == "House of Power":
            colour = self.power_colour
            emoji = self.bot.get_emoji(int(self.power_emoji.split(":")[2][:-1]))
        elif house == "House of Elegance":
            colour = self.elegance_colour
            emoji = self.bot.get_emoji(int(self.elegance_emoji.split(":")[2][:-1]))
        else:
            colour = self.technique_colour
            emoji = self.bot.get_emoji(int(self.technique_emoji.split(":")[2][:-1]))

        embed = discord.Embed(
            title="Point Change",
            description=description,
            color=colour,
        )

        try:
            embed.set_thumbnail(url=emoji.url)
        except AttributeError:
            pass

        embed.add_field(
            name="Reason",
            value=reason,
        )

        embed.set_footer(
            text=f"Changed by {author} ({author.id})", icon_url=author.avatar.url
        )

        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)

    @commands.command()
    @utils.check.is_moderator()
    async def addpoints(
        self,
        ctx: commands.Context,
        house: str,
        points: int,
        *,
        reason: str = "No reason provided.",
    ) -> None:
        """Adds points to a house, updating the leaderboard and logging the action.
        The house argument can be a partial match, and is case insensitive.
        """
        try:
            house_match, old_points, new_points = await self.edit_embed(
                ctx.guild.icon.url, house, points
            )

        except ValueError:
            await ctx.send(
                f"Sorry, I couldn't find a house with the name `{house}`. Please try again."
            )
            return

        await self.log_point_changes(
            house_match, old_points, new_points, reason, ctx.author
        )

    @commands.command()
    @utils.check.is_moderator()
    async def removepoints(
        self,
        ctx: commands.Context,
        house: str,
        points: int,
        *,
        reason: str = "No reason provided.",
    ) -> None:
        """Removes points from a house, updating the leaderboard and logging the action.
        The house argument can be a partial match, and is case insensitive.
        """
        try:
            house_match, old_points, new_points = await self.edit_embed(
                ctx.guild.icon.url, house, -points
            )
        except ValueError:
            await ctx.send(
                f"Sorry, I couldn't find a house with the name `{house}`. Please try again."
            )
            return

        await self.log_point_changes(
            house_match, old_points, new_points, reason, ctx.author
        )

    @commands.command()
    @utils.check.is_moderator()
    async def setpoints(
        self,
        ctx: commands.Context,
        house: str,
        points: int,
        *,
        reason: str = "No reason provided.",
    ) -> None:
        """Sets the points of a house to a given value, updating the leaderboard and logging the action.
        The house argument can be a partial match, and is case insensitive.
        """
        try:
            house_match, old_points, new_points = await self.edit_embed(
                ctx.guild.icon.url, house, points, set_points=True
            )
        except ValueError:
            await ctx.send(
                f"Sorry, I couldn't find a house with the name `{house}`. Please try again."
            )
            return

        await self.log_point_changes(
            house_match, old_points, new_points, reason, ctx.author
        )


# This will be commented out after the event is over.
async def setup(bot) -> None:
    await bot.add_cog(CharityEvent(bot))
    print("Charity Events cog loaded")
