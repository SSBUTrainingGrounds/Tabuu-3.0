import discord


class RpsButtons(discord.ui.View):
    """Contains the RPS Game Buttons."""

    def __init__(self, author: discord.Member, member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        self.message = None

    # Not sure why the Rock Emoji fails to display here, it does display properly on Discord.
    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.gray)
    async def rock(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Registers the author and user input for Rock.
        Stops if both parties made a choice.
        """

        await interaction.response.send_message("You chose Rock!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Rock"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Rock"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Paper", emoji="📝", style=discord.ButtonStyle.gray)
    async def paper(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Registers the author and user input for Paper.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Paper!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Paper"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Paper"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.gray)
    async def scissors(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        """Registers the author and user input for Scissors.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Scissors!", ephemeral=True)
        if interaction.user.id == self.author.id:
            self.authorchoice = "Scissors"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Scissors"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ignores every other member except the author and mentioned member.
        return interaction.user in (self.member, self.author)

    async def on_timeout(self) -> None:
        # If the match didnt go through as planned.
        if self.authorchoice is None and self.memberchoice is None:
            await self.message.reply(
                "Match timed out! Both parties took too long to pick a choice!"
            )
        elif self.authorchoice is None:
            await self.message.reply(
                f"Match timed out! {self.author.mention} took too long to pick a choice!"
            )
        elif self.memberchoice is None:
            await self.message.reply(
                f"Match timed out! {self.member.mention} took too long to pick a choice!"
            )
