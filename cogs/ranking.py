import asyncio
import datetime
import json
import random
from typing import Optional

import aiosqlite
import discord
import trueskill
from discord import app_commands
from discord.ext import commands, tasks

import utils.check
import utils.time
from utils.ids import (
    Emojis,
    GuildIDs,
    GuildNames,
    TGArenaChannelIDs,
    TGMatchmakingRoleIDs,
    TGRoleIDs,
)


class StarterStageButtons(discord.ui.View):
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

    @discord.ui.button(label="Town and City", emoji="🚌", style=discord.ButtonStyle.gray)
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

    @discord.ui.button(label="Town and City", emoji="🚌", style=discord.ButtonStyle.gray)
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

    @discord.ui.button(label="Yoshi's Story", emoji="🐣", style=discord.ButtonStyle.gray)
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
                content=f"**Stage bans**\n{self.turn.mention}, please *pick* a stage:",
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
    def __init__(self, player_one: discord.Member, player_two: discord.Member) -> None:
        super().__init__(timeout=1800)
        self.player_one = player_one
        self.player_two = player_two
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
            content="When you're done, click on the button of the winner of Game 1 to report the match.",
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
            content="When you're done, click on the button of the winner of Game 1 to report the match.",
            view=self,
        )
        self.cancelled = True
        self.stop()
        await interaction.channel.send(
            f"Match cancelled.\n{interaction.user.mention} called a moderator: <@&{TGRoleIDs.MOD_ROLE}>!"
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in (self.player_one.id, self.player_two.id)


class Ranking(commands.Cog):
    """Contains the ranked portion of our matchmaking system."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.decay_ratings.start()

    def cog_unload(self) -> None:
        self.decay_ratings.cancel()

    async def get_ranked_role(
        self, player: trueskill.Rating, guild: discord.Guild
    ) -> discord.Role:
        """Retrieves the ranked role of a user."""
        rating = self.get_display_rank(player)

        # We multiply the rating by 100 and add 1000, compared to the original Microsoft TrueSkill algorithm.
        # So a rating of 5000 equals a rank of 40, the ranks were used in Halo 3 where 50 was the highest rank.
        # A rating of 40 was also fairly hard to achieve so this is the current max rank for us.
        if rating >= 5000:
            return discord.utils.get(
                guild.roles, id=TGMatchmakingRoleIDs.GROUNDS_MASTER
            )
        elif rating >= 4200:
            return discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.FIVE_STAR)
        elif rating >= 3400:
            return discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.FOUR_STAR)
        elif rating >= 2600:
            return discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.THREE_STAR)
        elif rating >= 1800:
            return discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.TWO_STAR)
        else:
            # This rank should hopefully also be fairly hard to obtain, if you do not lose every single match.
            # This would equal a rank of below 8 in Halo 3.
            return discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.ONE_STAR)

    def get_all_ranked_roles(self, guild: discord.Guild) -> list[discord.Role]:
        """Gets you every ranked role."""
        role1 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.ONE_STAR)
        role2 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.TWO_STAR)
        role3 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.THREE_STAR)
        role4 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.FOUR_STAR)
        role5 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.FIVE_STAR)
        role6 = discord.utils.get(guild.roles, id=TGMatchmakingRoleIDs.GROUNDS_MASTER)
        return [role1, role2, role3, role4, role5, role6]

    async def remove_ranked_roles(
        self, member: discord.Member, guild: discord.Guild
    ) -> None:
        """Removes every ranked role a user has."""
        roles = self.get_all_ranked_roles(guild)
        await member.remove_roles(*roles)

    async def update_ranked_role(
        self, member: discord.Member, guild: discord.Guild, threshold: int = 5
    ) -> None:
        """This function updates the ranked roles of a member.
        The role change only triggers if the user does not have their current rating role,
        so its fine to remove ALL others first and then give the new one out.
        Also we only start to give these out at 5 games played automatically.
        """
        player, wins, losses, _ = await self.get_player(member)

        if wins + losses >= threshold:
            role = await self.get_ranked_role(player, guild)
            if role not in member.roles:
                await self.remove_ranked_roles(member, guild)
                await member.add_roles(role)

    async def create_ranked_profile(self, user: discord.User) -> None:
        """Creates an entry in the ranked file for a user,
        if the user is not already in there.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            matching_player = await db.execute_fetchall(
                """SELECT * FROM trueskill WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

            if len(matching_player) == 0:
                rating = 25.0
                deviation = 25 / 3
                wins = 0
                losses = 0
                matches = ""

                await db.execute(
                    """INSERT INTO trueskill VALUES (:user_id, :rating, :deviation, :wins, :losses, :matches)""",
                    {
                        "user_id": user.id,
                        "rating": rating,
                        "deviation": deviation,
                        "wins": wins,
                        "losses": losses,
                        "matches": matches,
                    },
                )

                await db.commit()

    async def update_ranked_profiles(
        self,
        winner: discord.User,
        winner_rating: trueskill.Rating,
        loser: discord.User,
        loser_rating: trueskill.Rating,
    ) -> None:
        """Updates a ranked profile with the new stats."""
        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """UPDATE trueskill SET
                    wins = wins + 1,
                    matches = matches || "W",
                    rating = :new_rating,
                    deviation = :new_deviation
                    WHERE user_id = :user_id""",
                {
                    "new_rating": winner_rating.mu,
                    "new_deviation": winner_rating.sigma,
                    "user_id": winner.id,
                },
            )

            await db.execute(
                """UPDATE trueskill SET
                    losses = losses + 1,
                    matches = matches || "L",
                    rating = :new_rating,
                    deviation = :new_deviation
                    WHERE user_id = :user_id""",
                {
                    "new_rating": loser_rating.mu,
                    "new_deviation": loser_rating.sigma,
                    "user_id": loser.id,
                },
            )
            await db.commit()

    async def log_match(
        self,
        match_id: int,
        winner: discord.User,
        old_winner: trueskill.Rating,
        new_winner: trueskill.Rating,
        loser: discord.User,
        old_loser: trueskill.Rating,
        new_loser: trueskill.Rating,
    ) -> None:
        """Logs a match in the database."""

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """INSERT INTO matches VALUES (
                :match_id,
                :winner_id,
                :loser_id,
                :timestamp,
                :old_winner_rating,
                :old_winner_deviation,
                :old_loser_rating,
                :old_loser_deviation,
                :new_winner_rating,
                :new_winner_deviation,
                :new_loser_rating,
                :new_loser_deviation)""",
                {
                    "match_id": match_id,
                    "winner_id": winner.id,
                    "loser_id": loser.id,
                    "timestamp": int(discord.utils.utcnow().timestamp()),
                    "old_winner_rating": old_winner.mu,
                    "old_winner_deviation": old_winner.sigma,
                    "old_loser_rating": old_loser.mu,
                    "old_loser_deviation": old_loser.sigma,
                    "new_winner_rating": new_winner.mu,
                    "new_winner_deviation": new_winner.sigma,
                    "new_loser_rating": new_loser.mu,
                    "new_loser_deviation": new_loser.sigma,
                },
            )

            await db.commit()

    async def save_match(
        self, winner: discord.User, loser: discord.User, guild: discord.Guild
    ) -> str:
        """Handles the reporting and saving of the match and the results in the database.
        Returns a message string to send to the users."""
        # Making sure both players exist in the database before getting their ratings.
        await self.create_ranked_profile(winner)
        await self.create_ranked_profile(loser)

        (winner_rating, _, _, _) = await self.get_player(winner)
        (loser_rating, _, _, _) = await self.get_player(loser)

        # Getting the updated ratings and updating the database.
        (new_winner_rating, new_loser_rating) = trueskill.rate_1vs1(
            winner_rating, loser_rating
        )

        await self.update_ranked_profiles(
            winner, new_winner_rating, loser, new_loser_rating
        )

        # Logging the match in the database.
        match_id = random.randint(10000000, 99999999)

        await self.log_match(
            match_id,
            winner,
            winner_rating,
            new_winner_rating,
            loser,
            loser_rating,
            new_loser_rating,
        )

        await self.update_ranked_role(winner, guild)
        await self.update_ranked_role(loser, guild)

        # Returning a neatly formatted message to display to the users.
        winner_diff = self.get_display_rank(new_winner_rating) - self.get_display_rank(
            winner_rating
        )
        loser_diff = self.get_display_rank(new_loser_rating) - self.get_display_rank(
            loser_rating
        )

        if winner_diff == 0.00:
            winner_diff_str = f"⇄ {winner_diff}"
        elif winner_diff > 0:
            winner_diff_str = f"🠕 +{winner_diff}"
        else:
            winner_diff_str = f"🠗 {winner_diff}"

        if loser_diff == 0.00:
            loser_diff_str = f"⇄ {loser_diff}"
        elif loser_diff > 0:
            loser_diff_str = f"🠕 +{loser_diff}"
        else:
            loser_diff_str = f"🠗 {loser_diff}"

        return (
            f"Game #{match_id} successfully reported!\n{winner.mention} won!\n\nUpdated ratings: \n"
            f"{winner.mention}: **{self.get_display_rank(winner_rating)}** → **{self.get_display_rank(new_winner_rating)}** ({winner_diff_str})\n"
            f"{loser.mention}: **{self.get_display_rank(loser_rating)}** → **{self.get_display_rank(new_loser_rating)}** ({loser_diff_str})\n\n"
        )

    async def get_player(
        self, user: discord.User
    ) -> tuple[trueskill.Rating, int, int, str]:
        """Gets a player rating, their wins, losses and matches from the database."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM trueskill WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        return (
            (
                trueskill.Rating(matching_user[0][1], matching_user[0][2]),
                matching_user[0][3],
                matching_user[0][4],
                matching_user[0][5],
            )
            if matching_user
            else (trueskill.Rating(), 0, 0, "")
        )

    def get_display_rank(self, player: trueskill.Rating) -> float:
        """Gets the conservatively estimated rank of a player, scaled."""
        # This is the formula used by Microsoft, for example in Halo 3.
        # But we multiply by 100 and add 1000 to get a nicer number.
        return max(round(((player.mu - 3 * player.sigma) * 100) + 1000), 0)

    def decay_deviation(self, player: trueskill.Rating) -> trueskill.Rating:
        """Decays the deviation of a player by 1%."""
        return trueskill.Rating(player.mu, min(player.sigma * 1.01, 25 / 3))

    def store_ranked_ping(self, ctx: commands.Context, timestamp: float) -> None:
        """Stores your ranked ping."""
        with open(r"./json/ranked.json", "r", encoding="utf-8") as f:
            rankedusers = json.load(f)

        rankedusers[f"{ctx.author.id}"] = {}
        rankedusers[f"{ctx.author.id}"] = {"channel": ctx.channel.id, "time": timestamp}

        with open(r"./json/ranked.json", "w", encoding="utf-8") as f:
            json.dump(rankedusers, f, indent=4)

    def delete_ranked_ping(self, ctx: commands.Context) -> None:
        """Deletes your ranked ping."""
        with open(r"./json/ranked.json", "r", encoding="utf-8") as f:
            rankedusers = json.load(f)

        try:
            del rankedusers[f"{ctx.message.author.id}"]
        except KeyError:
            logger = self.bot.get_logger("bot.mm")
            logger.warning(
                f"Tried to delete a ranked ping by {str(ctx.message.author)} but the ping was already deleted."
            )

        with open(r"./json/ranked.json", "w", encoding="utf-8") as f:
            json.dump(rankedusers, f, indent=4)

    def get_recent_ranked_pings(self, timestamp: float) -> str:
        """Gets a list with all the recent ranked pings.
        We need a different approach than unranked here because we also store the rank role here.
        This is its own function because we need to export it.
        """
        with open(r"./json/ranked.json", "r", encoding="utf-8") as f:
            user_pings = json.load(f)

        list_of_searches = []

        for ping in user_pings:
            ping_channel = user_pings[f"{ping}"]["channel"]
            ping_timestamp = user_pings[f"{ping}"]["time"]

            difference = timestamp - ping_timestamp

            minutes = round(difference / 60)

            if minutes < 31:
                list_of_searches.append(
                    f"<@!{ping}>, in <#{ping_channel}>, {minutes} minutes ago\n"
                )

        list_of_searches.reverse()

        return "".join(list_of_searches) or "Looks like no one has pinged recently :("

    @commands.hybrid_command(aliases=["rankedmm", "rankedmatchmaking", "rankedsingles"])
    @commands.cooldown(1, 120, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def ranked(self, ctx: commands.Context) -> None:
        """Used for 1v1 competitive ranked matchmaking."""
        timestamp = discord.utils.utcnow().timestamp()

        if ctx.message.channel.id in TGArenaChannelIDs.OPEN_RANKED_ARENAS:
            self.store_ranked_ping(ctx, timestamp)

            # Gets all of the other active pings.
            searches = self.get_recent_ranked_pings(timestamp)

            embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.blue(),
            )

            if ctx.interaction:
                await ctx.send("Processing request...", ephemeral=True)

            mm_message = await ctx.channel.send(
                f"{ctx.author.mention} is looking for ranked matchmaking games! <@&{TGMatchmakingRoleIDs.RANKED_ROLE}>",
                embed=embed,
            )
            mm_thread = await mm_message.create_thread(
                name=f"Ranked Arena of {ctx.author.name}", auto_archive_duration=60
            )
            await mm_thread.add_user(ctx.author)
            await mm_thread.send(
                f"Hi there, {ctx.author.mention}! "
                "Please use this thread for communicating with your opponent and for reporting matches."
            )

            # Waits 30 mins and deletes the ping afterwards.
            await asyncio.sleep(1800)

            self.delete_ranked_ping(ctx)

        elif ctx.message.channel.id in TGArenaChannelIDs.CLOSED_RANKED_ARENAS:
            searches = self.get_recent_ranked_pings(timestamp)

            embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.blue(),
            )

            if ctx.interaction:
                await ctx.send("Processing request...", ephemeral=True)

            mm_message = await ctx.channel.send(
                f"{ctx.author.mention} is looking for ranked matchmaking games! <@&{TGMatchmakingRoleIDs.RANKED_ROLE}>\n"
                "Here are the most recent pings in the open ranked arenas:",
                embed=embed,
            )
            mm_thread = await mm_message.create_thread(
                name=f"Ranked Arena of {ctx.author.name}", auto_archive_duration=60
            )
            await mm_thread.add_user(ctx.author)
            await mm_thread.send(
                f"Hi there, {ctx.author.mention}! "
                "Please use this thread for communicating with your opponent and for reporting matches."
            )

        else:
            await ctx.send(
                "Please only use this command in our ranked arena channels!",
                ephemeral=True,
            )
            ctx.command.reset_cooldown(ctx)

    @commands.hybrid_command(aliases=["reportgame"], cooldown_after_parsing=True)
    @commands.cooldown(1, 41, commands.BucketType.user)
    @commands.guild_only()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user you beat in the ranked match.")
    async def reportmatch(self, ctx: commands.Context, user: discord.Member) -> None:
        """The winner of the match uses this to report a ranked set.
        Updates the rating values and ranked roles of the players automatically.
        """

        if str(ctx.channel.type) == "public_thread":
            if (
                ctx.channel.parent_id not in TGArenaChannelIDs.OPEN_RANKED_ARENAS
                and ctx.channel.parent_id not in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
            ):
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas or the threads within."
                )
                ctx.command.reset_cooldown(ctx)
                return
        else:
            if (
                ctx.channel.id not in TGArenaChannelIDs.OPEN_RANKED_ARENAS
                and ctx.channel.id not in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
            ):
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas or the threads within."
                )
                ctx.command.reset_cooldown(ctx)
                return

        # To prevent any kind of abuse.
        if user.id == ctx.author.id:
            await ctx.send("Don't report matches with yourself please.")
            ctx.command.reset_cooldown(ctx)
            return

        if user.bot:
            await ctx.send("Are you trying to play a match with bots?")
            ctx.command.reset_cooldown(ctx)
            return

        def check(message: discord.Message) -> bool:
            return (
                message.content.lower() == "y"
                and message.author == user
                and message.channel == ctx.channel
            )

        await ctx.send(
            f"The winner of the match {ctx.author.mention} vs. {user.mention} is: {ctx.author.mention}! \n"
            f"{user.mention} do you agree with the results? **Type y to verify.**"
        )
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to respond! Please try reporting the match again."
            )
            return

        message = await self.save_match(ctx.author, user, ctx.guild)

        await ctx.send(message)

    @commands.hybrid_command(aliases=["forcereportgame"], cooldown_after_parsing=True)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        winner="The winner of the match.", loser="The loser of the match."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    @commands.cooldown(1, 41, commands.BucketType.user)
    async def forcereportmatch(
        self, ctx: commands.Context, winner: discord.Member, loser: discord.Member
    ) -> None:
        """Forcefully reports a match, in case someone abandons it or fails to report."""

        # This is much of the same as the reportmatch command.
        if ctx.guild.id != GuildIDs.TRAINING_GROUNDS:
            await ctx.send(
                f"This command is only available on the {GuildNames.TRAINING_GROUNDS} Server."
            )
            return

        def check(message: discord.Message) -> bool:
            return (
                message.content.lower() == "y"
                and message.author == ctx.author
                and message.channel == ctx.channel
            )

        await ctx.send(
            f"The winner of the match {winner.mention} vs. {loser.mention} is: {winner.mention}! \n"
            f"{ctx.author.mention}, is that result correct? **Type y to verify.**"
        )
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to respond! Please try reporting the match again."
            )
            return

        message = await self.save_match(winner, loser, ctx.guild)

        await ctx.send(message)

    @commands.hybrid_command(aliases=["startgame", "playmatch", "playgame"])
    @commands.cooldown(1, 61, commands.BucketType.user)
    @commands.guild_only()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to play against.")
    async def startmatch(self, ctx: commands.Context, member: discord.Member) -> None:
        """Walks you through a ranked match, includes stage bans and reporting the match.
        For a shortcut, use the reportmatch command."""
        # Since only threads have a parent_id, we need a special case for these to not throw any errors.
        if str(ctx.channel.type) == "public_thread":
            if (
                ctx.channel.parent_id not in TGArenaChannelIDs.OPEN_RANKED_ARENAS
                and ctx.channel.parent_id not in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
            ):
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas or the threads within."
                )
                ctx.command.reset_cooldown(ctx)
                return
        elif (
            ctx.channel.id not in TGArenaChannelIDs.OPEN_RANKED_ARENAS
            and ctx.channel.id not in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
        ):
            await ctx.send(
                "Please only use this command in the ranked matchmaking arenas or the threads within."
            )
            ctx.command.reset_cooldown(ctx)
            return

        # To prevent any kind of abuse.
        if member.id == ctx.author.id:
            await ctx.send("Don't report matches with yourself please.")
            ctx.command.reset_cooldown(ctx)
            return

        if member.bot:
            await ctx.send("Are you trying to play a match with bots?")
            ctx.command.reset_cooldown(ctx)
            return

        # Need to keep track of the score
        player_one_score = 0
        player_two_score = 0
        game_count = 0

        # We implement Dave's stupid rule, so we need to keep track of the stages played.
        player_one_dsr = []
        player_two_dsr = []

        best_of_view = BestOfButtons(ctx.author)
        await ctx.send(
            f"{ctx.author.mention}, do you want to play a Best of 3 or a Best of 5?",
            view=best_of_view,
        )

        await best_of_view.wait()

        if not best_of_view.choice:
            await ctx.send("You didn't choose a format in time!\nCancelling match.")
            return

        arena_view = ArenaButton(ctx.author, best_of_view.choice)

        await ctx.send(
            f"**Best of {best_of_view.choice}** selected.\n"
            "Please host an arena and share the Code/Password here. Click the button when you're ready.",
            view=arena_view,
        )

        timeout = await arena_view.wait()

        if timeout:
            await ctx.send("You didn't host an arena in time!\nCancelling match.")
            return

        # The first stage ban is special, so we cannot move this into the loop.
        stage_select = StarterStageButtons(ctx.author, member)

        await ctx.send(
            f"**Stage select**\n{ctx.author.mention}, please **ban 1 stage**:",
            view=stage_select,
        )

        await stage_select.wait()

        if not stage_select.choice:
            await ctx.send("No stage selected in time.\nCancelling match.")
            return

        game = PlayerButtons(ctx.author, member)

        await ctx.send(
            f"**{stage_select.choice}** selected.\nStart your match! Good luck!\n\n"
        )

        await ctx.send(
            "When you're done, click on the button of the winner of Game 1 to report the match.",
            view=game,
        )

        timeout = await game.wait()

        if timeout:
            await ctx.send("You didn't report the match in time!\nCancelling match.")
            return

        # Looping the rest of the stage bans until the game is over.
        game_over = False
        while not game_over:
            if game.cancelled:
                return

            # Incrementing counters, adding stages to the DSR list and assigning the correct view.
            game_count += 1
            if game.winner == ctx.author:
                player_one_score += 1
                player_two_dsr.append(stage_select.choice)
                stage_select = CounterpickStageButtons(
                    ctx.author,
                    member,
                    player_one_dsr,
                    2 if best_of_view.choice == 5 else 3,
                )
            elif game.winner == member:
                player_two_score += 1
                player_one_dsr.append(stage_select.choice)
                stage_select = CounterpickStageButtons(
                    member,
                    ctx.author,
                    player_two_dsr,
                    2 if best_of_view.choice == 5 else 3,
                )

            # Checking if the score threshold has been reached.
            if best_of_view.choice == 3 and (
                player_one_score >= 2 or player_two_score >= 2
            ):
                game_over = True
                break

            if best_of_view.choice == 5 and (
                player_one_score >= 3 or player_two_score >= 3
            ):
                game_over = True
                break

            # The winner of the previous set can ban three stages, then the loser can pick one (that he hasnt won on yet).
            await ctx.send(
                f"Game {game_count}/{best_of_view.choice} reported! {game.winner.mention} won! (Score: {player_one_score} - {player_two_score})\n"
                f"{game.winner.mention}, please ban {2 if best_of_view.choice == 5 else 3} stages:",
                view=stage_select,
            )

            await stage_select.wait()

            if not stage_select.choice:
                await ctx.send("No stage selected in time.\nCancelling match.")
                return

            next_game = PlayerButtons(ctx.author, member)

            # The players can now play the match, and the cycle repeats until a winner is found.
            await ctx.send(
                f"**{stage_select.choice}** selected.\nStart your match! Good luck!\n\n"
            )

            await ctx.send(
                f"When you're done, click on the button of the winner of Game {game_count} to report the match.",
                view=next_game,
            )

            timeout = await next_game.wait()

            if timeout:
                await ctx.send(
                    "You didn't report the match in time!\nCancelling match."
                )
                return

            game = next_game

        # When the game is over we report the match automatically and update the ratings etc.
        await ctx.send(
            f"The final score is: {player_one_score} - {player_two_score}! Reporting match automatically.."
        )

        if player_one_score > player_two_score:
            message = await self.save_match(ctx.author, member, ctx.guild)
        else:
            message = await self.save_match(member, ctx.author, ctx.guild)

        await ctx.send(message)

    @commands.hybrid_command(aliases=["rankedstats"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The user you want to see the ranked stats of.")
    async def rankstats(
        self, ctx: commands.Context, member: discord.User = None
    ) -> None:
        """Gets you the ranked stats of a member, or your own if you dont specify a member.
        If you get your own, you get a choice of removing/adding your ranked role.
        """
        if member is None:
            member = ctx.author

        rating, wins, losses, matches = await self.get_player(member)

        # Gets the last 5 games played and reverses that string.
        last5games = matches[-5:]
        gamelist = last5games[::-1]

        # Subs in the emojis.
        gamelist = gamelist.replace("W", Emojis.WIN_EMOJI)
        gamelist = gamelist.replace("L", Emojis.LOSE_EMOJI)

        ranked_role = await self.get_ranked_role(
            rating, self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
        )

        # We also go through the players matches to get their recent performance swings.
        async with aiosqlite.connect("./db/database.db") as db:
            recent_matches = await db.execute_fetchall(
                """SELECT * FROM matches WHERE winner_id = :user_id OR loser_id = :user_id ORDER BY timestamp DESC LIMIT 5""",
                {"user_id": member.id},
            )

            # If the recent matches are empty, we set the old rating to the current one.
            # Should never really happen, but who knows.
            if not recent_matches:
                old_mu = rating.mu
                old_sigma = rating.sigma
            # If there are matches we get the old rating from the last match.
            # We have to check if the user was the winner or loser to get the correct rating.
            # And then we get it from the last match in the list, 5 matches ago.
            elif recent_matches[-1][1] == member.id:
                old_mu = recent_matches[-1][4]
                old_sigma = recent_matches[-1][5]
            elif recent_matches[-1][2] == member.id:
                old_mu = recent_matches[-1][6]
                old_sigma = recent_matches[-1][7]

        recent_rating = self.get_display_rank(rating) - self.get_display_rank(
            trueskill.Rating(old_mu, old_sigma)
        )

        if recent_rating == 0:
            recent_rating = "±0"
        elif recent_rating > 0:
            recent_rating = f"+{recent_rating}"
        else:
            recent_rating = f"{recent_rating}"

        embed = discord.Embed(title=f"Ranked stats of {str(member)}", colour=0x3498DB)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="TabuuSkill", value=f"**{self.get_display_rank(rating)}**", inline=True
        )
        embed.add_field(name="Rank", value=ranked_role.name, inline=True)
        embed.add_field(name="Games Played", value=f"{wins + losses}")
        embed.add_field(name="Wins", value=wins, inline=True)
        embed.add_field(name="Losses", value=losses, inline=True)
        embed.add_field(
            name="Win Percentage", value=f"{round(wins/(wins+losses) * 100)}%"
        )
        embed.add_field(name="Last Matches", value=gamelist, inline=True)
        embed.add_field(name="Recent Performance", value=recent_rating, inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def leaderboard(self, ctx: commands.Context) -> None:
        """The Top 10 Players of our Ranked Matchmaking."""
        # This command could take a while to run, so we need to defer the slash version.
        # Typing does that in the slash version, and in the message version it displays the bot as typing in chat.
        await ctx.typing()

        async with aiosqlite.connect("./db/database.db") as db:
            top_10 = await db.execute_fetchall(
                """SELECT * FROM trueskill ORDER BY (rating - 3 * deviation) DESC LIMIT 10"""
            )

        embed = discord.Embed(
            title=f"Top 10 Players of {GuildNames.TRAINING_GROUNDS} Ranked Matchmaking",
            description="**Place - Player**\nRank **| TabuuSkill |** Wins / Losses (%)",
            colour=0x3498DB,
        )

        async with aiosqlite.connect("./db/database.db") as db:
            for r, u in enumerate(top_10, start=1):
                user_id, rating, deviation, wins, losses, _ = u

                # Getting the mains of the players, too.
                mains = await db.execute_fetchall(
                    """SELECT mains FROM profile WHERE user_id = :user_id""",
                    {"user_id": user_id},
                )
                # If they don't have any registered mains, we just display nothing.
                display_mains = f"{mains[0][0]}" if mains else ""

                # Trying to see if the user is in the cache, if not we have to fetch them.
                # This takes up the majority of the commands time.
                if not (user := self.bot.get_user(user_id)):
                    user = await self.bot.fetch_user(user_id)

                player = trueskill.Rating(rating, deviation)

                rank = await self.get_ranked_role(
                    player, self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                )

                embed.add_field(
                    name=f"#{r} - {str(user)} {display_mains}",
                    value=f"{rank.name} **| {self.get_display_rank(player)} |**"
                    f" {wins}/{losses} ({round(wins/(wins+losses) * 100)}%)",
                    inline=False,
                )

        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @tasks.loop(time=datetime.time(12, 0, 0))
    async def decay_ratings(self) -> None:
        """Decays the ratings of all inactive players every first of the month at 12:00 CET."""
        # Chose the first cause why not.
        if datetime.datetime.now().day != 1:
            return

        logger = self.bot.get_logger("bot.ranked")

        # This gets the timestamp of the first day of the last month at 12:00.
        # Timezones really dont matter too much here.
        first_last_month = datetime.datetime(
            datetime.datetime.now().year,
            (datetime.datetime.now().month - 1) % 12,
            1,
            12,
            0,
            0,
            0,
        ).timestamp()

        active_players = []

        logger.info("Starting to decay deviations for this month...")

        async with aiosqlite.connect("./db/database.db") as db:
            # First we go through the matches that were played in the last month and see who has competed in them.
            matches = await db.execute_fetchall(
                """SELECT winner_id, loser_id FROM matches WHERE timestamp > :first_last_month""",
                {"first_last_month": first_last_month},
            )

            for winner_id, loser_id in matches:
                if winner_id not in active_players:
                    active_players.append(winner_id)
                if loser_id not in active_players:
                    active_players.append(loser_id)

            all_players = await db.execute_fetchall(
                """SELECT user_id, rating, deviation FROM trueskill"""
            )

            for player in all_players:
                # If the player has not competed in a match in the last month, we decay their deviation.
                # Currently we decay it by just 1% every month.
                if player[0] not in active_players:
                    logger.info(f"Decaying rating of Player {player[0]}")

                    rating = trueskill.Rating(player[1], player[2])
                    decayed_rating = self.decay_deviation(rating)
                    await db.execute(
                        """UPDATE trueskill SET deviation = :new_deviation WHERE user_id = :user_id""",
                        {
                            "new_deviation": decayed_rating.sigma,
                            "user_id": player[0],
                        },
                    )

            await db.commit()

        logger.info("Finished decaying deviations for this month.")

    @decay_ratings.before_loop
    async def before_decay_ratings(self) -> None:
        await self.bot.wait_until_ready()

    @reportmatch.error
    async def reportmatch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                f"Please only use this command in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("Please mention the member that you beat in the match.")
        else:
            raise error

    @forcereportmatch.error
    async def forcereportmatch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send(
                "Please mention the 2 members that have played in this match. "
                "First mention the winner, second mention the loser."
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )
        else:
            raise error

    @rankstats.error
    async def rankstats_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("This user hasn't played a ranked match yet.")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                "I couldn't find this member, make sure you have the right one or just leave it blank."
            )
        else:
            raise error

    @ranked.error
    async def ranked_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        if (
            ctx.channel.id in TGArenaChannelIDs.OPEN_RANKED_ARENAS
            or ctx.channel.id in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
        ):
            timestamp = discord.utils.utcnow().timestamp()

            searches = self.get_recent_ranked_pings(timestamp)

            embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.blue(),
            )

            await ctx.send(
                f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \n"
                "In the meantime, here are the most recent ranked pings:",
                embed=embed,
            )
        else:
            await ctx.send(
                "Please only use this command in the ranked matchmaking arenas.",
                ephemeral=True,
            )

    @leaderboard.error
    async def leaderboard_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @startmatch.error
    async def startmatch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                f"Please only use this command in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.MemberNotFound)
        ):
            await ctx.send("Please mention the member that you beat in the match.")
        else:
            raise error


async def setup(bot) -> None:
    await bot.add_cog(Ranking(bot))
    print("Ranking cog loaded")
