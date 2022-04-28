import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands
from googletrans import Translator

import utils.conversion
from utils.ids import GuildIDs


class Usercommands(commands.Cog):
    """
    Mostly contains various commands which did not fit with the others.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def ping(self, ctx):
        """
        Gets you the ping of the bot in milliseconds.
        """
        pingtime = self.bot.latency * 1000
        await ctx.send(f"Ping: {round(pingtime)}ms")

    @commands.hybrid_command(aliases=["coinflip", "flipcoin", "flip"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def coin(self, ctx):
        """
        Tosses a coin.
        """
        coin = ["Coin toss: **Heads!**", "Coin toss: **Tails!**"]
        await ctx.send(random.choice(coin))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def stagelist(self, ctx):
        """
        Picture with our stagelist on it.
        We dont send a link because that could change over time.
        An image saved locally is just more reliable.
        Although it is around 700kb big and we do have to send it every time.
        """
        await ctx.send(file=discord.File(r"./files/stagelist.png"))

    @commands.hybrid_command(aliases=["r"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(dice="The dice to roll, in NdN format. Example: 2d20")
    async def roll(self, ctx, dice: str):
        """
        A dice roll, in NdN format.
        """
        try:
            amount, sides = map(int, dice.split("d"))
        except ValueError:
            await ctx.send(
                f"Wrong format!\n"
                f"Try something like: `{self.bot.command_prefix}roll 1d100`"
            )
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

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(count="The number to count down from.")
    async def countdown(self, ctx, count: int):
        """
        Counts down from a number less than 50.
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

    @commands.hybrid_command(aliases=["icon"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to see the avatar of.")
    async def avatar(self, ctx, member: discord.Member = None):
        """
        Gets you the avatar of a mentioned member, or yourself.
        """
        if member is None:
            member = ctx.author
        await ctx.send(member.display_avatar.url)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to see the banner of.")
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

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        question="Your question for the poll.",
    )
    async def poll(self, ctx: commands.Context, *, question: str):
        """
        Creates a new poll with 2 to 5 options.
        Sends a button, which if you click it, opens a modal to submit the options.
        Afterwards sends out an embed with the poll and reacts with the reactions.
        """

        # some basic check for ridiculous question lengths
        if len(question[250:]) > 0:
            await ctx.send("The maximum length for the question is 250 characters.")
            return

        # for some fields we can only have a very short maximum
        # however some questions are just longer than that.
        # so we provide a shortened form for those fields.
        shortened_question = question

        if len(question[45:]) > 0:
            shortened_question = f"{question[:42]}..."

        # the emojis which will be used for reacting to the poll message
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # the modal for filling out the poll options.
        # we define it in the function so we have access to the needed variables.
        class PollOptions(discord.ui.Modal, title=shortened_question):
            def __init__(self):
                super().__init__()
                self.add_item(
                    discord.ui.TextInput(
                        label="The options for your poll. One in each line.",
                        placeholder="Enter between 2 and 10 options, separated by new lines.",
                        style=discord.TextStyle.paragraph,
                        required=True,
                        max_length=2000,
                    )
                )

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.send_message(
                    "Creating poll...", ephemeral=True
                )

                options = self.children[0].value.split("\n")

                if len(options) < 2:
                    await interaction.followup.send(
                        "Please enter at least 2 options for your poll.",
                        ephemeral=True,
                    )
                    return

                if len(options) > 10:
                    await interaction.followup.send(
                        "You entered too many options for the poll! Maximum is 10.",
                        ephemeral=True,
                    )
                    return

                embed_description = [
                    f"{reactions[i]}: {option}" for i, option in enumerate(options)
                ]

                embed = discord.Embed(
                    title=question,
                    colour=discord.Colour.dark_purple(),
                    description="\n".join(embed_description),
                )
                embed.set_footer(
                    text=f"Poll created by {str(ctx.author)}",
                )

                embed_message = await ctx.send(embed=embed)

                for reaction in reactions[: len(options)]:
                    await embed_message.add_reaction(reaction)

        # we can only send a modal through an interaction, so we need this middle step of creating a button.
        # theoretically we only need this when you use a normal text based command,
        # but to keep them both the same we just do it no matter what.
        class PollButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(label=f"Select the options for: {shortened_question}.")
            async def poll_button(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                await interaction.response.send_modal(PollOptions())
                self.stop()

            async def interaction_check(self, interaction: discord.Interaction):
                return interaction.user == ctx.author

        view = PollButton()

        button_message = await ctx.send(view=view)

        await view.wait()

        # cleaning up afterwards.
        try:
            await button_message.delete()
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.hybrid_command(aliases=["emote"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(emoji="The emoji you want to see the stats of.")
    async def emoji(self, ctx, emoji: str):
        """
        Gives you information about an Emoji.
        """
        # since discord doesnt allow emojis as an argument,
        # we convert it ourselves with the partial emoji converter.
        # we are using the partial converter because the normal converter can only get
        # emojis from the bots servers, and we want to be able to get every emoji.
        partial_converter = commands.PartialEmojiConverter()
        emoji = await partial_converter.convert(ctx, emoji)

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
        Also you cant send a message together with a Sticker on Mobile or with Slash Commands,
        so this command only works as a text-based command on Desktop, unfortunately.
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

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member you want to see the current spotify listening status of."
    )
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

    @commands.hybrid_command(aliases=["currenttime"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def time(self, ctx):
        """
        Shows the current time as a timezone aware object.
        """
        await ctx.send(
            f"The current time is: {discord.utils.format_dt(discord.utils.utcnow(), style='T')}"
        )

    @commands.hybrid_command(aliases=["conversion"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        conversion_input="The input you want to convert to metric or imperial."
    )
    async def convert(self, ctx, *, conversion_input: str):
        """
        Converts your input between metric and imperial
        and the other way around.
        Works with most commonly used measurements.
        """
        await ctx.send(utils.conversion.convert_input(conversion_input))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(message="The string or message to translate.")
    async def translate(self, ctx, *, message: str = None):
        """
        Translates a message from any language to english.
        Specify a string to translate, or a message to translate by either using message ID/Link,
        or replying to a message.
        Attempts to guess the original language.
        """
        # first we check if the user is replying to a message
        if ctx.message.reference and not message:
            fetched_message = await ctx.channel.fetch_message(
                ctx.message.reference.message_id
            )
            message = fetched_message.content

        # similar to the emoji command, we have to use the converter ourselves here,
        # instead of just typehinting a Union of Message and str and letting discord.py handle it.
        try:
            message_converter = commands.MessageConverter()
            fetched_message = await message_converter.convert(ctx, message)
            message = fetched_message.content
        except commands.CommandError:
            pass

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
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send(
                "Please provide a question for your poll.\n"
                f"Example: `{self.bot.command_prefix}poll What is your favourite colour?`"
            )
        else:
            raise error

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Wrong format!\n"
                f"Try something like: `{self.bot.command_prefix}roll 1d100`"
            )
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

    @emoji.error
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
        if isinstance(
            error,
            (
                commands.MissingRequiredArgument,
                commands.CommandInvokeError,
                commands.HybridCommandError,
            ),
        ):
            await ctx.send("Invalid input! Please try again.")
        else:
            raise error

    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Please translate a valid message or string.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Usercommands(bot))
    print("Usercommands cog loaded")
