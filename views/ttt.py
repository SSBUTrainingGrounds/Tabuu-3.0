from math import ceil
from typing import Optional, Union

import discord


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

        # If theres a tie we return false, else the game is still ongoing and we return None.
        return False if 0 not in board else None

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
