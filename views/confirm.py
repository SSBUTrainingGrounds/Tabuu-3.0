import discord


class ConfirmationButtons(discord.ui.View):
    """The buttons for confirming/cancelling the request."""

    def __init__(self, member: discord.Member = None) -> None:
        super().__init__()

        self.confirm = None
        self.member = member
        self.timeout = 60

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✔️")
    async def confirm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.confirm = True
        self.clear_items()
        await interaction.response.edit_message(content="Confirming...", view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.confirm = False
        self.clear_items()
        await interaction.response.edit_message(content="Cancelling...", view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # We make sure its the right member thats pressing the button.
        return interaction.user == self.member
