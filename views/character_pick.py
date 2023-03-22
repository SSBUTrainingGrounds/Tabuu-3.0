import json
from typing import Optional

import discord
from discord.ext import commands


class CharacterDropdown(discord.ui.Select):
    """Handles the Pings and Threads of our Matchmaking System.
    Also contains the Recentpings command with the Dropdown Menu.
    """

    def __init__(
        self,
        bot: commands.Bot,
        characters: list[str, str, str],
    ) -> None:
        self.bot = bot

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
                f"{self.view.turn.mention} has chosen {self.values[0]}.",
            )

            if self.view.turn.id == self.view.player_one.id:
                self.view.player_one_choice = self.values[0]
                self.view.turn = self.view.player_two

            elif self.view.turn.id == self.view.player_two.id:
                self.view.player_two_choice = self.values[0]
                self.view.turn = self.view.player_one

            await self.view.message.edit(
                content=f"{self.view.turn.mention}, please pick a character for the next Game!"
            )

            if self.view.player_one_choice and self.view.player_two_choice:
                for item in self.view.children:
                    item.disabled = True
                await self.view.message.edit(view=self.view)
                self.view.stop()

            return

        # If there is no turn order, both players will pick their character simultaneously.
        await interaction.response.send_message(
            f"You have chosen {self.values[0]}.",
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


class CharacterView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(
        self,
        bot: commands.Bot,
        player_one: discord.Member,
        player_two: discord.Member,
        turn: Optional[discord.Member],
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

        self.add_item(CharacterDropdown(bot, char_options[:25]))
        self.add_item(CharacterDropdown(bot, char_options[25:50]))
        self.add_item(CharacterDropdown(bot, char_options[50:75]))
        self.add_item(CharacterDropdown(bot, char_options[75:]))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.turn:
            return interaction.user.id == self.turn.id

        return interaction.user.id in (self.player_one.id, self.player_two.id)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        await self.message.edit(view=self)
