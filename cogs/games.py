import discord
from discord.ext import commands
import random


class RpsButtons(discord.ui.View):
    """
    Contains the RPS Game Buttons.
    """

    def __init__(self, author, member):
        super().__init__()
        self.author = author
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        # set it to 1 min, default one was 3 mins thought that was a bit too long
        self.timeout = 60

    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.gray)
    async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Registers the author and user input for Rock.
        Stops if both parties made a choice.
        I dont know why the Rock Emoji doesnt display properly here btw,
        it does on Discord.
        """
        await interaction.response.send_message("You chose Rock!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Rock"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Rock"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Paper", emoji="📝", style=discord.ButtonStyle.gray)
    async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Registers the author and user input for Paper.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Paper!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Paper"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Paper"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.gray)
    async def scissors(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """
        Registers the author and user input for Scissors.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Scissors!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Scissors"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Scissors"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        # basically ignores every other member except the author and mentioned member
        return interaction.user in (self.member, self.author)


class TicTacToeButtons(discord.ui.View):
    """
    Contains the TicTacToe Buttons and Game Logic.
    """

    def __init__(self, author, member):
        super().__init__()
        self.author = author
        self.member = member
        self.turn = author
        # the timeout refreshes every time someone presses a button,
        # so 1 minute is more than enough.
        self.timeout = 60

    # initialises the board
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def check_for_winner(self, board):
        """
        Checks if there is a winner, a tie or if the game is still going on.
        """
        winning_combinations = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        # checks for the winner and returns it, if found
        for combination in winning_combinations:
            winning_list = []

            for position in combination:
                winning_list.append(board[position])

            if winning_list == [1, 1, 1]:
                return self.author

            if winning_list == [2, 2, 2]:
                return self.member

        # if theres a tie we return false
        if not 0 in board:
            return False

        return None

    async def game_ending(self, interaction: discord.Interaction):
        """
        Handles the game ending for us.
        """
        winner = self.check_for_winner(self.board)

        if winner is not None:
            self.stop()
            if winner is False:
                await interaction.message.reply(content="The game is tied!")
            else:
                await interaction.message.reply(
                    content=f"The winner is: {winner.mention}!"
                )

    async def handle_turn(
        self,
        button: discord.ui.Button,
        button_id: int,
        interaction: discord.Interaction,
    ):
        """
        The logic for one turn.
        """
        if interaction.user.id == self.author.id:
            self.board[button_id] = 1
            button.emoji = "❌"
            button.style = discord.ButtonStyle.red
            self.turn = self.member
        if interaction.user.id == self.member.id:
            self.board[button_id] = 2
            button.emoji = "⭕"
            button.style = discord.ButtonStyle.blurple
            self.turn = self.author

        await self.game_ending(interaction)

        button.disabled = True

        await interaction.response.edit_message(
            content=f"{self.author.mention}: ❌\n{self.member.mention}: ⭕\n\n{self.turn.mention}'s Turn:",
            view=self,
        )

    # the buttons, very repetitive
    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=1)
    async def button_one(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 0, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=1)
    async def button_two(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 1, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=1)
    async def button_three(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 2, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=2)
    async def button_four(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 3, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=2)
    async def button_five(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 4, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=2)
    async def button_six(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 5, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=3)
    async def button_seven(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 6, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=3)
    async def button_eight(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 7, interaction)

    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.gray, row=3)
    async def button_nine(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.handle_turn(button, 8, interaction)

    async def interaction_check(self, interaction: discord.Interaction):
        # checks if the user is in the game
        if not interaction.user in (self.member, self.author):
            return False
        # checks if its your turn
        if interaction.user == self.author and self.turn == self.author:
            self.turn = self.member
            return True
        if interaction.user == self.member and self.turn == self.member:
            self.turn = self.author
            return True
        return False

    async def on_timeout(self):
        await self.message.reply(
            f"Match timed out! {self.turn.mention} took too long to pick something!"
        )


class Games(commands.Cog):
    """
    Contains the commands to execute the Games.
    """

    def __init__(self, bot):
        self.bot = bot

    # never heard of those alternate names but wikipedia says they exist so might as well add them
    @commands.command(aliases=["rockpaperscissors", "rochambeau", "roshambo"])
    async def rps(self, ctx, member: discord.Member = None):
        """
        Plays a Game of Rock, Paper, Scissors with either a mentioned user,
        or the bot, if you do not mention a user.
        """
        if member is None:
            member = self.bot.user

        # basic checks for users
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot and member.id != self.bot.user.id:
            await ctx.send(
                "Please do not play with other bots, they are too predictable."
            )
            return

        view = RpsButtons(ctx.author, member)
        init_message = await ctx.send(
            f"Rock, Paper, Scissors: \n{ctx.author.mention} vs {member.mention}\nChoose wisely:",
            view=view,
        )

        # if the bot plays it just chooses randomly
        if member.id == self.bot.user.id:
            view.memberchoice = random.choice(["Rock", "Paper", "Scissors"])

        # waits for the button to stop or timeout
        await view.wait()

        # checks the results
        # if its the same we can just call it off here,
        # need a check if one of the responses is not none for the error message below
        if view.authorchoice == view.memberchoice and view.authorchoice is not None:
            await init_message.reply(
                f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**It's a draw!**"
            )
            return

        author_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {ctx.author.mention}!**"
        member_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {member.mention}!**"

        # since draws are already ruled out the rest of the logic isnt too bad, still a whole lot of elif statements though
        if view.authorchoice == "Rock":
            if view.memberchoice == "Paper":
                await init_message.reply(member_winner_message)
            elif view.memberchoice == "Scissors":
                await init_message.reply(author_winner_message)

        elif view.authorchoice == "Paper":
            if view.memberchoice == "Scissors":
                await init_message.reply(member_winner_message)
            elif view.memberchoice == "Rock":
                await init_message.reply(author_winner_message)

        elif view.authorchoice == "Scissors":
            if view.memberchoice == "Rock":
                await init_message.reply(member_winner_message)
            elif view.memberchoice == "Paper":
                await init_message.reply(author_winner_message)

        # if the match didnt go through as planned:
        elif view.authorchoice is None and view.memberchoice is None:
            await init_message.reply(
                "Match timed out! Both parties took too long to pick a choice!"
            )
        elif view.authorchoice is None:
            await init_message.reply(
                f"Match timed out! {ctx.author.mention} took too long to pick a choice!"
            )
        elif view.memberchoice is None:
            await init_message.reply(
                f"Match timed out! {member.mention} took too long to pick a choice!"
            )

        # and the fallback
        else:
            await init_message.reply("Something went wrong! Please try again.")

    @commands.command(aliases=["ttt"])
    async def tictactoe(self, ctx, member: discord.Member):
        """
        Starts a game of Tic Tac Toe vs another User.
        """
        # basic checks for users
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot:
            await ctx.send("Please do not play matches with bots!")
            return

        view = TicTacToeButtons(ctx.author, member)
        # we reply to that message in the timeout event
        view.message = await ctx.send(
            f"{ctx.author.mention}: ❌\n{member.mention}: ⭕\n\n{ctx.author.mention}'s Turn:",
            view=view,
        )

    # basic error handling
    @rps.error
    async def rps_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @tictactoe.error
    async def tictactoe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Games cog loaded")
