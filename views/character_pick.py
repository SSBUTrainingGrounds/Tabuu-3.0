import json
from typing import Optional

import discord
from utils.character import match_character


class CharacterDropdown(discord.ui.Select):
    """Handles the Pings and Threads of our Matchmaking System.
    Also contains the Recentpings command with the Dropdown Menu.
    """

    def __init__(
        self,
        characters: list[str, str, str],
    ) -> None:

        options = [
            discord.SelectOption(
                label=character[0].title(),
                description=f"ID: {', '.join(character[1])}",
                emoji=character[2],
            )
            for character in characters
        ]

        super().__init__(
            placeholder=f"Characters {characters[0][1][0]} - {characters[-1][1][0]}",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        # If there is a turn order, the winner of the previous game will be the first to pick.
        # Then the pick is announced in the channel and the loser picks their character.
        if self.view.turn:
            await interaction.response.send_message(
                f"{self.view.turn.mention} has chosen {self.values[0]}. "
                f"({match_character(self.values[0])[0]})"
            )

            if self.view.turn.id == self.view.player_one.id:
                self.view.player_one_choice = self.values[0]
                self.view.turn = self.view.player_two

            elif self.view.turn.id == self.view.player_two.id:
                self.view.player_two_choice = self.values[0]
                self.view.turn = self.view.player_one

            # If there is a turn order, the first child of the view will be the CharacterButton.
            self.view.children[0].update_label_emoji()

            if self.view.player_one_choice and self.view.player_two_choice:
                for item in self.view.children:
                    item.disabled = True
                await self.view.message.edit(view=self.view)
                self.view.stop()
            else:
                await self.view.message.edit(
                    content=f"{self.view.turn.mention}, please pick a character for the next Game!",
                    view=self.view,
                )

            return

        # If there is no turn order, both players will pick their character simultaneously.
        await interaction.response.send_message(
            f"You have chosen {self.values[0]}. "
            f"({match_character(self.values[0])[0]})",
            ephemeral=True,
        )

        if interaction.user.id == self.view.player_one.id:
            self.view.player_one_choice = self.values[0]

        elif interaction.user.id == self.view.player_two.id:
            self.view.player_two_choice = self.values[0]

        if self.view.player_one_choice and self.view.player_two_choice:
            for item in self.view.children:
                item.disabled = True
            await self.view.message.edit(view=self.view)
            self.view.stop()


class CharacterButton(discord.ui.Button):
    def __init__(
        self,
        player_one: discord.Member,
        player_one_character: str,
        player_one_emoji: str,
        player_two: discord.Member,
        player_two_character: str,
        player_two_emoji: str,
        turn: discord.Member,
    ):
        self.player_one_character = player_one_character
        self.player_one_emoji = player_one_emoji
        self.player_two_character = player_two_character
        self.player_two_emoji = player_two_emoji

        if turn.id == player_one.id:
            super().__init__(
                label=f"Stay {self.player_one_character}?",
                emoji=self.player_one_emoji,
            )
        elif turn.id == player_two.id:
            super().__init__(
                label=f"Stay {self.player_two_character}?",
                emoji=self.player_two_emoji,
            )

    def update_label_emoji(self) -> None:
        if self.view.player_one_choice and self.view.player_two_choice:
            self.disabled = True
            return

        if self.view.turn.id == self.view.player_one.id:
            self.label = f"Stay {self.player_one_character}?"
            self.emoji = self.player_one_emoji
        elif self.view.turn.id == self.view.player_two.id:
            self.label = f"Stay {self.player_two_character}?"
            self.emoji = self.player_two_emoji

    async def callback(self, interaction: discord.Interaction):
        if self.view.turn.id == self.view.player_one.id:
            await interaction.response.send_message(
                f"{self.view.turn.mention} has chosen {self.player_one_character}. "
                f"({self.player_one_emoji})",
            )

            self.view.player_one_choice = self.player_one_character
            self.view.turn = self.view.player_two

            self.update_label_emoji()

        elif self.view.turn.id == self.view.player_two.id:
            await interaction.response.send_message(
                f"{self.view.turn.mention} has chosen {self.player_two_character}. "
                f"({self.player_two_emoji})",
            )

            self.view.player_two_choice = self.player_two_character
            self.view.turn = self.view.player_one

            self.update_label_emoji()

        if self.view.player_one_choice and self.view.player_two_choice:
            for item in self.view.children:
                item.disabled = True
            await self.view.message.edit(view=self.view)
            self.view.stop()
        else:
            await self.view.message.edit(
                content=f"{self.view.turn.mention}, please pick a character for the next Game!",
                view=self.view,
            )


class CharacterView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(
        self,
        player_one: discord.Member,
        player_two: discord.Member,
        turn: Optional[discord.Member],
        last_choice_one: Optional[tuple[str, str]] = None,
        last_choice_two: Optional[tuple[str, str]] = None,
    ) -> None:
        super().__init__(timeout=180)

        self.player_one = player_one
        self.player_one_choice = ""
        self.player_two = player_two
        self.player_two_choice = ""

        self.turn = turn

        self.message: Optional[discord.Message] = None

        with open(r"./files/characters.json", "r", encoding="utf-8") as f:
            characters = json.load(f)

        char_options = [
            [
                character["name"],
                character["id"],
                character["emoji"],
            ]
            for character in characters["Characters"]
        ]

        if last_choice_one and last_choice_two:
            self.add_item(
                CharacterButton(
                    player_one,
                    last_choice_one[0],
                    last_choice_one[1],
                    player_two,
                    last_choice_two[0],
                    last_choice_two[1],
                    turn,
                )
            )

        self.add_item(CharacterDropdown(char_options[:25]))
        self.add_item(CharacterDropdown(char_options[25:50]))
        self.add_item(CharacterDropdown(char_options[50:75]))
        self.add_item(CharacterDropdown(char_options[75:]))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.turn:
            return interaction.user.id == self.turn.id

        return interaction.user.id in (self.player_one.id, self.player_two.id)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        await self.message.edit(view=self)
