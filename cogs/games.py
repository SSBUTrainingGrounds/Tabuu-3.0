import random
from math import ceil, floor
from typing import Optional

import discord
from discord.ext import commands


class RpsButtons(discord.ui.View):
    """
    Contains the RPS Game Buttons.
    """

    def __init__(self, author: discord.Member, member: discord.Member):
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        self.message = None

    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.gray)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
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
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
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

    def __init__(self, author: discord.Member, member: discord.Member):
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.turn = author
        self.message = None
        # initialises the board
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # adds all of the buttons
        for i in range(9):
            self.add_item(TicTacToeButtons(i))

    def check_for_winner(self, board: list[int]):
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
            winning_list = [board[position] for position in combination]

            if winning_list == [1, 1, 1]:
                return self.author

            if winning_list == [2, 2, 2]:
                return self.member

        # if theres a tie we return false
        if 0 not in board:
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
        if interaction.user not in (self.member, self.author):
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
    def __init__(self, author: discord.Member, member: discord.Member):
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

        # checks if the card is already present in one hand, if so repeats the process
        # i read that in real life blackjack is played with like 8 decks at once
        # so this really isnt even needed
        if card[0] in self.author_hand[0] or card[0] in self.member_hand[0]:
            try:
                self.draw_card()
                return
            except RecursionError:
                return

        if self.turn == self.author:
            # if the card is an ace, checks if it should be worth 11 or 1
            if card[1] == 1 and self.author_hand[1] <= 10:
                card[1] = 11
            self.author_hand[0].append(card[0])
            self.author_hand[1] += card[1]
        else:
            if card[1] == 1 and self.member_hand[1] <= 10:
                card[1] = 11
            self.member_hand[0].append(card[0])
            self.member_hand[1] += card[1]

    def get_winner(self):
        # checks for values greater than 21
        if self.author_hand[1] > 21 >= self.member_hand[1]:
            return self.member

        if self.member_hand[1] > 21 >= self.author_hand[1]:
            return self.author

        # checks for draws
        if self.member_hand[1] == self.author_hand[1]:
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
    async def draw(self, interaction: discord.Interaction, button: discord.ui.Button):
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
    async def fold(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        if interaction.user not in (self.author, self.member):
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


class _2048Buttons(discord.ui.Button["_2048Game"]):
    """
    The actual buttons that are used as game tiles.
    """

    def __init__(self, button_pos: int, label: str):
        super().__init__(
            style=discord.ButtonStyle.gray,
            label=label,
            row=floor((button_pos) / 4),
        )
        self.button_pos = button_pos
        self.disabled = True
        # we need to track the column of the button ourselves.
        self.column = button_pos % 4


class _2048Game(discord.ui.View):
    """
    Contains the logic for the game.
    """

    def __init__(self, player):
        super().__init__(timeout=60)
        self.player = player
        self.win = False
        self.score = 0
        for i in range(16):
            self.add_item(_2048Buttons(i, self.empty_label))
        # only the game buttons, without the menu ones.
        self.game_tiles = [button for button in self.children if not button.emoji]
        # the game starts off with 2 tiles set to "2".
        for _ in range(2):
            self.spawn_new_tile()

    # a zero-width space character.
    empty_label = "\u200b"

    @discord.ui.button(
        label=empty_label, emoji="⬅️", style=discord.ButtonStyle.blurple, row=4
    )
    async def left(self, interaction: discord.Interaction, button: discord.Button):
        """
        Shifts the game tiles to the left.
        """
        tiles = []
        for i in range(4):
            row = [button for button in self.game_tiles if button.row == i]
            # for left and for up we have to reverse the row/column.
            row.reverse()
            tiles.extend([row])

        # also we need to call the turn in reverse so it merges correctly.
        self.turn(tiles, reverse=True)

        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    @discord.ui.button(
        label=empty_label, emoji="⬆️", style=discord.ButtonStyle.blurple, row=4
    )
    async def up(self, interaction: discord.Interaction, button: discord.Button):
        """
        Shifts the game tiles up.
        """
        tiles = []
        for i in range(4):
            column = [button for button in self.game_tiles if button.column == i]
            column.reverse()
            tiles.extend([column])

        self.turn(tiles, reverse=True)

        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    @discord.ui.button(
        label=empty_label, emoji="⬇️", style=discord.ButtonStyle.blurple, row=4
    )
    async def down(self, interaction: discord.Interaction, button: discord.Button):
        """
        Shifts the game tiles down.
        """
        tiles = []
        for i in range(4):
            column = [button for button in self.game_tiles if button.column == i]
            tiles.extend([column])

        self.turn(tiles)

        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    @discord.ui.button(
        label=empty_label, emoji="➡️", style=discord.ButtonStyle.blurple, row=4
    )
    async def right(self, interaction: discord.Interaction, button: discord.Button):
        """
        Shifts the game tiles to the right.
        """
        tiles = []
        for i in range(4):
            row = [button for button in self.game_tiles if button.row == i]
            tiles.extend([row])

        self.turn(tiles)

        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    @discord.ui.button(
        label="Quit Game", emoji="❌", style=discord.ButtonStyle.red, row=4
    )
    async def quit(self, interaction: discord.Interaction, button: discord.Button):
        """
        Exits the game immediately.
        """
        self.stop()
        # we edit the message with the same content because otherwise
        # the user would get the interaction failed message.
        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    def spawn_new_tile(self) -> Optional[_2048Buttons]:
        """
        Spawns a new random tile with 90% of the tile being worth 2
        and 10% of it being worth 4, and colours it green.
        """
        if empty_tiles := [
            tile for tile in self.game_tiles if tile.label == self.empty_label
        ]:
            chosen_tile = random.choice(empty_tiles)
            chosen_tile.label = random.choices(["2", "4"], weights=[0.9, 0.1], k=1)[0]
            # colouring a new tile green so you can see it easier.
            chosen_tile.style = discord.ButtonStyle.green
            return chosen_tile
        return None

    def merge_tiles(self, tiles: list[_2048Buttons], reverse: bool = False) -> list:
        """
        Merges every tile along the same row/column.
        Does it up to 3 times.
        """
        merges = []
        # we reverse the list, so that the last elements get merged first,
        # like in the real game.
        tiles.reverse()

        for i in range(len(tiles) - 1):
            # checks if the labels match and if the tile has not already been merged.
            if (
                tiles[i].label != self.empty_label
                and tiles[i].label == tiles[i + 1].label
            ) and (tiles[i + int(reverse)] not in merges):
                combined_score = int(tiles[i].label) + int(tiles[i + 1].label)
                # if the order of tiles is reversed, we have to reverse the logic,
                # so that the tiles are merged in the right order.
                # otherwise they could be merged multple times.
                if reverse:
                    tiles[i].label = str(combined_score)
                    tiles[i + 1].label = self.empty_label
                    merges.append(tiles[i])
                else:
                    tiles[i + 1].label = str(combined_score)
                    tiles[i].label = self.empty_label
                    merges.append(tiles[i + 1])

                self.score += combined_score

        tiles.reverse()
        return merges

    def shift_tiles(self, tiles: list[_2048Buttons]) -> list:
        """
        Shifts every tile along the same row/column.
        Does it up to 3 times.
        """
        shifts = []
        for _ in tiles:
            for i in range(len(tiles) - 1):
                if (
                    tiles[i].label != self.empty_label
                    and tiles[i + 1].label == self.empty_label
                ):
                    tiles[i].label, tiles[i + 1].label = (
                        tiles[i + 1].label,
                        tiles[i].label,
                    )
                    shifts.append([tiles[i], tiles[i + 1]])

        return shifts

    def turn(self, tiles: list[list[_2048Buttons]], reverse: bool = False):
        """
        The logic for one turn.
        """
        # colouring every tile back to gray first.
        for tile_list in tiles:
            for tile in tile_list:
                if tile.style != discord.ButtonStyle.gray:
                    tile.style = discord.ButtonStyle.gray

        moves_made = []
        for tile_list in tiles:
            moves_made.extend(self.shift_tiles(tile_list))

            # we merge the tiles, then check again for any shifts possible.
            # we only want to merge once per turn though.
            moves_made.extend(self.merge_tiles(tile_list, reverse))

            moves_made.extend(self.shift_tiles(tile_list))

        self.end_turn(moves_made)

    def check_for_win(self) -> bool:
        if "2048" in [button.label for button in self.game_tiles]:
            for button in self.game_tiles:
                button.style = discord.ButtonStyle.green
            self.win = True

        return self.win

    def check_if_full(self) -> bool:
        return self.empty_label not in [button.label for button in self.game_tiles]

    def check_for_possible_moves(self) -> bool:
        """
        Checks if any moves could be executed right now.
        Only gets called when the board is full. If there are no moves,
        and the board is full, the game is over.
        """
        for x in range(4):
            column = [button for button in self.game_tiles if button.column == x]
            row = [button for button in self.game_tiles if button.row == x]
            for i in range(3):
                if column[i].label == column[i + 1].label:
                    return True
                if row[i].label == row[i + 1].label:
                    return True

        return False

    def end_turn(self, moves_made: list[_2048Buttons]):
        """
        Ends your turn and checks for a game over.
        """
        # the game ends if either the player reached the 2048 tile,
        # or if no new tiles can be spawned and the board is full.
        if self.check_for_win():
            self.stop()
        # if the board wouldnt change when you move, you dont get a new tile,
        # just like in the real game.
        elif moves_made:
            self.spawn_new_tile()
        # if there are no possible moves, and the board is full, we end the game.
        elif self.check_if_full():
            if not self.check_for_possible_moves():
                self.stop()
        # if there are no moves made but moves possible, we just do nothing.

    async def interaction_check(self, interaction: discord.Interaction):
        return self.player == interaction.user


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

    @commands.command(name="2048")
    async def _2048(self, ctx):
        """
        Starts a game of 2048.
        """
        view = _2048Game(ctx.author)
        await ctx.send(f"{ctx.author.mention}'s score: {view.score}", view=view)

        timeout = await view.wait()

        if timeout:
            await ctx.reply(
                f"Your game timed out! Thanks for playing.\nFinal score: {view.score}"
            )
            return

        if view.win:
            await ctx.reply("Congratulations! You win!\n" f"Final score: {view.score}")
            return

        await ctx.reply(
            "Too bad, but you will win next time! Thanks for playing.\n"
            f"Final score: {view.score}"
        )

    # basic error handling
    @rps.error
    async def rps_error(self, ctx, error):
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @tictactoe.error
    async def tictactoe_error(self, ctx, error):
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Games cog loaded")
