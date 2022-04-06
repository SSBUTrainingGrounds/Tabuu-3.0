import asyncio
import random
from typing import Union

import discord
from discord.ext import commands
from googletrans import Translator

import utils.conversion


class Usercommands(commands.Cog):
    """
    Mostly contains various commands which did not fit with the others.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Classic ping command.
        """
        pingtime = self.bot.latency * 1000
        await ctx.send(f"Ping: {round(pingtime)}ms")

    @commands.command()
    async def coin(self, ctx):
        """
        Generic coin toss.
        """
        coin = ["Coin toss: **Heads!**", "Coin toss: **Tails!**"]
        await ctx.send(random.choice(coin))

    @commands.command()
    async def stagelist(self, ctx):
        """
        Picture with our stagelist on it.
        We dont send a link because that could change over time.
        An image saved locally is just more reliable.
        Although it is around 700kb big and we do have to send it every time.
        """
        await ctx.send(file=discord.File(r"./files/stagelist.png"))

    @commands.command(aliases=["r"])
    async def roll(self, ctx, dice: str):
        """
        A dice roll, in NdN format.
        """
        try:
            amount, sides = map(int, dice.split("d"))
        except ValueError:
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
            return

        results = []
        if amount > 100:
            await ctx.send("Too many dice!")
            return
        if sides > 1000:
            await ctx.send("Too many sides!")
            return
        for r in range(amount):
            x = random.randint(1, sides)
            results.append(x)
        if len(results) == 1:
            await ctx.send(f"Rolling **1**-**{sides}** \nResult: **{results}**")
        else:
            await ctx.send(
                f"Rolling **1**-**{sides}** **{r+1}** times \nResults: **{results}** \nTotal: **{sum(results)}**"
            )

    @commands.command()
    async def countdown(self, ctx, count: int):
        """
        Counts down from a number < 50.
        """
        if count > 50:
            await ctx.send("Maximum limit is 50.")
            return
        if count < 1:
            await ctx.send("Invalid number!")
            return

        initial_count = count

        countdown_message = await ctx.send(
            f"Counting down from {initial_count}...\n{count}"
        )

        while count > 1:
            count -= 1
            await asyncio.sleep(2)
            await countdown_message.edit(
                content=f"Counting down from {initial_count}...\n{count}"
            )

        await asyncio.sleep(2)
        await countdown_message.edit(
            content=f"Counting down from {initial_count}...\nFinished!"
        )

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """
        Gets you the avatar of a mentioned member, or yourself.
        """
        if member is None:
            member = ctx.author
        await ctx.send(member.display_avatar.url)

    @commands.command()
    async def banner(self, ctx, member: discord.Member = None):
        """
        Gets you the banner of a mentioned member, or yourself.
        """
        if member is None:
            member = ctx.author
        # we have to fetch the user first for whatever reason
        user = await self.bot.fetch_user(member.id)
        # if the user does not have a banner, we get an error referencing it
        if user.banner:
            await ctx.send(user.banner.url)
        else:
            await ctx.send("This user does not have a banner.")

    @commands.command()
    async def poll(self, ctx, question, *options: str):
        """
        Poll command, with up to 10 options.
        Sends it out in a neat embed and adds the reactions.
        """
        if len(options) < 2:
            await ctx.send("You need at least 2 options to make a poll!")
            return
        if len(options) > 10:
            await ctx.send("You can only have 10 options at most!")
            return
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        reactions = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "0️⃣",
        ]
        description = []

        for x, option in enumerate(options):
            description += f"\n{reactions[x]}: {option}"
        embed = discord.Embed(
            title=question,
            description="".join(description),
            colour=discord.Colour.dark_purple(),
        )
        embed.set_footer(text=f"Poll by {ctx.author}")
        embed_message = await ctx.send(embed=embed)
        for reaction in reactions[: len(options)]:
            await embed_message.add_reaction(reaction)

    @commands.command(aliases=["emoji"])
    async def emote(self, ctx, emoji: discord.PartialEmoji):
        """
        Gives you information about an Emoji.
        """
        embed = discord.Embed(
            title="Emoji Info",
            colour=discord.Colour.orange(),
            description=f"\
**Url:** {emoji.url}\n\
**Name:** {emoji.name}\n\
**ID:** {emoji.id}\n\
**Created at:** {discord.utils.format_dt(emoji.created_at, style='F')}\n\
            ",
        )
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def sticker(self, ctx):
        """
        Gives you information about a Sticker.
        Note that Stickers work very differently from Emojis.
        They count as a message attachment, so we fetch the first of those.
        Also you cant send a message together with a Sticker on Mobile,
        so this command is straight up useless on anything other than Desktop.
        """
        sticker = await ctx.message.stickers[0].fetch()
        embed = discord.Embed(
            title="Sticker Info",
            colour=discord.Colour.orange(),
            description=f"\
**Url:** {sticker.url}\n\
**Name:** {sticker.name}\n\
**ID:** {sticker.id}\n\
**Created at:** {discord.utils.format_dt(sticker.created_at, style='F')}\n\
            ",
        )
        embed.set_image(url=sticker.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def spotify(self, ctx, member: discord.Member = None):
        """
        Posts the Spotify Song Link the member (or yourself) is listening to.
        You need to enable the feature that displays the current Song as your Activity for this to work.
        Still is finicky on Mobile though.
        """
        if member is None:
            member = ctx.author

        if not ctx.guild:
            await ctx.send("This command does not work in my DM channel.")
            return

        listeningstatus = next(
            (
                activity
                for activity in member.activities
                if isinstance(activity, discord.Spotify)
            ),
            None,
        )

        if listeningstatus is None:
            await ctx.send(
                "This user is not listening to Spotify right now or their account is not connected."
            )
        else:
            await ctx.send(f"https://open.spotify.com/track/{listeningstatus.track_id}")

    @commands.command(aliases=["currenttime"])
    async def time(self, ctx):
        """
        Shows the current time as a timezone aware object.
        """
        await ctx.send(
            f"The current time is: {discord.utils.format_dt(discord.utils.utcnow(), style='T')}"
        )

    @commands.command(aliases=["conversion"])
    async def convert(self, ctx, *, conversion_input):
        """
        Converts your input between metric and imperial
        and the other way around.
        Works with most commonly used measurements.
        """
        await ctx.send(utils.conversion.convert_input(conversion_input))

    @commands.command()
    async def translate(self, ctx, *, message: Union[discord.Message, str] = None):
        """
        Translates a message from any language to english.
        Specify a string to translate, or a message to translate by either using message ID/Link,
        or replying to a message.
        Attempts to guess the original language.
        """
        # first we check if the user is replying to a message
        if ctx.message.reference and not message:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        # then we get the actual content to translate
        if isinstance(message, discord.Message):
            message = message.content

        # checks if the message is empty if either the user failed to specify anything
        # or if the message content of the message specified is empty
        if not message:
            await ctx.send("You need to specify a message to translate!")
            return

        translation = Translator().translate(f"{message}", dest="en")

        embed = discord.Embed(title="Translation", colour=0x007377)
        embed.add_field(
            name=f"Original Text ({translation.src}):",
            value=translation.origin[:1000],
            inline=False,
        )
        embed.add_field(
            name="Translated Text (en):", value=translation.text[:1000], inline=False
        )

        await ctx.send(embed=embed)

    # error handling for the above
    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @banner.error
    async def banner_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You need to specify a question, and then at least 2 options!"
            )
        else:
            raise error

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
        else:
            raise error

    @countdown.error
    async def countdown_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a number!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid number!")
        else:
            raise error

    @emote.error
    async def emote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify an emoji!")
        elif isinstance(error, commands.PartialEmojiConversionFailure):
            await ctx.send(
                "I couldn't find information on this emoji! Make sure this is not a default emoji."
            )
        else:
            raise error

    @sticker.error
    async def sticker_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I could not find any information on this sticker!")
        else:
            raise error

    @spotify.error
    async def spotify_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @convert.error
    async def convert_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Invalid input! Please try again.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid input! Please try again.")
        else:
            raise error

    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Please translate a valid message or string.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Usercommands(bot))
    print("Usercommands cog loaded")
