import time
from itertools import repeat
from math import floor
from random import shuffle
from typing import Optional

import discord


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
        return interaction.user.id == self.turn.id

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"The game timed out! {self.turn.mention} took too long to pick something!"
        )
