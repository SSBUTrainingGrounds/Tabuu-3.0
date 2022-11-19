from math import floor
from random import shuffle
from typing import Optional

import discord


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
