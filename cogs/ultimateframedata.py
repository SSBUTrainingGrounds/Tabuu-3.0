from typing import Optional, Union

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from stringmatch import Match

from utils.character import get_single_character_name
from utils.ids import GuildIDs
from views.move_select import MoveView


class UltimateFrameData(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def handle_stats(self, ctx: commands.Context, character: str) -> None:
        """Handles displaying the stats for a character."""
        async with aiosqlite.connect("./db/ultimateframedata.db") as db:
            stats = await db.execute_fetchall(
                """SELECT * FROM stats WHERE character = :character""",
                {"character": character},
            )

            if len(stats) == 0:
                await ctx.send(
                    "Character not found.\nMake sure you are not searching for special characters like Pokemon Trainer or Pyra & Mythra, but instead for the individual characters like Charizard or Mythra."
                )
                return

            # The following queries are used to get the rank of each stat for the character.
            # The SUBSTR is needed because the data is stored as "Stat - Value" (Weight - 113).
            weights = await db.execute_fetchall(
                """SELECT row_number() OVER(ORDER BY CAST(SUBSTR(weight, 9) AS INTEGER) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            gravities = await db.execute_fetchall(
                """SELECT row_number() OVER(ORDER BY CAST(SUBSTR(gravity, 11, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            walk_speeds = await db.execute_fetchall(
                """SELECT row_number() OVER(ORDER BY CAST(SUBSTR(walk_speed, 14, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            run_speeds = await db.execute_fetchall(
                """SELECT row_number() OVER(ORDER BY CAST(SUBSTR(run_speed, 13, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            initial_dashs = await db.execute_fetchall(
                """SELECT row_number() OVER(ORDER BY CAST(SUBSTR(initial_dash, 16, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            air_speeds = await db.execute_fetchall(
                """SELECT row_number() OVER (ORDER BY CAST(SUBSTR(air_speed, 13, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            total_air_accelerations = await db.execute_fetchall(
                """SELECT row_number() OVER (ORDER BY CAST(SUBSTR(total_air_acceleration, 26, 5) AS FLOAT) DESC) as row_num, character FROM stats""",
                {"character": character},
            )

            # Gets the actual ranks.
            weight = [w[0] for w in weights if w[1] == character][0]
            gravity = [g[0] for g in gravities if g[1] == character][0]
            walk_speed = [w[0] for w in walk_speeds if w[1] == character][0]
            run_speed = [r[0] for r in run_speeds if r[1] == character][0]
            initial_dash = [i[0] for i in initial_dashs if i[1] == character][0]
            air_speed = [a[0] for a in air_speeds if a[1] == character][0]
            total_air_acceleration = [
                t[0] for t in total_air_accelerations if t[1] == character
            ][0]

        stats = stats[0]

        rank_list = [
            weight,
            gravity,
            walk_speed,
            run_speed,
            initial_dash,
            air_speed,
            total_air_acceleration,
        ]

        # And then we format the stats into a nice embed.
        description = ""

        # All of the ranked stats above.
        for i, s in enumerate(rank_list):
            stat = stats[i + 2]
            [title, value] = stat.split(" — ", 1)
            # The characters are always gonna be 89 for Smash Ultimate now.
            description += (
                f"**{title}**: {discord.utils.escape_markdown(value)} (#{s}/89)\n"
            )

        # SH / FH and Fall Speeds
        for s in stats[len(rank_list) + 2 : len(rank_list) + 4]:
            [title, value] = s.split(" — ", 1)
            description += f"**{title}**: {discord.utils.escape_markdown(value)}\n"

        # These are the Out of Shield options.
        for i, s in enumerate(stats[len(rank_list) + 4 : len(rank_list) + 7]):
            [title, value] = s.split(" — ", 1)
            title = title.replace("Out of Shield, ", f"**OOS #{i + 1}**: ")
            description += f"{title} - {discord.utils.escape_markdown(value)}\n"

        # And then the remaining stats.
        for s in stats[len(rank_list) + 7 :]:
            [title, value] = s.split(" — ", 1)
            description += f"**{title}**: {discord.utils.escape_markdown(value)}\n"

        embed = discord.Embed(
            title=f"{character.title()} - Stats",
            color=self.bot.colour,
            description=description,
        )

        embed.set_image(url=stats[1])

        await ctx.send(embed=embed)

    async def get_move_embed(
        self, move: Union[str, str, Optional[str]]
    ) -> discord.Embed:
        """Gets the move embed for a specific move."""
        movename = f"{move[4].title()}"

        titles = [
            "Startup Frames",
            "Active Frames",
            "Endlag Frames",
            "On Shield Frames",
            "Shieldlag Frames",
            "Shieldstun Frames",
            "Total Frames",
            "Autocancels",
            "Actionable Before Landing",
            "Damage",
        ]

        description = ""

        # We append the description with every move above.
        # Starting at 5 because the first 4 elements are the character, input, move name and full move name, and special hitbox.
        for i, title in enumerate(titles):
            if move[i + 5]:
                description += f"**{title}**: {discord.utils.escape_markdown(move[i + 5].replace('**', '--'))}\n"

        description += f"**Notes**: {discord.utils.escape_markdown(move[-1])}"

        embed = discord.Embed(
            title=movename,
            color=self.bot.colour,
            description=description,
        )

        hitbox_gif = move[-2]

        if hitbox_gif is not None:
            hitbox_gif = hitbox_gif.replace(" ", "%20")

        embed.set_image(url=hitbox_gif)

        return embed

    def replace_common_abbreviations(self, input_str: str) -> str:
        """Replaces common abbreviations with their full names."""

        input_str = input_str.lower()

        input_str = input_str.replace("-", " ")

        replacements = {
            "nair": "Neutral Air",
            "fair": "Forward Air",
            "bair": "Back Air",
            "dair": "Down Air",
            "uair": "Up Air",
            "ftilt": "Forward Tilt",
            "utilt": "Up Tilt",
            "dtilt": "Down Tilt",
            "fsmash": "Forward Smash",
            "usmash": "Up Smash",
            "dsmash": "Down Smash",
        }

        for k, v in replacements.items():
            if input_str == k:
                input_str = v

        return input_str

    async def handle_move(
        self, ctx: commands.Context, character: str, move_name: str
    ) -> None:
        """Handles displaying the move data for a character."""

        move_name = self.replace_common_abbreviations(move_name)

        async with aiosqlite.connect("./db/ultimateframedata.db") as db:
            move = await db.execute_fetchall(
                """SELECT * FROM moves WHERE character = :character AND TRIM(input) = :move_name COLLATE NOCASE 
                OR character = :character AND TRIM(move_name) = :move_name COLLATE NOCASE
                OR character = :character AND TRIM(full_move_name) = :move_name COLLATE NOCASE""",
                {"character": character, "move_name": move_name},
            )

            all_moves = await db.execute_fetchall(
                """SELECT full_move_name FROM moves WHERE character = :character""",
                {"character": character},
            )

        # If a unique move was found, we can just send the embed.
        if len(move) == 1:
            move = move[0]

            embed = await self.get_move_embed(move)

            await ctx.send(embed=embed)
            return

        # If the move is not unique, we'll prompt the user to select one.
        if len(move) > 1:
            moves = [m[4] for m in move]

            view = MoveView(ctx.author, character, moves)

            await ctx.send(
                "Multiple moves found, please select one:",
                view=view,
            )

            timed_out = await view.wait()

            if timed_out or view.selected_move is None:
                await ctx.reply("You didn't select a move.")
                return

            move = view.selected_move

            embed = await self.get_move_embed(move)

            await ctx.send(embed=embed)
            return

        # And if the move is not found, we'll try to get the best matches for the user to choose from.
        match = Match(ignore_case=True, include_partial=True)

        moves = [m[0] for m in all_moves]

        best_matches = match.get_best_matches(move_name, moves, score=40, limit=25)

        # This will only happen if the move is way off.
        if len(best_matches) == 0:
            await ctx.send("No match for this move could be found for this character.")
            return

        view = MoveView(ctx.author, character, best_matches)

        await ctx.send(
            "Move not found. Here are the best matches, please select one:",
            view=view,
        )

        timed_out = await view.wait()

        if timed_out or view.selected_move is None:
            await ctx.reply("You didn't select a move.")
            return

        # The move can be either None, "Stats" or a move tuple, directly queried from the database.
        move = view.selected_move

        if move is None:
            await ctx.send("Something went wrong, the move could not be found.")
            return

        if move == "Stats":
            await self.handle_stats(ctx, character)
            return

        embed = await self.get_move_embed(move)

        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["s", "v"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(character="The character you are looking for.")
    @app_commands.describe(move_name="The move you are looking for.")
    async def show(
        self,
        ctx: commands.Context,
        character: str,
        *,
        move_name: str = "Stats",
    ) -> None:
        """Shows the frame data for a specific character move.
        If the character in question has multiple moves with the same name, you will be prompted to select one.
        If you only want the stats of the character, use "stats" as the move name, or leave it empty.

        You may need to use "quotes" around the character name if it has multiple words, when using the message command: `%show "duck hunt"`.
        """
        character = get_single_character_name(character)

        if character is None:
            await ctx.send("Character not found.")
            return

        if move_name.lower() == "stats":
            await self.handle_stats(ctx, character)
            return

        await self.handle_move(ctx, character, move_name)
        return

    @show.autocomplete("character")
    async def character_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        await interaction.response.defer()

        choices = []

        async with aiosqlite.connect("./db/ultimateframedata.db") as db:
            chars = await db.execute_fetchall("""SELECT character FROM stats""")

        chars = [c[0].title() for c in chars]

        # We dont use the autocomplete function here from utils.search,
        # cause we need some customisation here.
        match = Match(ignore_case=True, include_partial=True)

        match_list = match.get_best_matches(current, chars, score=40, limit=25)

        choices.extend(
            app_commands.Choice(name=match, value=match) for match in match_list
        )

        return choices[:25]

    @show.autocomplete("move_name")
    async def move_name_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        await interaction.response.defer()

        choices = []

        if interaction.namespace.character is None:
            return choices

        character = interaction.namespace.character.lower()

        async with aiosqlite.connect("./db/ultimateframedata.db") as db:
            raw_moves = await db.execute_fetchall(
                """SELECT full_move_name FROM moves WHERE character = :character""",
                {"character": character},
            )

        match = Match(ignore_case=True, include_partial=True)

        moves = [m[0] for m in raw_moves]
        moves.append("Stats")

        match_list = match.get_best_matches(current, moves, score=40, limit=25)

        choices.extend(
            app_commands.Choice(name=match, value=match) for match in match_list
        )

        return choices[:25]

    @show.error
    async def show_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await ctx.send(error)


async def setup(bot) -> None:
    await bot.add_cog(UltimateFrameData(bot))
    print("UltimateFrameData cog loaded")
