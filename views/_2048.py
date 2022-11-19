import random
from math import floor
from typing import Optional, Union

import discord


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
