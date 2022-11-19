import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.ids import GuildIDs
from views._2048 import _2048Game
from views.blackjack import BlackJackButtons
from views.memory import MemoryGame
from views.minesweeper import MinesweeperGame
from views.rps import RpsButtons
from views.ttt import TicTacToeGame


class Games(commands.Cog):
    """Contains the commands to execute the Games."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Never heard of those alternate names but wikipedia says they exist so might as well add them.
    @commands.hybrid_command(aliases=["rockpaperscissors", "rochambeau", "roshambo"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to play against.")
    async def rps(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Plays a Game of Rock, Paper, Scissors with a mentioned user.
        Or the bot, if you do not mention a user.
        """
        if member is None:
            member = self.bot.user

        # Basic checks for users.
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot and member.id != self.bot.user.id:
            await ctx.send(
                "Please do not play with other bots, they are too predictable."
            )
            return

        view = RpsButtons(ctx.author, member)
        view.message = await ctx.send(
            f"Rock, Paper, Scissors: \n{ctx.author.mention} vs {member.mention}\nChoose wisely:",
            view=view,
        )

        # If the bot plays it just chooses randomly.
        if member.id == self.bot.user.id:
            view.memberchoice = random.choice(["Rock", "Paper", "Scissors"])

        # Waits for the button to stop or timeout.
        await view.wait()

        # Checks the results.
        # If its the same we can just call it off here,
        # need a check if one of the responses is not none for the error message below.
        if view.authorchoice == view.memberchoice and view.authorchoice is not None:
            await view.message.reply(
                f"{ctx.author.mention} chose {view.authorchoice}!\n"
                f"{member.mention} chose {view.memberchoice}!\n"
                "**It's a draw!**"
            )
            return

        author_winner_message = (
            f"{ctx.author.mention} chose {view.authorchoice}!\n"
            f"{member.mention} chose {view.memberchoice}!\n"
            f"**The winner is: {ctx.author.mention}!**"
        )

        member_winner_message = (
            f"{ctx.author.mention} chose {view.authorchoice}!\n"
            f"{member.mention} chose {view.memberchoice}!\n"
            f"**The winner is: {member.mention}!**"
        )

        # Since draws are already ruled out the rest of the logic isnt too bad,
        # still a whole lot of elif statements though.
        if view.authorchoice == "Rock":
            if view.memberchoice == "Paper":
                await view.message.reply(member_winner_message)
            elif view.memberchoice == "Scissors":
                await view.message.reply(author_winner_message)

        elif view.authorchoice == "Paper":
            if view.memberchoice == "Scissors":
                await view.message.reply(member_winner_message)
            elif view.memberchoice == "Rock":
                await view.message.reply(author_winner_message)

        elif view.authorchoice == "Scissors":
            if view.memberchoice == "Rock":
                await view.message.reply(member_winner_message)
            elif view.memberchoice == "Paper":
                await view.message.reply(author_winner_message)

    @commands.hybrid_command(aliases=["ttt"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to play against.")
    async def tictactoe(self, ctx: commands.Context, member: discord.Member) -> None:
        """Starts a game of Tic Tac Toe vs another User."""
        # Basic checks for users.
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot:
            await ctx.send("Please do not play matches with bots!")
            return

        view = TicTacToeGame(ctx.author, member)
        # We reply to that message in the timeout event.
        view.message = await ctx.send(
            f"{ctx.author.mention}: ❌\n{member.mention}: ⭕\n\n{ctx.author.mention}'s Turn:",
            view=view,
        )

    @commands.hybrid_command(aliases=["21", "vingtetun", "vingtun"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to play against.")
    async def blackjack(self, ctx: commands.Context, member: discord.Member) -> None:
        """Starts a game of Blackjack vs another User."""

        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot:
            await ctx.send("Please do not play matches with bots!")
            return

        view = BlackJackButtons(ctx.author, member)

        view.message = await ctx.send(
            f"{ctx.author.mention}'s Hand: Empty (0)\n{member.mention}'s Hand: Empty (0)\n\nIt is {view.turn.mention}'s Turn.",
            view=view,
        )

    @commands.hybrid_command(name="2048")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def _2048(self, ctx: commands.Context) -> None:
        """Starts a game of 2048."""

        view = _2048Game(ctx.author)
        await ctx.send(f"{ctx.author.mention}'s score: {view.score}", view=view)

        timeout = await view.wait()

        if timeout:
            message = (
                f"Your game timed out! Thanks for playing.\nFinal score: {view.score}"
            )

        elif view.win:
            message = "Congratulations! You win!\n" f"Final score: {view.score}"

        else:
            message = (
                "Too bad, but you will win next time! Thanks for playing.\n"
                f"Final score: {view.score}"
            )

        # We have 15 minutes to reply to the message,
        # if the game goes on for longer, which is a common possibility,
        # we cant reply to it anymore, which i would prefer but oh well.
        try:
            await ctx.reply(message)
        except discord.HTTPException:
            # We wanna mention the user if we cant reply.
            await ctx.send(f"{ctx.author.mention} {message}")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to play against.")
    async def memory(self, ctx: commands.Context, member: discord.Member) -> None:
        """Plays a game of memory with the mentioned member."""
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot:
            await ctx.send("Please do not play matches with bots!")
            return

        view = MemoryGame(ctx.author, member)

        view.message = await ctx.send(
            f"Memory:\n🟦{ctx.author.mention} vs. 🟩{member.mention}\n{member.mention}'s turn:",
            view=view,
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(mine_count="The amount of mines, from 2-12 (Default: 5).")
    async def minesweeper(
        self, ctx: commands.Context, mine_count: commands.Range[int, 2, 12] = 5
    ) -> None:
        """Starts a game of Minesweeper."""
        view = MinesweeperGame(ctx.author, mine_count)

        view.message = await ctx.send(
            f"💣 Minesweeper ({mine_count} Bombs) 💣", view=view
        )

    @minesweeper.error
    async def minesweeper_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please input a mine count between 2 and 12!")


async def setup(bot) -> None:
    await bot.add_cog(Games(bot))
    print("Games cog loaded")
