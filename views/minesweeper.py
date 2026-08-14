from math import floor
from random import shuffle
from typing import cast, override

import discord


class MinesweeperButton(discord.ui.Button["MinesweeperGame"]):
    """A single button in the for the Minesweeper Game."""

    def __init__(self, button_pos: int, max_cols: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, row=floor((button_pos) / max_cols)
        )
        self.emoji: str = "⬛"
        self.column: int = button_pos % max_cols
        self.button_pos: int = button_pos

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return
        await self.view.handle_turn(self, interaction)


class MinesweeperGame(discord.ui.View):
    """Contains the logic for the game."""

    def __init__(self, player: discord.Member, mine_count: int) -> None:
        super().__init__(timeout=180)
        self.player: discord.Member = player
        # The dimensions of the board.
        self.grid_x: int = 5
        self.grid_y: int = 5

        self.message: discord.Message | None = None

        # The list of mines as "True"s and the inverse as "False"s.
        self.mine_count: int = mine_count
        self.mines_list: list[bool] = [True] * mine_count + [False] * (
            (self.grid_x * self.grid_y) - mine_count
        )
        shuffle(self.mines_list)

        for i in range(self.grid_x * self.grid_y):
            _ = self.add_item(MinesweeperButton(i, self.grid_x))

    async def handle_turn(
        self, button: MinesweeperButton, interaction: discord.Interaction
    ) -> None:
        """Handles clicking on a Square in the Minesweeper Game."""
        self.first_turn(button.button_pos)

        # If we hit a mine, its game over immediately.
        if self.mines_list[button.button_pos]:
            for b in self.children:
                # We know the children are all MinesweeperButtons, so we can safely cast them.
                b = cast(MinesweeperButton, b)
                if self.mines_list[b.button_pos]:
                    b.style = discord.ButtonStyle.red
                    b.disabled = True
                    b.emoji = "💣"

            button.emoji = "💥"

            self.stop()

        else:
            self.open_cell(button)

        if self.check_game_over():
            for b in self.children:
                b = cast(MinesweeperButton, b)
                if self.mines_list[b.button_pos]:
                    b.style = discord.ButtonStyle.green
                    b.emoji = "🚩"

            self.stop()

            _ = await interaction.response.edit_message(
                content="🚩 Minesweeper (Solved!) 🚩", view=self
            )

        else:
            _ = await interaction.response.edit_message(
                content=f"💣 Minesweeper ({self.mine_count} Bombs) 💣", view=self
            )

    def get_adjacent_cells(self, row: int, column: int) -> list[MinesweeperButton]:
        """Gets every adjacent cell from a given cell."""
        # A list of coordinates.
        adjacent_cells: list[tuple[int, int]] = []

        # There are probably a dozen more efficient ways to do this,
        # but we check if an adjacent cell is in bounds and then add it to the list.
        if row > 0:
            adjacent_cells.append((row - 1, column))
        if row + 1 < self.grid_y:
            adjacent_cells.append((row + 1, column))
        if column > 0:
            adjacent_cells.append((row, column - 1))
        if column + 1 < self.grid_x:
            adjacent_cells.append((row, column + 1))
        if row > 0 and column > 0:
            adjacent_cells.append((row - 1, column - 1))
        if row + 1 < self.grid_y and column + 1 < self.grid_x:
            adjacent_cells.append((row + 1, column + 1))
        if row > 0 and column + 1 < self.grid_x:
            adjacent_cells.append((row - 1, column + 1))
        if row + 1 < self.grid_y and column > 0:
            adjacent_cells.append((row + 1, column - 1))

        return [
            cast(MinesweeperButton, self.children[cell[0] * self.grid_x + cell[1]])
            for cell in adjacent_cells
        ]

    def get_bomb_count(self, row: int, column: int) -> int:
        """Gets the count of Bombs that are adjacent to the given cell."""
        adjacent_cells = self.get_adjacent_cells(row, column)
        return sum(bool(self.mines_list[cell.button_pos]) for cell in adjacent_cells)

    def get_emoji(self, bomb_count: int) -> str:
        """Gets the emoji for a given Bomb Count."""
        if bomb_count == 0:
            return "⬛"
        elif bomb_count == 1:
            return "1️⃣"
        elif bomb_count == 2:
            return "2️⃣"
        elif bomb_count == 3:
            return "3️⃣"
        elif bomb_count == 4:
            return "4️⃣"
        elif bomb_count == 5:
            return "5️⃣"
        elif bomb_count == 6:
            return "6️⃣"
        elif bomb_count == 7:
            return "7️⃣"
        elif bomb_count == 8:
            return "8️⃣"
        # This should never happen, but just in case.
        else:
            return "❓"

    def open_cell(self, cell: MinesweeperButton) -> None:
        """Opens a cell."""
        # We return if the cell is already opened, for opening the mines recursively.
        if cell.disabled:
            return

        # Can't really happen if the button was properly initialized.
        if cell.row is None:
            return

        bomb_count = self.get_bomb_count(cell.row, cell.column)
        cell.disabled = True
        self.open_adjacent_cells(bomb_count, cell.row, cell.column)
        cell.emoji = self.get_emoji(bomb_count)

    def open_adjacent_cells(self, bomb_count: int, row: int, column: int) -> None:
        """Opens every adjacent cell if the adjacent Bomb Count is 0."""
        if bomb_count != 0:
            return

        adjacent_cells = self.get_adjacent_cells(row, column)

        for cell in adjacent_cells:
            if cell.row is None:
                continue

            new_bomb_count = self.get_bomb_count(cell.row, cell.column)
            cell.emoji = self.get_emoji(new_bomb_count)
            self.open_cell(cell)
            cell.disabled = True

    def check_game_over(self) -> bool:
        """Returns whether or not there are more non-mine cells to open."""
        buttons = [cast(MinesweeperButton, cell) for cell in self.children]
        return not any(
            not cell.disabled and not self.mines_list[cell.button_pos]
            for cell in buttons
        )

    def first_turn(self, button_pos: int) -> None:
        """If its the first cell you click, we want the user to always hit a 0."""
        # If a cell is already disabled, it is not the first turn anymore.
        for cell in self.children:
            cell = cast(MinesweeperButton, cell)
            if cell.disabled:
                return

        # We just shuffle until the clicked cell is a 0,
        # there are probably more efficient ways to go about that.
        while (
            self.get_bomb_count(
                floor(button_pos / self.grid_x), button_pos % self.grid_x
            )
            != 0
            or self.mines_list[button_pos]
        ):
            shuffle(self.mines_list)

    @override
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.player

    @override
    async def on_timeout(self) -> None:
        if self.message is None:
            return

        _ = await self.message.reply(
            f"The game timed out! {self.player.mention} took too long to pick something!"
        )
