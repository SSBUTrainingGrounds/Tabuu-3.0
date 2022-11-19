from typing import Optional

import discord

from utils.ids import TGRoleIDs


class BestOfButtons(discord.ui.View):
    def __init__(self, player_one: discord.Member) -> None:
        super().__init__(timeout=60)
        self.player_one = player_one
        self.choice: Optional[int] = None

    @discord.ui.button(label="Best of 3", emoji="3️⃣", style=discord.ButtonStyle.gray)
    async def three_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """The button to select a Best of 3."""
        self.choice = 3
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(
            content=f"{self.player_one.mention}, do you want to play a Best of 3 or a Best of 5?",
            view=self,
        )
        self.stop()

    @discord.ui.button(label="Best of 5", emoji="5️⃣", style=discord.ButtonStyle.gray)
    async def five_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """The button to select a Best of 5."""
        self.choice = 5
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(
            content=f"{self.player_one.mention}, do you want to play a Best of 3 or a Best of 5?",
            view=self,
        )
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.player_one.id


class ArenaButton(discord.ui.View):
    def __init__(self, player_one: discord.Member, choice: int) -> None:
        super().__init__(timeout=1500)
        self.player_one = player_one
        self.choice = choice

    @discord.ui.button(
        label="Click here when you're ready to go.",
        emoji="✔️",
        style=discord.ButtonStyle.gray,
    )
    async def check_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """The button to start the match."""
        button.disabled = True
        await interaction.response.edit_message(
            content=f"**Best of {self.choice}** selected.\n"
            "Please host an arena and share the Code/Password here. Click the button when you're ready.",
            view=self,
        )
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.player_one.id


class PlayerButtons(discord.ui.View):
    def __init__(
        self, player_one: discord.Member, player_two: discord.Member, game_count: int
    ) -> None:
        super().__init__(timeout=1800)
        self.player_one = player_one
        self.player_two = player_two
        self.game_count = game_count
        self.player_one_choice: Optional[discord.Member] = None
        self.player_two_choice: Optional[discord.Member] = None
        self.winner: Optional[discord.Member] = None
        self.cancelled = False
        button_one = discord.ui.Button(
            label=str(player_one), style=discord.ButtonStyle.gray, emoji="1️⃣", row=0
        )
        button_one.callback = self.player_one_button
        self.add_item(button_one)

        button_two = discord.ui.Button(
            label=str(player_two), style=discord.ButtonStyle.gray, emoji="2️⃣", row=0
        )
        button_two.callback = self.player_two_button
        self.add_item(button_two)

    async def handle_choice(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Handles the choice of the winner of a player."""
        if self.player_one_choice and self.player_two_choice:
            if self.player_one_choice == self.player_two_choice:
                for button in self.children:
                    button.disabled = True
                self.winner = self.player_one_choice
                self.stop()
            else:
                self.player_one_choice = None
                self.player_two_choice = None
                for button in [
                    c for c in self.children if c.style == discord.ButtonStyle.blurple
                ]:
                    button.style = discord.ButtonStyle.grey
                await interaction.channel.send(
                    "You picked different winners! Please either try again, or call a moderator/cancel the match."
                )
        else:
            button.style = discord.ButtonStyle.blurple

        await interaction.response.edit_message(
            content=f"When you're done, click on the button of the winner of Game {self.game_count} to report the match.",
            view=self,
        )

    async def player_one_button(self, interaction: discord.Interaction) -> None:
        """The button for reporting player one as the match winner."""
        # The button can only be clicked if the player has not already picked a winner.
        if (
            (interaction.user.id == self.player_one.id) and not self.player_one_choice
        ) or (
            (interaction.user.id == self.player_two.id) and not self.player_two_choice
        ):
            if interaction.user.id == self.player_one.id:
                self.player_one_choice = self.player_one
            else:
                self.player_two_choice = self.player_one

            button = [c for c in self.children if c.label == str(self.player_one)][0]

            await self.handle_choice(interaction, button)

    async def player_two_button(self, interaction: discord.Interaction) -> None:
        """The button for reporting player two as the match winner."""
        if (
            (interaction.user.id == self.player_one.id) and not self.player_one_choice
        ) or (
            (interaction.user.id == self.player_two.id) and not self.player_two_choice
        ):
            if interaction.user.id == self.player_one.id:
                self.player_one_choice = self.player_two
            else:
                self.player_two_choice = self.player_two

            button = [c for c in self.children if c.label == str(self.player_two)][0]

            await self.handle_choice(interaction, button)

    @discord.ui.button(
        label="Cancel Match", emoji="❌", style=discord.ButtonStyle.red, row=1
    )
    async def cancel_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """The button to cancel the match immediately."""
        await interaction.response.send_message(
            f"Match cancelled by {interaction.user.mention}!"
        )
        self.cancelled = True
        self.stop()

    @discord.ui.button(
        label="Call a Moderator", emoji="👮", style=discord.ButtonStyle.red, row=1
    )
    async def call_mod_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """The button for calling a moderator."""
        await interaction.response.edit_message(
            content=f"When you're done, click on the button of the winner of Game {self.game_count} to report the match.",
            view=self,
        )
        self.cancelled = True
        self.stop()
        await interaction.channel.send(
            f"Match cancelled.\n{interaction.user.mention} called a moderator: <@&{TGRoleIDs.MOD_ROLE}>!"
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in (self.player_one.id, self.player_two.id)
