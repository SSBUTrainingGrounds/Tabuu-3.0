import json
from typing import Optional

import aiosqlite
import discord


class CharacterDropdown(discord.ui.Select):
    """Adds the characters to the Dropdown menu."""

    def __init__(
        self,
        characters: list[str, str, str],
        current_values: list[str] = None,
    ) -> None:
        options = [
            discord.SelectOption(
                label=character[0].title(),
                description=f"ID: {', '.join(character[1])}",
                emoji=character[2],
                default=character[2] in current_values,
                value=character[2],
            )
            for character in characters
        ]

        super().__init__(
            placeholder=f"Characters {characters[0][1][0]} - {characters[-1][1][0]} ({characters[0][0].title()} - {characters[-1][0].title()})",
            min_values=0,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        for character in self.options:
            if str(character.emoji) in self.view.current_values:
                self.view.current_values.remove(character.value)

        for character in self.values:
            if character not in self.view.current_values:
                self.view.current_values.append(character)

        await interaction.response.defer()


class CharacterView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(
        self,
        user: discord.User,
        current_values: list[str],
        character_type: str,
        max_values: Optional[int] = 7,
    ) -> None:
        super().__init__(timeout=300)

        self.user = user
        self.max_values = max_values
        self.current_values = current_values
        self.character_type = character_type

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

        self.add_item(CharacterDropdown(char_options[:25], current_values))
        self.add_item(CharacterDropdown(char_options[25:50], current_values))
        self.add_item(CharacterDropdown(char_options[50:75], current_values))
        self.add_item(CharacterDropdown(char_options[75:], current_values))

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if len(self.current_values) > self.max_values:
            await interaction.response.send_message(
                f"You can only select up to {self.max_values} characters, "
                f"please deselect at least {len(self.current_values) - self.max_values} character(s).",
                ephemeral=True,
            )
            return

        chars = "" if len(self.current_values) == 0 else " ".join(self.current_values)

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET """
                + self.character_type
                + """ = :chars WHERE user_id = :user_id""",
                {"chars": chars, "user_id": self.user.id},
            )

            await db.commit()

        if not chars:
            await interaction.response.send_message(
                f"{self.user.mention}, I have deleted your {self.character_type}."
            )
        else:
            await interaction.response.send_message(
                f"{self.user.mention}, I have set your {self.character_type} to: {chars}"
            )

        self.stop()

    @discord.ui.button(label="Deselect All", style=discord.ButtonStyle.red, row=4)
    async def deselect_all(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        self.current_values = []

        for child in self.children:
            if isinstance(child, CharacterDropdown):
                for option in child.options:
                    option.default = False

        await interaction.message.edit(view=self)

        await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id


class RegionDropdown(discord.ui.Select):
    """Adds the regions to the Dropdown menu."""

    def __init__(self, user: discord.User) -> None:
        options = [
            discord.SelectOption(label="None", emoji="❌"),
            discord.SelectOption(label="North America", emoji="🌎"),
            discord.SelectOption(label="NA East", emoji="🗽"),
            discord.SelectOption(label="NA West", emoji="🌉"),
            discord.SelectOption(label="NA South", emoji="🌵"),
            discord.SelectOption(label="Europe", emoji="🇪🇺"),
            discord.SelectOption(label="South America", emoji="🌴"),
            discord.SelectOption(label="Asia", emoji="⛩"),
            discord.SelectOption(label="Oceania", emoji="🌊"),
            discord.SelectOption(label="Africa", emoji="🦒"),
        ]

        self.user = user

        super().__init__(
            placeholder="Select your region",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        region = self.values[0]

        if region == "None":
            region = ""

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET region = :region WHERE user_id = :user_id""",
                {"region": region, "user_id": self.user.id},
            )

            await db.commit()

        if not region:
            await interaction.response.send_message(
                f"{self.user.mention}, I have deleted your region."
            )
        else:
            await interaction.response.send_message(
                f"{self.user.mention}, I have set your region to: {self.values[0]}"
            )

        self.view.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id


class RegionView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(self, user: discord.User) -> None:
        super().__init__(timeout=300)

        self.user = user

        self.add_item(RegionDropdown(user))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id


