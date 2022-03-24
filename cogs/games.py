import discord
from discord.ext import commands
from math import ceil
import random


class RpsButtons(discord.ui.View):
    """
    Contains the RPS Game Buttons.
    """

    def __init__(self, author, member):
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        self.message = None

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

    async def on_timeout(self):
        # if the match didnt go through as planned
        if self.authorchoice is None and self.memberchoice is None:
            await self.message.reply(
                "Match timed out! Both parties took too long to pick a choice!"
            )
        elif self.authorchoice is None:
            await self.message.reply(
                f"Match timed out! {self.author.mention} took too long to pick a choice!"
            )
        elif self.memberchoice is None:
            await self.message.reply(
                f"Match timed out! {self.member.mention} took too long to pick a choice!"
            )


class TicTacToeButtons(discord.ui.Button["TicTacToeGame"]):
    """
    Contains the TicTacToe Buttons.
    """

    def __init__(self, button_pos: int):
        super().__init__(
            style=discord.ButtonStyle.gray,
            label="\u200b",
            row=ceil((button_pos + 1) / 3),
        )
        self.button_pos = button_pos

    async def callback(self, interaction: discord.Interaction):
        await self.view.handle_turn(self, self.button_pos, interaction)


class TicTacToeGame(discord.ui.View):
    """
    Contains the TicTacToe Game Logic.
    """

    def __init__(self, author, member):
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.turn = author
        self.message = None
        # initialises the board
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # adds all of the buttons
        for i in range(0, 9):
            self.add_item(TicTacToeButtons(i))

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


class BlackJackButtons(discord.ui.View):
    def __init__(self, author, member):
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.author_hand = [[], 0]
        self.member_hand = [[], 0]
        self.folded = []
        self.turn = author
        self.message = None

    # all of the possible cards
    card_faces = [
        "Ace",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Jack",
        "Queen",
        "King",
    ]
    card_suites = ["♠️", "♦️", "♣️", "♥️"]

    def draw_card(self):
        card_deck = []
        for i, f in enumerate(self.card_faces):
            for s in self.card_suites:
                if i in (10, 11, 12):
                    i = 9
                card_deck.append([f"{f} of {s}", i + 1])

        card = random.choice(card_deck)

        if card[0] in (self.author_hand[0] or self.member_hand[0]):
            try:
                self.draw_card()
            except RecursionError:
                return

        if self.turn == self.author:
            if card[1] == 1:
                if self.author_hand[1] + 11 <= 21:
                    card[1] = 11
            self.author_hand[0].append(card[0])
            self.author_hand[1] += card[1]
        else:
            if card[1] == 1:
                if self.member_hand[1] + 11 <= 21:
                    card[1] = 11
            self.member_hand[0].append(card[0])
            self.member_hand[1] += card[1]

    def get_winner(self):
        if self.author_hand[1] > 21 >= self.member_hand[1]:
            return self.member

        if self.member_hand[1] > 21 >= self.author_hand[1]:
            return self.author

        if self.member_hand[1] == self.author_hand[1] or (
            self.author_hand[1] > 21 and self.member_hand[1] > 21
        ):
            return None

        if self.author_hand[1] > self.member_hand[1]:
            return self.author

        return self.member

    async def end_game(self):
        self.stop()

        if self.get_winner():
            await self.message.reply(f"The winner is {self.get_winner().mention}!")
        else:
            await self.message.reply("The game is tied!")

    @discord.ui.button(
        label="Draw a Card", emoji="🃏", style=discord.ButtonStyle.blurple
    )
    async def draw(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Draws another card and checks if the players turn is over.
        """
        self.draw_card()

        if self.turn == self.author:
            if self.author_hand[1] > 20:
                await self.end_game()
            if self.member not in self.folded:
                self.turn = self.member
        else:
            if self.member_hand[1] > 20:
                await self.end_game()
            if self.author not in self.folded:
                self.turn = self.author

        await interaction.response.edit_message(
            content=f"{self.author.mention}'s Hand: {', '.join(self.author_hand[0])} ({self.author_hand[1]})\n"
            f"{self.member.mention}'s Hand: {', '.join(self.member_hand[0])} ({self.member_hand[1]})\n\n"
            f"It is {self.turn.mention}'s Turn.",
            view=self,
        )

    @discord.ui.button(label="Fold", emoji="❌", style=discord.ButtonStyle.red)
    async def fold(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Folds and switches the turn, or exits the game.
        """
        if self.turn == self.author:
            self.folded.append(self.author)
            self.turn = self.member
        else:
            self.folded.append(self.member)
            self.turn = self.author

        if all(x in self.folded for x in [self.member, self.author]):
            await self.end_game()

        await interaction.response.edit_message(
            content=f"{self.author.mention}'s Hand: {', '.join(self.author_hand[0])} ({self.author_hand[1]})\n"
            f"{self.member.mention}'s Hand: {', '.join(self.member_hand[0])} ({self.member_hand[1]})\n\n"
            f"It is {self.turn.mention}'s Turn.",
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user in (self.author, self.member):
            return False
        if interaction.user == self.author and self.turn == self.author:
            return True
        if interaction.user == self.member and self.turn == self.member:
            return True
        return False

    async def on_timeout(self):
        await self.message.reply(
            f"The match timed out! {self.turn.mention} took too long to pick a choice!"
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
        view.message = await ctx.send(
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
            await view.message.reply(
                f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**It's a draw!**"
            )
            return

        author_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {ctx.author.mention}!**"
        member_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {member.mention}!**"

        # since draws are already ruled out the rest of the logic isnt too bad, still a whole lot of elif statements though
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

        view = TicTacToeGame(ctx.author, member)
        # we reply to that message in the timeout event
        view.message = await ctx.send(
            f"{ctx.author.mention}: ❌\n{member.mention}: ⭕\n\n{ctx.author.mention}'s Turn:",
            view=view,
        )

    @commands.command(aliases=["21", "vingtetun", "vingtun"])
    async def blackjack(self, ctx, member: discord.Member):
        """
        Starts a game of Blackjack vs another User.
        """
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

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Games cog loaded")
