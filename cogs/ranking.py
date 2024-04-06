import asyncio
import datetime
import random

import aiosqlite
import discord
import trueskill
from discord import app_commands
from discord.ext import commands, tasks

import utils.check
import utils.time
from utils.character import match_character
from utils.ids import (
    Emojis,
    GuildIDs,
    GuildNames,
    TGArenaChannelIDs,
    TGMatchmakingRoleIDs,
)
from utils.image import get_dominant_colour
from views.character_pick import CharacterView
from views.ranked import ArenaButton, BestOfButtons, PlayerButtons
from views.stageban import CounterpickStageButtons, StarterStageButtons


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

        # We multiply the rating by 100 and add 1000, compared to the original
        # Microsoft TrueSkill algorithm. So a rating of 5000 equals a rank of 40,
        # the ranks were used in Halo 3 where 50 was the highest rank.
        # A rating of 40 was also fairly hard to achieve
        # so this is the current max rank for us.
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
            # This rank should hopefully also be fairly hard to obtain,
            # if you do not lose every single match.
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
        # Checking if the user has the role before removing it.
        # Prevents unnecessary API calls which would slow us down.
        for role in roles:
            if role in member.roles:
                await member.remove_roles(role)

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
        # If the threshold is not met, we remove all ranked roles just in case.
        else:
            await self.remove_ranked_roles(member, guild)

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
            f"Match #{match_id} successfully reported!\n{winner.mention} won!\n\nUpdated ratings: \n"
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

    def get_potential(self, player: trueskill.Rating) -> float:
        """Gets the maximum rank of a player, scaled."""
        return max(round(((player.mu + 3 * player.sigma) * 100) + 1000), 0)

    def decay_deviation(self, player: trueskill.Rating) -> trueskill.Rating:
        """Decays the deviation of a player by 3.33%."""
        # 3.33% was chosen because a decently rated player (~25 games played) has a deviation of ~2.6,
        # with a 3.33% decay, the deviation will be at the maximum value after 36 decay steps.
        # We decay the deviation every month, so it will take 3 years.
        return trueskill.Rating(player.mu, min(player.sigma * (31 / 30), 25 / 3))

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
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
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

    @commands.hybrid_command(
        aliases=["startgame", "playmatch", "playgame"], cooldown_after_parsing=True
    )
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

        # The players pick their characters.
        # In Game 1, this is done before the stage bans.
        # After that, the players pick their characters after the stage bans.
        character_view = CharacterView(ctx.author, member, None)

        character_view.message = await ctx.send(
            f"{ctx.author.mention} and {member.mention}: Pick a character for Game 1!",
            view=character_view,
        )

        timeout = await character_view.wait()

        if timeout:
            await ctx.send(
                "A player did not select their character in time.\nCancelling match."
            )
            return

        await ctx.send(
            f"{ctx.author.mention} has chosen {character_view.player_one_choice}. ({match_character(character_view.player_one_choice)[0]})\n"
            f"{member.mention} has chosen {character_view.player_two_choice}. ({match_character(character_view.player_two_choice)[0]})"
        )

        last_choice_author = [
            character_view.player_one_choice,
            match_character(character_view.player_one_choice)[0],
        ]
        last_choice_member = [
            character_view.player_two_choice,
            match_character(character_view.player_two_choice)[0],
        ]

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

        game = PlayerButtons(ctx.author, member, game_count + 1)

        game_message = (
            f"**Game {game_count + 1}/{best_of_view.choice} - {stage_select.choice}**\n"
            f"{ctx.author.mention} "
            f"({character_view.player_one_choice} {match_character(character_view.player_one_choice)[0]}) "
            f"**{player_one_score}** - **{player_two_score}** "
            f"{member.mention} "
            f"({character_view.player_two_choice} {match_character(character_view.player_two_choice)[0]})\n\n"
            "Please start your match! Good luck, Have fun!\n\n"
            f"When you're done, click on the button of the winner of Game {game_count + 1} to report the match."
        )

        await ctx.send(game_message, view=game)

        timeout = await game.wait()

        if timeout:
            await ctx.send("You didn't report the match in time!\nCancelling match.")
            return

        # Looping the rest of the stage bans until the game is over.
        game_over = False
        while not game_over:
            if game.cancelled:
                return

            # Incrementing counters, adding stages to the DSR list and assigning the correct views.
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
                character_view = CharacterView(
                    ctx.author,
                    member,
                    ctx.author,
                    last_choice_author,
                    last_choice_member,
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
                character_view = CharacterView(
                    ctx.author, member, member, last_choice_author, last_choice_member
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
                f"Game {game_count}/{best_of_view.choice} reported! {game.winner.mention} won! "
                f"(Score: **{player_one_score} - {player_two_score})**\n"
                f"{game.winner.mention}, please ban {2 if best_of_view.choice == 5 else 3} stages:",
                view=stage_select,
            )

            await stage_select.wait()

            if not stage_select.choice:
                await ctx.send("No stage selected in time.\nCancelling match.")
                return

            next_game = PlayerButtons(ctx.author, member, game_count + 1)

            # Then the two players pick their characters.
            # First the winner and then the loser.
            character_view.message = await ctx.send(
                f"{game.winner.mention}, please pick a character for the next Game!",
                view=character_view,
            )

            timeout = await character_view.wait()

            if timeout:
                await ctx.send(
                    "A player did not select their character in time.\nCancelling match."
                )
                return

            last_choice_author = [
                character_view.player_one_choice,
                match_character(character_view.player_one_choice)[0],
            ]
            last_choice_member = [
                character_view.player_two_choice,
                match_character(character_view.player_two_choice)[0],
            ]

            game_message = (
                f"**Game {game_count + 1}/{best_of_view.choice} - {stage_select.choice}**\n"
                f"{ctx.author.mention} "
                f"({character_view.player_one_choice} {match_character(character_view.player_one_choice)[0]}) "
                f"**{player_one_score}** - **{player_two_score}** "
                f"{member.mention} "
                f"({character_view.player_two_choice} {match_character(character_view.player_two_choice)[0]})\n\n"
                "Please start your match! Good luck, Have fun!\n\n"
                f"When you're done, click on the button of the winner of Game {game_count + 1} to report the match."
            )

            # And finally the match starts.
            # The cycle repeats until the game is over.
            await ctx.send(game_message, view=next_game)

            timeout = await next_game.wait()

            if timeout:
                await ctx.send(
                    "You didn't report the match in time!\nCancelling match."
                )
                return

            game = next_game

        # When the game is over we report the match automatically and update the ratings etc.
        await ctx.send(
            f"Game {game_count}/{best_of_view.choice} reported! {game.winner.mention} won!\n"
            "The final result of the match is: "
            f"{ctx.author.mention} **{player_one_score} - {player_two_score}** {member.mention}!"
            "\nReporting match automatically.."
        )

        if player_one_score > player_two_score:
            message = await self.save_match(ctx.author, member, ctx.guild)
        else:
            message = await self.save_match(member, ctx.author, ctx.guild)

        await ctx.send(message)

    @commands.hybrid_command(aliases=["rankstats"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The user you want to see the ranked stats of.")
    async def rankedstats(
        self, ctx: commands.Context, member: discord.User = None
    ) -> None:
        """Gets you the ranked stats of a member, or your own if you dont specify a member.
        If you get your own, you get a choice of removing/adding your ranked role.
        """
        await ctx.typing()

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

        colour = await get_dominant_colour(member.display_avatar)

        # We also go through the players matches to get their recent performance swings.
        async with aiosqlite.connect("./db/database.db") as db:
            recent_matches = await db.execute_fetchall(
                """SELECT * FROM matches WHERE winner_id = :user_id OR loser_id = :user_id ORDER BY timestamp DESC LIMIT 5""",
                {"user_id": member.id},
            )

            complete_leaderboard = await db.execute_fetchall(
                """SELECT row_number() OVER (ORDER BY (rating - 3 * deviation) DESC) as row_num, user_id FROM trueskill WHERE wins + losses > 4"""
            )

            best_win = await db.execute_fetchall(
                """SELECT * FROM matches WHERE winner_id = :user_id ORDER BY (old_loser_rating - 3 * old_loser_deviation) DESC LIMIT 1""",
                {"user_id": member.id},
            )

            average_opponents = await db.execute_fetchall(
                """
                SELECT
                    CASE WHEN winner_id = :user_id THEN
                        old_loser_rating
                    ELSE
                        old_winner_rating
                    END rating,
                    CASE WHEN winner_id = :user_id THEN
                        old_loser_deviation
                    ELSE
                        old_winner_deviation
                    END deviation
                FROM matches
                WHERE winner_id = :user_id OR loser_id = :user_id
                """,
                {"user_id": member.id},
            )

            # This sql statement basically fetches either the highest rating after a win, after a loss, or before a loss,
            # together with a timestamp. You can gain rating by losing, but you cannot lose rating by winning.
            highest_rating = await db.execute_fetchall(
                """
                SELECT
                    CASE WHEN winner_id = :user_id THEN
                        new_winner_rating
                    ELSE
                        CASE WHEN new_loser_rating - 3 * new_loser_deviation < old_loser_rating - 3 * old_loser_deviation THEN
                            old_loser_rating
                        ELSE
                            new_loser_rating
                        END
                    END rating,
                    CASE WHEN winner_id = :user_id THEN
                        new_winner_deviation
                    ELSE
                        CASE WHEN new_loser_rating - 3 * new_loser_deviation < old_loser_rating - 3 * old_loser_deviation THEN
                            old_loser_deviation
                        ELSE
                            new_loser_deviation
                        END
                    END deviation,
                    timestamp
                FROM matches
                WHERE winner_id = :user_id OR loser_id = :user_id
                ORDER BY rating - 3 * deviation
                DESC LIMIT 1""",
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

        if not best_win:
            highest_win = "*N/A*"
        else:
            user = self.bot.get_user(best_win[0][2])
            if not user:
                try:
                    user = await self.bot.fetch_user(best_win[0][2])
                except discord.NotFound:
                    user = "Unknown User"
            highest_win = (
                f"vs. **{str(user)}**\n"
                f"***({self.get_display_rank(trueskill.Rating(best_win[0][6], best_win[0][7]))}**, "
                f"<t:{best_win[0][3]}:d>)*"
            )

        if not average_opponents:
            average_opponent = "*N/A*"
        else:
            average_ratings = [
                self.get_display_rank(trueskill.Rating(opponent[0], opponent[1]))
                for opponent in average_opponents
            ]
            average_opponent = (
                f"**≈{round(sum(average_ratings) / len(average_ratings))}**"
            )

        recent_rating = self.get_display_rank(rating) - self.get_display_rank(
            trueskill.Rating(old_mu, old_sigma)
        )

        if recent_rating == 0:
            recent_rating = "±0"
        elif recent_rating > 0:
            recent_rating = f"+{recent_rating}"
        else:
            # If it's negative, the minus sign is already there.
            recent_rating = f"{recent_rating}"

        all_time_win = (
            # We do not really need the min here, it's just a kind of failsafe.
            max(
                self.get_display_rank(
                    trueskill.Rating(highest_rating[0][0], highest_rating[0][1])
                ),
                self.get_display_rank(rating),
            )
            if highest_rating
            else self.get_display_rank(rating)
        )

        # Getting the longest and current win and lose streaks.
        longest_winstreak = 0
        current_winstreak = 0
        longest_losestreak = 0
        current_losestreak = 0
        for m in matches:
            if m == "W":
                current_winstreak += 1
                current_losestreak = 0
            else:
                current_losestreak += 1
                current_winstreak = 0

            longest_winstreak = max(longest_winstreak, current_winstreak)
            longest_losestreak = max(longest_losestreak, current_losestreak)

        # We basically check double here, because we want the current time stamp
        # if the player still has the highest rating that they ever achieved.
        timestamp_win = (
            round(discord.utils.utcnow().timestamp())
            if self.get_display_rank(rating) == all_time_win
            else highest_rating[0][2]
        )

        embed = discord.Embed(title=f"Ranked stats of {str(member)}", colour=colour)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="TabuuSkill", value=f"**{self.get_display_rank(rating)}**", inline=True
        )
        embed.add_field(
            name="Deviation", value=f"**{round(rating.sigma * 100, 2)}?**", inline=True
        )
        embed.add_field(
            name="All-Time High",
            value=f"**{all_time_win}** *(<t:{timestamp_win}:d>)*",
            inline=True,
        )

        if wins + losses >= 5:
            if ctx.guild and ranked_role.guild.id == ctx.guild.id:
                embed.add_field(name="Rank", value=ranked_role.mention, inline=True)
            else:
                embed.add_field(
                    name="Rank", value=f"**{ranked_role.name}**", inline=True
                )
        else:
            embed.add_field(name="Rank", value="*Unranked*", inline=True)

        # This will only yield the top half of the leaderboard.
        leaderboard_top = complete_leaderboard[: len(complete_leaderboard) // 2]

        if any((pos := i) and member.id == m for (i, m) in leaderboard_top):
            if pos <= 5:  # noqa: F821
                index = pos - 1  # noqa: F821
            elif pos <= 10:  # noqa: F821
                index = 5
            elif pos <= 15:  # noqa: F821
                index = 6
            elif pos <= 20:  # noqa: F821
                index = 7
            # The last index is an empty string.
            else:
                index = 8

            percent = min(
                max(
                    round(
                        ((pos - 1) / len(complete_leaderboard)) * 100, 2  # noqa: F821
                    ),
                    0.01,
                ),
                100,
            )

            embed.add_field(
                name="Leaderboard",
                value=f"{Emojis.LEADERBOARD_EMOJIS[index]} **#{pos}** *(Top {percent}%)*",  # noqa: F821
                inline=True,
            )
        else:
            embed.add_field(name="Leaderboard", value="*N/A*", inline=True)

        embed.add_field(name="Matches Played", value=f"**{wins + losses}**")
        embed.add_field(name="Wins", value=f"**{wins}**", inline=True)
        embed.add_field(name="Losses", value=f"**{losses}**", inline=True)
        embed.add_field(
            name="Win Percentage", value=f"**{round(wins/(wins+losses) * 100)}%**"
        )
        embed.add_field(name="Last Matches", value=f"**{gamelist}**", inline=True)
        embed.add_field(
            name="Longest Winning Streak",
            value=f"**{longest_winstreak}** *(Current: {current_winstreak})*",
            inline=True,
        )
        embed.add_field(
            name="Longest Losing Streak",
            value=f"**{longest_losestreak}** *(Current: {current_losestreak})*",
            inline=True,
        )
        embed.add_field(
            name="Recent Performance", value=f"**{recent_rating}**", inline=True
        )
        embed.add_field(name="Average Opponent", value=average_opponent, inline=True)
        embed.add_field(name="Highest Win", value=highest_win, inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def leaderboard(self, ctx: commands.Context) -> None:
        """The Top 10 Players of our Ranked Matchmaking."""
        # This command could take a while to run, so we need to defer the slash version.
        # Typing does that in the slash version, and in the message version it displays the bot as typing in chat.
        await ctx.typing()

        async with aiosqlite.connect("./db/database.db") as db:
            top_10 = await db.execute_fetchall(
                """SELECT * FROM trueskill WHERE wins + losses > 4 ORDER BY (rating - 3 * deviation) DESC LIMIT 10"""
            )

        embed = discord.Embed(
            title=f"Top 10 Players of {GuildNames.TRAINING_GROUNDS} Ranked Matchmaking",
            description="**Place - Player**\nRank **| TabuuSkill |** Wins / Losses (%)",
            colour=0x3498DB,
        )

        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

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

                rank = await self.get_ranked_role(player, guild)

                embed.add_field(
                    name=f"#{r} - {str(user)} {display_mains}",
                    value=f"{rank.name} **| {self.get_display_rank(player)} |**"
                    f" {wins}/{losses} ({round(wins/(wins+losses) * 100)}%)",
                    inline=False,
                )

        embed.set_thumbnail(url=guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.describe(
        start="The start of the season in the format of a unix timestamp.",
        end="The end of the season in the format of a unix timestamp.",
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def seasonleaderboard(
        self, ctx: commands.Context, start: int, end: int
    ) -> None:
        """Shows you the Ranked Matchmaking Leaderboard only counting matches between two Unix timestamps.
        Note that the ratings displayed will not be affected by rating decay.
        So you might end up seeing a different leaderboard than the one in the leaderboard command.
        """
        await ctx.typing()

        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        async with aiosqlite.connect("./db/database.db") as db:
            season_matches = await db.execute_fetchall(
                """SELECT * FROM matches WHERE timestamp BETWEEN :start AND :end""",
                {"start": start, "end": end},
            )

        # Re-calculating the matches, with every player starting at the default rating.

        all_players = []

        for match in season_matches:
            (_, winner_id, loser_id, _, _, _, _, _, _, _, _, _) = match

            # We need to check if the player is already in the list, if not we add them.
            if winner_id not in [p["user_id"] for p in all_players]:
                all_players.append(
                    {
                        "user_id": winner_id,
                        "wins": 0,
                        "losses": 0,
                        "rating": trueskill.Rating(),
                    }
                )
            if loser_id not in [p["user_id"] for p in all_players]:
                all_players.append(
                    {
                        "user_id": loser_id,
                        "wins": 0,
                        "losses": 0,
                        "rating": trueskill.Rating(),
                    }
                )

            # Then we get both players from the list.

            winner = [p for p in all_players if p["user_id"] == winner_id][0]
            loser = [p for p in all_players if p["user_id"] == loser_id][0]

            # And update their ratings.

            (new_winner, new_loser) = trueskill.rate_1vs1(
                winner["rating"], loser["rating"]
            )

            winner["rating"] = new_winner
            loser["rating"] = new_loser

            # And finally we update their wins and losses.

            winner["wins"] += 1
            loser["losses"] += 1

        # Now we get rid of the players that did not play at least 5 matches.
        all_players = [p for p in all_players if p["wins"] + p["losses"] > 4]

        # Now we sort the list by their display rank.
        all_players.sort(key=lambda p: self.get_display_rank(p["rating"]), reverse=True)

        top_10 = all_players[:10]

        embed = discord.Embed(
            title=f"Top 10 Players of {GuildNames.TRAINING_GROUNDS} Ranked Matchmaking from <t:{start}:d> to <t:{end}:d>",
            description="**Place - Player**\nRank **| TabuuSkill |** Wins / Losses (%)",
            colour=0x3498DB,
        )

        async with aiosqlite.connect("./db/database.db") as db:
            for r, u in enumerate(top_10, start=1):
                user_id = u["user_id"]
                player = u["rating"]
                wins = u["wins"]
                losses = u["losses"]

                mains = await db.execute_fetchall(
                    """SELECT mains FROM profile WHERE user_id = :user_id""",
                    {"user_id": user_id},
                )

                display_mains = f"{mains[0][0]}" if mains else ""

                if not (user := self.bot.get_user(user_id)):
                    user = await self.bot.fetch_user(user_id)

                rank = await self.get_ranked_role(player, guild)

                embed.add_field(
                    name=f"#{r} - {str(user)} {display_mains}",
                    value=f"{rank.name} **| {self.get_display_rank(player)} |**"
                    f" {wins}/{losses} ({round(wins/(wins+losses) * 100)}%)",
                    inline=False,
                )

        embed.set_thumbnail(url=guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def recentmatches(self, ctx: commands.Context) -> None:
        """Gets you the last 20 matches played in Ranked Matchmaking."""
        await ctx.typing()

        async with aiosqlite.connect("./db/database.db") as db:
            recent_matches = await db.execute_fetchall(
                """SELECT * FROM matches ORDER BY timestamp DESC LIMIT 20"""
            )

        embed = discord.Embed(
            title=f"Last 20 Matches of {GuildNames.TRAINING_GROUNDS} Ranked Matchmaking",
            description="**Match ID - Timestamp**\n**Winner**: Before → After\n**Loser**: Before → After",
            colour=0x3498DB,
        )

        for match in recent_matches:
            (
                match_id,
                winner_id,
                loser_id,
                timestamp,
                old_winner_mu,
                old_winner_sigma,
                old_loser_mu,
                old_loser_sigma,
                new_winner_mu,
                new_winner_sigma,
                new_loser_mu,
                new_loser_sigma,
            ) = match

            winner = self.bot.get_user(winner_id)
            loser = self.bot.get_user(loser_id)

            if not winner:
                winner = await self.bot.fetch_user(winner_id)
            if not loser:
                loser = await self.bot.fetch_user(loser_id)

            embed.add_field(
                name=f"#{match_id} - <t:{timestamp}:F>",
                value=f"**{str(winner)}**: {self.get_display_rank(trueskill.Rating(old_winner_mu, old_winner_sigma))}"
                f" → {self.get_display_rank(trueskill.Rating(new_winner_mu, new_winner_sigma))}\n"
                f"**{str(loser)}**: {self.get_display_rank(trueskill.Rating(old_loser_mu, old_loser_sigma))}"
                f" → {self.get_display_rank(trueskill.Rating(new_loser_mu, new_loser_sigma))}",
                inline=False,
            )

        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def matchhistory(self, ctx: commands.Context, user: discord.User) -> None:
        """Gets you the last 10 matches of a player."""
        await ctx.typing()

        async with aiosqlite.connect("./db/database.db") as db:
            recent_matches = await db.execute_fetchall(
                """SELECT * FROM matches WHERE winner_id = :user_id OR loser_id = :user_id ORDER BY timestamp DESC LIMIT 10""",
                {"user_id": user.id},
            )

        embed = discord.Embed(
            title=f"Last 10 Matches of {str(user)}",
            description="**Match ID - Timestamp**\n**Winner**: Before → After\n**Loser**: Before → After",
            colour=0x3498DB,
        )

        for match in recent_matches:
            (
                match_id,
                winner_id,
                loser_id,
                timestamp,
                old_winner_mu,
                old_winner_sigma,
                old_loser_mu,
                old_loser_sigma,
                new_winner_mu,
                new_winner_sigma,
                new_loser_mu,
                new_loser_sigma,
            ) = match

            winner = self.bot.get_user(winner_id)
            loser = self.bot.get_user(loser_id)

            if not winner:
                winner = await self.bot.fetch_user(winner_id)
            if not loser:
                loser = await self.bot.fetch_user(loser_id)

            embed.add_field(
                name=f"#{match_id} - <t:{timestamp}:F>",
                value=f"**{str(winner)}**: {self.get_display_rank(trueskill.Rating(old_winner_mu, old_winner_sigma))}"
                f" → {self.get_display_rank(trueskill.Rating(new_winner_mu, new_winner_sigma))}\n"
                f"**{str(loser)}**: {self.get_display_rank(trueskill.Rating(old_loser_mu, old_loser_sigma))}"
                f" → {self.get_display_rank(trueskill.Rating(new_loser_mu, new_loser_sigma))}",
                inline=False,
            )

        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def deletematch(self, ctx: commands.Context, match_id: int) -> None:
        """Deletes a match from the database and restores the previous ratings."""
        await ctx.typing()

        def check(m: discord.Message) -> bool:
            return (
                m.content.lower() in ("y", "n")
                and m.author == ctx.author
                and m.channel == ctx.channel
            )

        async with aiosqlite.connect("./db/database.db") as db:
            match = await db.execute_fetchall(
                """SELECT * FROM matches WHERE match_id = :match_id""",
                {"match_id": match_id},
            )

            if not match:
                await ctx.send("Invalid Match ID! Please try again.")
                return

            winner = match[0][1]
            loser = match[0][2]
            timestamp = match[0][3]

            new_match = await db.execute_fetchall(
                """SELECT * FROM matches WHERE timestamp > :timestamp AND
                 (winner_id = :winner_id OR loser_id = :loser_id OR winner_id = :loser_id OR loser_id = :winner_id)""",
                {"timestamp": timestamp, "winner_id": winner, "loser_id": loser},
            )

            if new_match:
                await ctx.send(
                    "Could not delete match as one or both users played another match after this one."
                )
                return

            winner_user = self.bot.get_user(winner)
            loser_user = self.bot.get_user(loser)

            if not winner_user:
                winner_user = await self.bot.fetch_user(winner)
            if not loser_user:
                loser_user = await self.bot.fetch_user(loser)

            embed = discord.Embed(
                title=f"Match #{match_id}: {str(winner_user)} vs {str(loser_user)}",
                description=f"**Winner: {str(winner_user)}\n\nRatings Before → After**\n\n"
                f"**{str(winner_user)}**: {self.get_display_rank(trueskill.Rating(match[0][4], match[0][5]))}"
                f" → {self.get_display_rank(trueskill.Rating(match[0][8], match[0][9]))}"
                f"\n**{str(loser_user)}**: {self.get_display_rank(trueskill.Rating(match[0][6], match[0][7]))}"
                f" → {self.get_display_rank(trueskill.Rating(match[0][10], match[0][11]))}",
                colour=0x3498DB,
            )
            embed.set_thumbnail(url=ctx.guild.icon.url)

            await ctx.send(
                "Are you sure you want to delete this match and restore the previous ratings?\n"
                "**Type y to verify** or **Type n to cancel**.",
                embed=embed,
            )

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(
                    f"Delete request for Match {match_id} timed out! Please try again."
                )
                return

            if msg.content.lower() == "y":
                await db.execute(
                    """DELETE FROM matches WHERE match_id = :match_id""",
                    {"match_id": match_id},
                )
                await db.execute(
                    """UPDATE trueskill SET rating = :rating, deviation = :deviation, wins = wins - 1,
                     matches = SUBSTR(matches, 1, LENGTH(matches)-1) WHERE user_id = :user_id""",
                    {
                        "rating": match[0][4],
                        "deviation": match[0][5],
                        "user_id": winner,
                    },
                )
                await db.execute(
                    """UPDATE trueskill SET rating = :rating, deviation = :deviation, losses = losses - 1,
                     matches = SUBSTR(matches, 1, LENGTH(matches)-1) WHERE user_id = :user_id""",
                    {
                        "rating": match[0][6],
                        "deviation": match[0][7],
                        "user_id": loser,
                    },
                )
                await db.commit()

                # Updating the roles, if the member is still on the server.
                try:
                    winner_member = await ctx.guild.fetch_member(winner)
                    await self.update_ranked_role(winner_member, ctx.guild)
                except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                    pass

                try:
                    loser_member = await ctx.guild.fetch_member(loser)
                    await self.update_ranked_role(loser_member, ctx.guild)
                except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                    pass

                await ctx.send(
                    f"Match #{match_id} deleted successfully! Ratings were restored."
                )
            else:
                await ctx.send(f"Delete request for {match_id} cancelled.")
                return

    @tasks.loop(time=datetime.time(12, 0, 0))
    async def decay_ratings(self) -> None:
        """Decays the ratings of all inactive players every first of the month at 12:00 CET."""
        # Chose the first cause why not.
        if datetime.datetime.now().day != 1:
            return

        logger = self.bot.get_logger("bot.ranked")

        # This gets the timestamp of the first day of the last month at 12:00.
        # Timezones really dont matter too much here.
        first_last_month = (
            datetime.datetime(
                datetime.datetime.now().year,
                (datetime.datetime.now().month - 1),
                1,
                12,
                0,
                0,
                0,
            ).timestamp()
            if datetime.datetime.now().month != 1
            else datetime.datetime(
                (datetime.datetime.now().year - 1),
                12,
                1,
                12,
                0,
                0,
                0,
            ).timestamp()
        )

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

    @forcereportmatch.error
    async def forcereportmatch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )

    @rankedstats.error
    async def rankedstats_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("This user hasn't played a ranked match yet.")

    @deletematch.error
    async def deletematch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid match ID.")

    @startmatch.error
    async def startmatch_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )

    @seasonleaderboard.error
    async def seasonleaderboard_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid start and end Unix Timestamp.")


async def setup(bot) -> None:
    await bot.add_cog(Ranking(bot))
    print("Ranking cog loaded")
