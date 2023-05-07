import aiosqlite
import discord


class MacroModal(discord.ui.Modal, title="Create a new macro"):
    """A modal to create a new macro."""

    def __init__(self) -> None:
        super().__init__()

    name = discord.ui.TextInput(
        label="Macro name:",
        style=discord.TextStyle.short,
        placeholder="The name of your macro.",
        max_length=50,
    )

    payload = discord.ui.TextInput(
        label="Macro Payload:",
        style=discord.TextStyle.paragraph,
        placeholder="The payload of your macro (Markdown supported).",
        max_length=1500,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        macro_name = self.name.value.lower()

        # list of every command together with the aliases registered.
        # Cannot use those for a macro, obviously.
        command_list = [command.name for command in interaction.client.commands]
        for command in interaction.client.commands:
            command_list.extend(iter(command.aliases))

        async with aiosqlite.connect("./db/database.db") as db:
            matching_macro = await db.execute_fetchall(
                """SELECT name FROM macros WHERE name = :name""", {"name": macro_name}
            )

            # Basic checks for invalid stuff.
            if len(matching_macro) != 0:
                await interaction.response.send_message(
                    "This name was already taken. "
                    "If you want to update this macro please delete it first and then create it again."
                )
                return

            if macro_name in command_list:
                await interaction.response.send_message(
                    "This name is already being used for a command! Please use a different one."
                )
                return

            await db.execute(
                """INSERT INTO macros VALUES (:name, :payload, :uses, :author)""",
                {
                    "name": macro_name,
                    "payload": self.payload.value,
                    "uses": 0,
                    "author": interaction.user.id,
                },
            )

            await db.commit()

        await interaction.response.send_message(
            f"New macro `{macro_name}` was created.\nOutput:\n`{self.payload.value}`"
        )


class MacroButton(discord.ui.View):
    def __init__(self, author: discord.User) -> None:
        self.author = author
        super().__init__(timeout=60)

    @discord.ui.button(
        label="Create a new macro!", emoji="🖨️", style=discord.ButtonStyle.gray
    )
    async def macro_button(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_modal(MacroModal())
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.author
