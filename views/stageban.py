from typing import Optional

import discord


class StarterStageButtons(discord.ui.View):
    """Contains the buttons for the initial stage banning.
    Does not contain the stages for counterpicking.

    The stages are banned in a 1-2-1 format."""

    def __init__(self, player_one: discord.Member, player_two: discord.Member) -> None:
        super().__init__(timeout=180)
        self.player_one = player_one
        self.player_two = player_two
        self.player_two_choices = 0
        self.turn = player_one
        self.choice: Optional[str] = None

    @discord.ui.button(label="Battlefield", emoji="⚔️", style=discord.ButtonStyle.gray)
    async def battlefield(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Final Destination", emoji="👾", style=discord.ButtonStyle.gray
    )
    async def final_destination(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Small Battlefield", emoji="🗡️", style=discord.ButtonStyle.gray
    )
    async def small_battlefield(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(label="Smashville", emoji="🏛️", style=discord.ButtonStyle.gray)
    async def smashville(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Town and City", emoji="🚌", style=discord.ButtonStyle.gray
    )
    async def town_and_city(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    async def ban_stage(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Handles the banning of stages in the first phase, in Game 1."""
        button.style = discord.ButtonStyle.red
        button.disabled = True

        # When only one stage remains, that is the stage that will be played.
        if len([button for button in self.children if not button.disabled]) == 1:
            chosen_stage = [button for button in self.children if not button.disabled][
                0
            ]
            chosen_stage.style = discord.ButtonStyle.green
            await interaction.response.edit_message(
                content=f"**Stage bans**\nThe chosen stage is: **{chosen_stage.label}**",
                view=self,
            )
            self.choice = chosen_stage.label
            self.stop()
        else:
            await interaction.response.edit_message(
                content=f"**Stage bans**\n{self.turn.mention}, "
                f"please **ban {'1 stage' if self.turn == self.player_one else '2 stages'}**:",
                view=self,
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.player_one, self.player_two):
            return False
        if interaction.user == self.player_one and self.turn == self.player_one:
            self.turn = self.player_two
            return True
        if interaction.user == self.player_two and self.turn == self.player_two:
            if self.player_two_choices == 1:
                self.turn = self.player_one
            else:
                self.player_two_choices += 1
            return True
        return False


class CounterpickStageButtons(discord.ui.View):
    """Contains the buttons for counterpicking stages.

    The winner bans 2 or 3 stages (depending on BO3/BO5),
    and the loser picks from the remaining stages."""

    def __init__(
        self,
        player_one: discord.Member,
        player_two: discord.Member,
        dsr: list[str],
        stage_ban_count: int,
    ) -> None:
        super().__init__(timeout=180)
        self.player_one = player_one
        self.dsr = dsr
        self.player_two = player_two
        self.turn = player_one
        self.ban_count = 0
        self.stage_ban_count = stage_ban_count
        self.choice: Optional[str] = None

    @discord.ui.button(label="Battlefield", emoji="⚔️", style=discord.ButtonStyle.gray)
    async def battlefield(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Final Destination", emoji="👾", style=discord.ButtonStyle.gray
    )
    async def final_destination(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Small Battlefield", emoji="🗡️", style=discord.ButtonStyle.gray
    )
    async def small_battlefield(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(label="Smashville", emoji="🏛️", style=discord.ButtonStyle.gray)
    async def smashville(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Town and City", emoji="🚌", style=discord.ButtonStyle.gray
    )
    async def town_and_city(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Pokémon Stadium 2", emoji="🦎", style=discord.ButtonStyle.gray
    )
    async def pokemon_stadium_2(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Kalos Pokémon League", emoji="🐋", style=discord.ButtonStyle.gray
    )
    async def kalos_pokemon_league(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Hollow Bastion", emoji="🏰", style=discord.ButtonStyle.gray
    )
    async def hollow_bastion(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    @discord.ui.button(
        label="Yoshi's Story", emoji="🐣", style=discord.ButtonStyle.gray
    )
    async def yoshis_story(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.ban_stage(interaction, button)

    async def ban_stage(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Handles the banning of stages in the counterpick phase, after Game 1."""
        # After the first player banned two or three stages, the second player can choose one.
        if self.turn == self.player_two:
            button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(
                content=f"**Stage bans**\nThe chosen stage is: **{button.label}**",
                view=self,
            )
            self.choice = button.label
            self.stop()
        elif self.ban_count == self.stage_ban_count - 1:
            button.disabled = True
            button.style = discord.ButtonStyle.red
            self.turn = self.player_two

            # The second player cannot choose a stage he already won on.
            for button in [c for c in self.children if c.label in self.dsr]:
                button.disabled = True

            await interaction.response.edit_message(
                content=f"**Stage bans**\n{self.turn.mention}, please *pick* a stage:",
                view=self,
            )
        else:
            self.ban_count += 1
            button.disabled = True
            button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(
                content=f"**Stage bans**\n{self.turn.mention}, please **ban {self.stage_ban_count} stages** in total:",
                view=self,
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.player_one, self.player_two):
            return False
        if interaction.user == self.player_one and self.turn == self.player_one:
            return True
        return interaction.user == self.player_two and self.turn == self.player_two
