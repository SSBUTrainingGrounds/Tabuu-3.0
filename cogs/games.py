import random
import time
from itertools import repeat
from math import ceil, floor
from random import shuffle
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands

from utils.ids import GuildIDs


class RpsButtons(discord.ui.View):
    """Contains the RPS Game Buttons."""

    def __init__(self, author: discord.Member, member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        self.message = None

    # Not sure why the Rock Emoji fails to display here, it does display properly on Discord.
    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.gray)
    async def rock(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Registers the author and user input for Rock.
        Stops if both parties made a choice.
        """

        await interaction.response.send_message("You chose Rock!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Rock"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Rock"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Paper", emoji="📝", style=discord.ButtonStyle.gray)
    async def paper(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Registers the author and user input for Paper.
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
    ) -> None:
        """Registers the author and user input for Scissors.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Scissors!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Scissors"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Scissors"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ignores every other member except the author and mentioned member.
        return interaction.user in (self.member, self.author)

    async def on_timeout(self) -> None:
        # If the match didnt go through as planned.
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
    """Contains the TicTacToe Buttons."""

    def __init__(self, button_pos: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray,
            label="\u200b",
            row=ceil((button_pos + 1) / 3),
        )
        self.button_pos = button_pos

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.handle_turn(self, self.button_pos, interaction)


class TicTacToeGame(discord.ui.View):
    """Contains the TicTacToe Game Logic."""

    def __init__(self, author: discord.Member, member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.turn = author
        self.message = None
        # Initialises the board.
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # Adds all of the buttons.
        for i in range(9):
            self.add_item(TicTacToeButtons(i))

    def check_for_winner(
        self, board: list[int]
    ) -> Optional[Union[discord.Member, bool]]:
        """Checks if the game is over and the outcome of the game."""

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

        # Checks for the winner and returns it, if found.
        for combination in winning_combinations:
            winning_list = [board[position] for position in combination]

            if winning_list == [1, 1, 1]:
                return self.author

            if winning_list == [2, 2, 2]:
                return self.member

        # If theres a tie we return false.
        if 0 not in board:
            return False

        # If the game is ongoing, we return None.
        return None

    async def game_ending(self, interaction: discord.Interaction) -> None:
        """Handles the game ending for us."""

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
    ) -> None:
        """The logic for one turn."""

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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Checks if the user is in the game.
        if interaction.user not in (self.member, self.author):
            return False
        # Checks if its your turn.
        if interaction.user == self.author and self.turn == self.author:
            self.turn = self.member
            return True
        if interaction.user == self.member and self.turn == self.member:
            self.turn = self.author
            return True
        return False

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"Match timed out! {self.turn.mention} took too long to pick something!"
        )


class BlackJackButtons(discord.ui.View):
    def __init__(self, author: discord.Member, member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.author_hand = [[], 0]
        self.member_hand = [[], 0]
        self.folded = []
        self.turn = author
        self.message = None

    # All of the possible cards.
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

    def draw_card(self) -> None:
        card_deck = []
        for i, f in enumerate(self.card_faces):
            for s in self.card_suites:
                if i in (10, 11, 12):
                    i = 9
                card_deck.append([f"{f} of {s}", i + 1])

        card = random.choice(card_deck)

        # Checks if the card is already present in one hand, if so repeats the process.
        # I read that in real life blackjack is played with like 8 decks at once,
        # so this really isnt even needed
        if card[0] in self.author_hand[0] or card[0] in self.member_hand[0]:
            try:
                self.draw_card()
                return
            except RecursionError:
                return

        if self.turn == self.author:
            # If the card is an ace, checks if it should be worth 11 or 1.
            if card[1] == 1 and self.author_hand[1] <= 10:
                card[1] = 11
            self.author_hand[0].append(card[0])
            self.author_hand[1] += card[1]
        else:
            if card[1] == 1 and self.member_hand[1] <= 10:
                card[1] = 11
            self.member_hand[0].append(card[0])
            self.member_hand[1] += card[1]

    def get_winner(self) -> Optional[discord.Member]:
        # Checks for values greater than 21.
        if self.author_hand[1] > 21 >= self.member_hand[1]:
            return self.member

        if self.member_hand[1] > 21 >= self.author_hand[1]:
            return self.author

        # Checks for draws.
        if self.member_hand[1] == self.author_hand[1]:
            return None

        if self.author_hand[1] > self.member_hand[1]:
            return self.author

        return self.member

    async def end_game(self) -> None:
        self.stop()

        if self.get_winner():
            await self.message.reply(f"The winner is {self.get_winner().mention}!")
        else:
            await self.message.reply("The game is tied!")

    @discord.ui.button(
        label="Draw a Card", emoji="🃏", style=discord.ButtonStyle.blurple
    )
    async def draw(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Draws another card and checks if the players turn is over."""

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
    async def fold(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Folds and switches the turn, or exits the game."""

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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.author, self.member):
            return False
        if interaction.user == self.author and self.turn == self.author:
            return True
        if interaction.user == self.member and self.turn == self.member:
            return True
        return False

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"The match timed out! {self.turn.mention} took too long to pick a choice!"
        )