class ColourDropdown(discord.ui.Select):
    """Adds some predefined colours to the Dropdown menu."""

    def __init__(self, user: discord.User) -> None:
        options = [
            discord.SelectOption(
                label="Black", emoji="⚫", value="0x000000", description="#000000"
            ),
            discord.SelectOption(
                label="White", emoji="⚪", value="0xFFFFFF", description="#FFFFFF"
            ),
            discord.SelectOption(
                label="Red", emoji="🔴", value="0xFF0000", description="#FF0000"
            ),
            discord.SelectOption(
                label="Green", emoji="🟢", value="0x00FF00", description="#00FF00"
            ),
            discord.SelectOption(
                label="Blue", emoji="🔵", value="0x0000FF", description="#0000FF"
            ),
            discord.SelectOption(
                label="Yellow", emoji="🟡", value="0xFFFF00", description="#FFFF00"
            ),
            discord.SelectOption(
                label="Orange", emoji="🟠", value="0xFFA500", description="#FFA500"
            ),
            discord.SelectOption(
                label="Purple", emoji="🟣", value="0x800080", description="#800080"
            ),
            discord.SelectOption(
                label="Brown", emoji="🟤", value="0xA52A2A", description="#A52A2A"
            ),
            # Kinda hard to find emojis for some of those colours.
            discord.SelectOption(
                label="Pink", emoji="🧠", value="0xFFC0CB", description="#FFC0CB"
            ),
            discord.SelectOption(
                label="Grey", emoji="🏛", value="0x808080", description="#808080"
            ),
            discord.SelectOption(
                label="Dark Grey", emoji="🗻", value="0x3B3B3B", description="#3B3B3B"
            ),
            discord.SelectOption(
                label="Cyan", emoji="❄", value="0x00D9FF", description="#00D9FF"
            ),
            discord.SelectOption(
                label="Lime", emoji="🍐", value="0xBFFF00", description="#BFFF00"
            ),
            discord.SelectOption(
                label="Ruby", emoji="🍒", value="0xD10056", description="#D10056"
            ),
            discord.SelectOption(
                label="Salmon", emoji="🍥", value="0xFA8072", description="#FA8072"
            ),
            discord.SelectOption(
                label="Turquoise", emoji="🌊", value="0x40E0D0", description="#40E0D0"
            ),
            discord.SelectOption(
                label="Peach", emoji="🍑", value="0xFFE5B4", description="#FFE5B4"
            ),
            discord.SelectOption(
                label="Beige", emoji="📜", value="0xF5F5DC", description="#F5F5DC"
            ),
            discord.SelectOption(
                label="Emerald", emoji="🥦", value="0x009975", description="#009975"
            ),
            discord.SelectOption(
                label="Magenta", emoji="🌸", value="0xFF00FF", description="#FF00FF"
            ),
            discord.SelectOption(
                label="Maroon", emoji="💼", value="0x800000", description="#800000"
            ),
            discord.SelectOption(
                label="Tan", emoji="🍞", value="0xD2B48C", description="#D2B48C"
            ),
            discord.SelectOption(
                label="Periwinkle", emoji="🔮", value="0xCCCCFF", description="#CCCCFF"
            ),
            discord.SelectOption(
                label="Gold", emoji="🥇", value="0xD4AF37", description="#D4AF37"
            ),
        ]

        self.user = user

        super().__init__(
            placeholder="Choose from a preset colour",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        colour = self.values[0]

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET colour = :colour WHERE user_id = :user_id""",
                {"colour": int(colour, 16), "user_id": self.user.id},
            )

            await db.commit()

        await interaction.response.send_message(
            f"{self.user.mention}, I have set your colour to: {colour}"
        )

        self.view.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id


class ColourModal(discord.ui.Modal, title="Custom Colour Picker"):
    """A modal for picking a custom colour."""

    def __init__(self, user: discord.User) -> None:
        self.user = user

        super().__init__(timeout=300)

    colour = discord.ui.TextInput(
        label="Your custom color in hex format.",
        placeholder="#000000",
        required=True,
        min_length=7,
        max_length=7,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        colour = self.children[0].value

        if not colour.startswith("#"):
            await interaction.response.send_message(
                f"{self.user.mention}, please enter a valid hex colour.\n"
                "If you are confused you can use the dropdown menu, or head over to a website like this https://color.hailpixel.com/ to get a valid hex colour."
            )

            return

        colour = colour.replace("#", "0x")

        try:
            hex_colour = int(colour, 16)
        except ValueError:
            await interaction.response.send_message(
                f"{self.user.mention}, please enter a valid hex colour.\n"
                "If you are confused you can use the dropdown menu, or head over to a website like this https://color.hailpixel.com/ to get a valid hex colour."
            )

            return

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE profile SET colour = :colour WHERE user_id = :user_id""",
                {"colour": hex_colour, "user_id": self.user.id},
            )

            await db.commit()

        await interaction.response.send_message(
            f"{self.user.mention}, I have set your colour to: {colour}"
        )


class ColourView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(self, user: discord.User) -> None:
        super().__init__(timeout=300)

        self.user = user

        self.add_item(ColourDropdown(user))

    @discord.ui.button(
        label="Choose a Custom Colour",
        style=discord.ButtonStyle.gray,
        emoji="🎨",
        row=1,
    )
    async def custom_colour(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        colour_modal = ColourModal(self.user)

        await interaction.response.send_modal(colour_modal)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id
