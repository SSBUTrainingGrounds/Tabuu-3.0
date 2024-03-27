import aiosqlite
import discord

from utils.character import match_character


class MoveSelect(discord.ui.Select):
    def __init__(
        self,
        user: discord.User,
        character: str,
        moves: list[str],
    ) -> None:

        character_emoji = "✅"
        matching_emoji = match_character(character)

        if matching_emoji:
            character_emoji = matching_emoji[0]

        # Checks for duplicates in the options list and append a number to the end of the move name.
        # Shouldn't be necessary, but just in case.
        def rename_duplicates(old: list[str]) -> str:
            seen = {}
            for x in old:
                if x in seen:
                    seen[x] += 1
                    yield f"{x} ({seen[x]})"
                else:
                    seen[x] = 1
                    yield x

        options = [
            discord.SelectOption(label=move, value=move, emoji=character_emoji)
            for move in list(rename_duplicates(moves))
        ]

        super().__init__(
            placeholder="Select a move from the best matches",
            min_values=1,
            max_values=1,
            options=options,
        )

        self.user = user
        self.character = character
        self.moves = moves

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        # Special check for the Stats option.
        if self.values[0] == "Stats":
            self.view.selected_move = "Stats"
            self.view.stop()
            return

        async with aiosqlite.connect("./db/ultimateframedata.db") as db:
            actual_move = await db.execute_fetchall(
                """SELECT * FROM moves WHERE character = :character AND TRIM(input) = :move_name COLLATE NOCASE 
                OR character = :character AND TRIM(move_name) = :move_name COLLATE NOCASE
                OR character = :character AND TRIM(full_move_name) = :move_name COLLATE NOCASE""",
                {"character": self.character, "move_name": self.values[0]},
            )

        # Otherwise the move should be found, but just in case we'll check again.
        if len(actual_move) == 0 or actual_move[0] is None:
            await interaction.message.edit(
                content="Something went wrong, the move could not be found in the database.",
                view=None,
            )
            self.view.stop()
            return

        self.view.selected_move = actual_move[0]

        self.view.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id


class MoveView(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(self, user: discord.User, character: str, moves: list[str]) -> None:
        super().__init__(timeout=300)

        self.user = user
        self.selected_move = None

        self.add_item(MoveSelect(user, character, moves))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id