class _2048Buttons(discord.ui.Button["_2048Game"]):
    """The actual buttons that are used as game tiles."""

    def __init__(self, button_pos: int, label: str) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray,
            label=label,
            row=floor((button_pos) / 4),
        )
        self.button_pos = button_pos
        self.disabled = True
        # We need to track the column of the button ourselves.
        self.column = button_pos % 4


class _2048Game(discord.ui.View):
    """Contains the logic for the game."""

    def __init__(self, player: Union[discord.User, discord.Member]) -> None:
        super().__init__(timeout=60)
        self.player = player
        self.win = False
        self.score = 0
        for i in range(16):
            self.add_item(_2048Buttons(i, self.empty_label))
        # Only the game buttons, without the menu ones.
        self.game_tiles = [button for button in self.children if not button.emoji]
        # The game starts off with 2 tiles set to "2".
        for _ in range(2):
            self.spawn_new_tile()

    # A zero-width space character.
    empty_label = "\u200b"

    @discord.ui.button(
        label=empty_label, emoji="⬅️", style=discord.ButtonStyle.blurple, row=4
    )
    async def left(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Shifts the game tiles to the left."""

        tiles = []
        for i in range(4):
            row = [button for button in self.game_tiles if button.row == i]
            # For left and for up we have to reverse the row/column.
            row.reverse()
            tiles.extend([row])

        # Also we need to call the turn in reverse so it merges correctly.
        self.turn(tiles, reverse=True)

        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    @discord.ui.button(
        label=empty_label, emoji="⬆️", style=discord.ButtonStyle.blurple, row=4
    )
    async def up(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Shifts the game tiles up."""

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
    async def down(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Shifts the game tiles down."""

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
    async def right(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Shifts the game tiles to the right."""

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
    async def quit(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Exits the game immediately."""

        self.stop()
        # We edit the message with the same content because otherwise
        # the user would get the interaction failed message.
        await interaction.response.edit_message(
            content=f"{interaction.user.mention}'s score: {self.score}", view=self
        )

    def spawn_new_tile(self) -> Optional[_2048Buttons]:
        """Spawns a new random tile with 90% of the tile being worth 2
        and 10% of it being worth 4, and colours it green.
        """
        if empty_tiles := [
            tile for tile in self.game_tiles if tile.label == self.empty_label
        ]:
            chosen_tile = random.choice(empty_tiles)
            chosen_tile.label = random.choices(["2", "4"], weights=[0.9, 0.1], k=1)[0]
            # Colouring a new tile green so you can see it easier.
            chosen_tile.style = discord.ButtonStyle.green
            return chosen_tile
        return None

    def merge_tiles(self, tiles: list[_2048Buttons], reverse: bool = False) -> list:
        """Merges every tile along the same row/column.
        Does it up to 3 times.
        """
        merges = []
        # We reverse the list, so that the last elements get merged first,
        # like in the real game.
        tiles.reverse()

        for i in range(len(tiles) - 1):
            # Checks if the labels match and if the tile has not already been merged.
            if (
                tiles[i].label != self.empty_label
                and tiles[i].label == tiles[i + 1].label
            ) and (tiles[i + int(reverse)] not in merges):
                combined_score = int(tiles[i].label) + int(tiles[i + 1].label)
                # If the order of tiles is reversed, we have to reverse the logic,
                # so that the tiles are merged in the right order.
                # Otherwise they could be merged multple times.
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
        """Shifts every tile along the same row/column.
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

    def turn(self, tiles: list[list[_2048Buttons]], reverse: bool = False) -> None:
        """The logic for one turn."""

        # Colouring every tile back to gray first.
        for tile_list in tiles:
            for tile in tile_list:
                if tile.style != discord.ButtonStyle.gray:
                    tile.style = discord.ButtonStyle.gray

        moves_made = []
        for tile_list in tiles:
            moves_made.extend(self.shift_tiles(tile_list))

            # We merge the tiles, then check again for any shifts possible.
            # We only want to merge once per turn though.
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
        """Checks if any moves could be executed right now.
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

    def end_turn(self, moves_made: list[_2048Buttons]) -> None:
        """Ends your turn and checks for a game over."""
        # The game ends if either the player reached the 2048 tile,
        # or if no new tiles can be spawned and the board is full.
        if self.check_for_win():
            self.stop()
        # If the board wouldnt change when you move, you dont get a new tile,
        # just like in the real game.
        elif moves_made:
            self.spawn_new_tile()
        # If there are no possible moves, and the board is full, we end the game.
        elif self.check_if_full():
            if not self.check_for_possible_moves():
                self.stop()
        # If there are no moves made but possible moves left, we just do nothing.

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.player == interaction.user


class MemoryButtons(discord.ui.Button["MemoryGame"]):
    """Contains Buttons for the Memory Game."""

    def __init__(self, button_pos: int, hidden_emoji: str) -> None:
        super().__init__(style=discord.ButtonStyle.gray, row=floor((button_pos) / 5))
        self.revealed: bool = False

        # The very middle button will be disabled, since we have 25 buttons.
        if button_pos == 12:
            self.disabled = True
            self.revealed = True

        self.label: str = "\u200b"

        self.button_pos: int = button_pos
        self.hidden_emoji: str = hidden_emoji

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.handle_turn(self, interaction)


class MemoryGame(discord.ui.View):
    """Contains the Game Logic for the Memory Game."""

    def __init__(self, player1: discord.Member, player2: discord.Member) -> None:
        super().__init__(timeout=60)
        self.player1: discord.Member = player1
        self.player2: discord.Member = player2
        self.turn: discord.Member = player2
        self.compare_emoji: Optional[str] = None
        self.message: Optional[discord.Message] = None

        # Includes every emoji in there twice and shuffles the list.
        emoji_list = [
            x
            for item in [
                "🎲",
                "🎮",
                "❤️",
                "💀",
                "🔥",
                "📯",
                "🎵",
                "📢",
                "⚽",
                "🎯",
                "♟️",
                "🏹",
            ]
            for x in repeat(item, 2)
        ]
        shuffle(emoji_list)
        self.emojis: list[str] = emoji_list

        for i in range(25):
            if i < 12:
                self.add_item(MemoryButtons(i, self.emojis[i]))
            elif i > 12:
                self.add_item(MemoryButtons(i, self.emojis[i - 1]))
            else:
                self.add_item(MemoryButtons(i, ""))

    async def handle_turn(
        self, button: discord.Button, interaction: discord.Interaction
    ) -> None:
        """Handles a turn in the memory game."""
        button.disabled = True
        button.emoji = button.hidden_emoji

        if self.turn == self.player1:
            button.style = discord.ButtonStyle.blurple
        else:
            button.style = discord.ButtonStyle.green

        await interaction.response.edit_message(
            content=f"Memory:\n🟦{self.player1.mention} vs. 🟩{self.player2.mention}\n{self.turn.mention}'s turn:",
            view=self,
        )

        if self.check_if_over():
            winner, player1_count, player2_count = self.get_winner()
            if winner:
                await self.message.reply(
                    content=f"The winner is: {winner.mention}! {round(player1_count / 2)} pairs vs. {round(player2_count / 2)} pairs!"
                )
            else:
                # If the game is tied it will always be 6v6 pairs but might as well use the variables.
                await self.message.reply(
                    content=f"The game is tied with {round(player1_count / 2)} pairs vs. {round(player2_count / 2)} pairs!"
                )
            self.stop()

        if not self.compare_emoji:
            self.compare_emoji = button.emoji
        else:
            # We intentionally use a blocking call here.
            # We want the user to see the new emoji for a few seconds before editing again.
            # A non-blocking call would allow the user to click on more tiles, we dont wanna do that,
            # we just want to display the emojis a bit longer so we can safely use a blocking sleep statement.
            # We have 3 seconds to respond to a discord interaction, sleeping 1.5s should be fine, hopefully.
            time.sleep(1.5)

            self.check_for_pair(self.compare_emoji, button.emoji)

        await interaction.edit_original_response(
            content=f"Memory:\n🟦{self.player1.mention} vs. 🟩{self.player2.mention}\n{self.turn.mention}'s turn:",
            view=self,
        )

    def check_for_pair(self, emoji1: str, emoji2: str) -> None:
        """Checks if the 2 emojis are the same and handles the result.
        If they are the same the player continues, otherwise we will switch turns."""
        if emoji1 == emoji2:
            for button in self.children:
                if button.emoji:
                    button.revealed = True
        else:
            for button in self.children:
                if not button.revealed:
                    button.emoji = None
                    button.style = discord.ButtonStyle.gray
                    button.disabled = False

            self.turn = self.player2 if self.turn == self.player1 else self.player1

        self.compare_emoji = None

    def check_if_over(self) -> bool:
        """Checks if the game is over."""
        return all(button.disabled for button in self.children)

    def get_winner(self) -> tuple[Optional[discord.Member], int, int]:
        """Counts the total pairs and returns a winner, if there is one."""
        player1_count = 0
        player2_count = 0

        for button in self.children:
            if button.style == discord.ButtonStyle.blurple:
                player1_count += 1
            elif button.style == discord.ButtonStyle.green:
                player2_count += 1

        if player1_count > player2_count:
            return (self.player1, player1_count, player2_count)
        elif player2_count > player1_count:
            return (self.player2, player1_count, player2_count)
        else:
            return (None, player1_count, player2_count)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Checks if the user is in the game.
        if interaction.user not in (self.player1, self.player2):
            return False
        # Checks if its your turn.
        if interaction.user == self.turn:
            return True
        return False

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"The game timed out! {self.turn.mention} took too long to pick something!"
        )


class MinesweeperButtons(discord.ui.Button["MinesweeperGame"]):
    """Contains Buttons for the Memory Game."""

    def __init__(self, button_pos: int) -> None:
        super().__init__(style=discord.ButtonStyle.gray, row=floor((button_pos) / 5))
        self.label: str = "\u200b"
        self.column = button_pos % 5
        self.button_pos = button_pos

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.handle_turn(self, interaction)


class MinesweeperGame(discord.ui.View):
    """Contains the logic for the game."""

    def __init__(self, player: discord.Member, mine_count: int) -> None:
        super().__init__(timeout=60)
        self.player: discord.Member = player
        # The dimensions of the board.
        self.grid_x: int = 5
        self.grid_y: int = 5

        self.message: Optional[discord.Message] = None

        # The list of mines as "True"s and the inverse as "False"s.
        self.mine_count: int = mine_count
        self.mines_list: list[bool] = [True] * mine_count + [False] * (
            (self.grid_x * self.grid_y) - mine_count
        )
        shuffle(self.mines_list)

        for i in range(25):
            self.add_item(MinesweeperButtons(i))

    async def handle_turn(
        self, button: discord.Button, interaction: discord.Interaction
    ) -> None:
        """Handles clicking on a Square in the Minesweeper Game."""
        self.first_turn(button.button_pos)

        # If we hit a mine, its game over immediately.
        if self.mines_list[button.button_pos]:
            for b in self.children:
                if self.mines_list[b.button_pos]:
                    b.style = discord.ButtonStyle.red
                    b.disabled = True
                    b.emoji = "💣"

            self.stop()

        else:
            self.open_cell(button)

        if self.check_game_over():
            for b in self.children:
                if self.mines_list[b.button_pos]:
                    b.style = discord.ButtonStyle.green
                    b.emoji = "🚩"

            self.stop()

            await interaction.response.edit_message(
                content="🚩 Minesweeper (Solved!) 🚩", view=self
            )

        else:
            await interaction.response.edit_message(
                content=f"💣 Minesweeper ({self.mine_count} Bombs) 💣", view=self
            )

    def get_adjacent_cells(self, row: int, column: int) -> list[discord.Button]:
        """Gets every adjacent cell from a given cell."""
        adjacent_cells = []

        # There are probably a dozen more efficient ways to do this,
        # but we check if an adjacent cell is in bounds and then add it to the list.
        if row > 0:
            adjacent_cells.append((row - 1, column))
        if row + 1 < self.grid_x:
            adjacent_cells.append((row + 1, column))
        if column > 0:
            adjacent_cells.append((row, column - 1))
        if column + 1 < self.grid_y:
            adjacent_cells.append((row, column + 1))
        if row > 0 and column > 0:
            adjacent_cells.append((row - 1, column - 1))
        if row + 1 < self.grid_x and column + 1 < self.grid_y:
            adjacent_cells.append((row + 1, column + 1))
        if row > 0 and column + 1 < self.grid_y:
            adjacent_cells.append((row - 1, column + 1))
        if row + 1 < self.grid_x and column > 0:
            adjacent_cells.append((row + 1, column - 1))

        return [
            self.children[cell[0] * self.grid_x + cell[1]] for cell in adjacent_cells
        ]

    def get_bomb_count(self, row: int, column: int) -> int:
        """Gets the count of Bombs that are adjacent to the given cell."""
        adjacent_cells = self.get_adjacent_cells(row, column)
        return sum(bool(self.mines_list[cell.button_pos]) for cell in adjacent_cells)

    def open_cell(self, cell: discord.Button) -> None:
        """Opens a cell."""
        # We return if the cell is already opened, for opening the mines recursively.
        if cell.disabled:
            return

        bomb_count = self.get_bomb_count(cell.row, cell.column)
        cell.disabled = True
        self.open_adjacent_cells(cell, bomb_count, cell.row, cell.column)
        cell.label = bomb_count if bomb_count != 0 else "\u200b"

    def open_adjacent_cells(
        self, cell: discord.Button, bomb_count: int, row: int, column: int
    ) -> None:
        """Opens every adjacent cell if the adjacent Bomb Count is 0."""
        if bomb_count != 0:
            return

        adjacent_cells = self.get_adjacent_cells(row, column)

        for cell in adjacent_cells:
            new_bomb_count = self.get_bomb_count(cell.row, cell.column)
            cell.label = new_bomb_count if new_bomb_count != 0 else "\u200b"
            self.open_cell(cell)
            cell.disabled = True

    def check_game_over(self) -> bool:
        """Returns whether or not there are more non-mine cells to open."""
        return not any(
            not cell.disabled and not self.mines_list[cell.button_pos]
            for cell in self.children
        )

    def first_turn(self, button_pos: int) -> None:
        """If its the first cell you click, we want the user to always hit a 0."""
        # If a cell is already disabled, it is not the first turn anymore.
        for cell in self.children:
            if cell.disabled:
                return

        # We just shuffle until the clicked cell is a 0,
        # there are probably more efficient ways to go about that.
        while (
            self.get_bomb_count(
                floor(button_pos / self.grid_x), button_pos % self.grid_y
            )
            != 0
            or self.mines_list[button_pos]
        ):

            shuffle(self.mines_list)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.player

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"The game timed out! {self.player.mention} took too long to pick something!"
        )


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

    @rps.error
    async def rps_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @tictactoe.error
    async def tictactoe_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @blackjack.error
    async def blackjack_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @memory.error
    async def memory_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error

    @minesweeper.error
    async def minesweeper_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please input a mine count between 2 and 12!")
        else:
            raise error


async def setup(bot) -> None:
    await bot.add_cog(Games(bot))
    print("Games cog loaded")
