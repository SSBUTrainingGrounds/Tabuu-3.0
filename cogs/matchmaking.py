import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

import utils.check
from utils.ids import GuildIDs, TGArenaChannelIDs, TGMatchmakingRoleIDs


class Pings(discord.ui.Select):
    """Handles the Pings for the recentpings command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.mins = round(bot.matchmaking_ping_time / 60)

        options = [
            discord.SelectOption(
                label="Singles",
                description=f"Singles Pings in the last {self.mins} Minutes",
                emoji="🗡️",
            ),
            discord.SelectOption(
                label="Doubles",
                description=f"Doubles Pings in the last {self.mins} Minutes",
                emoji="⚔️",
            ),
            discord.SelectOption(
                label="Funnies",
                description=f"Funnies Pings in the last {self.mins} Minutes",
                emoji="😂",
            ),
            discord.SelectOption(
                label="Ranked",
                description=f"Ranked Pings in the last {self.mins} Minutes",
                emoji="🏆",
            ),
        ]

        super().__init__(
            placeholder="Which pings do you want to see?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.values[0] not in ["Singles", "Doubles", "Funnies", "Ranked"]:
            await interaction.response.send_message(
                "Something went wrong! Please try again.", ephemeral=True
            )
            return

        timestamp = discord.utils.utcnow().timestamp()

        searches = Matchmaking.get_recent_pings(self, self.values[0].lower(), timestamp)
        colour = Matchmaking.get_embed_colour(self, self.values[0].lower())

        embed = discord.Embed(
            title=f"{self.values[0]} Pings in the last {self.mins} Minutes:",
            description=searches,
            colour=colour,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class DropdownPings(discord.ui.View):
    """Adds the items to the Dropdown menu."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.add_item(Pings(bot))


class Matchmaking(commands.Cog):
    """Contains the Unranked portion of our matchmaking system."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # Clears the Matchmaking Pings on Startup.
        self.clear_mmrequests()

        self.archive_threads.start()

    def cog_unload(self) -> None:
        self.archive_threads.cancel()

    def get_embed_colour(self, mm_type: str) -> Optional[discord.Colour]:
        """Returns the colour of the Matchmaking Type."""

        if mm_type == "singles":
            return discord.Colour.dark_red()
        elif mm_type == "doubles":
            return discord.Colour.dark_blue()
        elif mm_type == "funnies":
            return discord.Colour.green()
        elif mm_type == "ranked":
            return discord.Colour.blue()
        else:
            return None

    def get_matchmaking_role(
        self, guild: discord.Guild, mm_type: str
    ) -> Optional[discord.Role]:
        """Returns the role of the Matchmaking Type."""

        if mm_type == "singles":
            return guild.get_role(TGMatchmakingRoleIDs.SINGLES_ROLE)
        elif mm_type == "doubles":
            return guild.get_role(TGMatchmakingRoleIDs.DOUBLES_ROLE)
        elif mm_type == "funnies":
            return guild.get_role(TGMatchmakingRoleIDs.FUNNIES_ROLE)
        elif mm_type == "ranked":
            return guild.get_role(TGMatchmakingRoleIDs.RANKED_ROLE)
        else:
            return None

    def get_recent_pings(self, mm_type: str, timestamp: float) -> str:
        """Gets a list with every Ping saved, as long it is not older than the cutoff time."""

        user_pings = self.bot.matchmaking_pings[mm_type]

        list_of_searches = []

        for ping in user_pings:
            ping_timestamp = user_pings[f"{ping}"]["time"]
            difference = timestamp - ping_timestamp

            if difference < self.bot.matchmaking_ping_time:
                ping_channel = user_pings[f"{ping}"]["channel"]
                list_of_searches.append(
                    f"- <@!{ping}>, in <#{ping_channel}>, <t:{round(ping_timestamp)}:R>\n"
                )

        list_of_searches.reverse()

        return "".join(list_of_searches) or "Looks like no one has pinged recently :("

    def store_ping(self, ctx: commands.Context, mm_type: str, timestamp: float) -> None:
        """Saves a Matchmaking Ping of any type in the according dict."""

        self.bot.matchmaking_pings[mm_type][str(ctx.author.id)] = {
            "time": timestamp,
            "channel": ctx.channel.id,
        }

    def delete_ping(self, ctx: commands.Context, mm_type: str) -> None:
        """Deletes a specific Matchmaking Ping of any type from the according dict."""

        try:
            del self.bot.matchmaking_pings[mm_type][str(ctx.author.id)]
        except KeyError:
            logger = self.bot.get_logger("bot.mm")
            logger.warning(
                f"Tried to delete a {mm_type} ping by {str(ctx.author)} but the ping was already deleted."
            )

    def clear_mmrequests(self) -> None:
        """Clears every Matchmaking Ping in the Singles, Doubles, Funnies and Ranked dicts."""
        logger = self.bot.get_logger("bot.mm")

        self.bot.matchmaking_pings = {
            "singles": {},
            "doubles": {},
            "funnies": {},
            "ranked": {},
        }

        logger.info("Successfully deleted all matchmaking pings!")

    async def handle_request(
        self,
        ctx: commands.Context,
        mm_type: str,
        *,
        timeout: Optional[float] = None,
        message: Optional[str] = None,
    ) -> None:
        """Handles the matchmaking request."""
        # First we find out if the message is sent in a public, or private arena channel, or neither.
        open_channel = False
        private_channel = False
        if (
            mm_type == "ranked"
            and ctx.channel.id in TGArenaChannelIDs.OPEN_RANKED_ARENAS
        ) or (
            mm_type != "ranked" and ctx.channel.id in TGArenaChannelIDs.PUBLIC_ARENAS
        ):
            open_channel = True
        elif (
            mm_type == "ranked"
            and ctx.channel.id in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
        ) or (
            mm_type != "ranked" and ctx.channel.id in TGArenaChannelIDs.PRIVATE_ARENAS
        ):
            private_channel = True

        wrong_channel_message = (
            "Please only use this command in our ranked arena channels!"
            if mm_type == "ranked"
            else "Please only use this command in our arena channels!"
        )

        if mm_type == "ranked":
            thread_message = (
                f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent."
                f"\nOnce you found an opponent, start your ranked set by using `{self.bot.main_prefix}startmatch @Your Opponent`."
                "\nGood luck, have fun!"
            )
        elif mm_type == "doubles":
            thread_message = f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponents."
        else:
            thread_message = f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent."

        # If the message is sent in neither public nor private arena channel, we send an error message and return.
        if not open_channel and not private_channel:
            await ctx.send(wrong_channel_message, ephemeral=True)
            if not timeout:
                ctx.command.reset_cooldown(ctx)
            return

        timestamp = discord.utils.utcnow().timestamp()
        colour = self.get_embed_colour(mm_type)
        role = self.get_matchmaking_role(ctx.guild, mm_type)

        ping_message = f"{ctx.author.mention} is looking for {role.mention} games!"
        if message:
            ping_message += f" `{discord.utils.remove_markdown(message)}`"
        if private_channel:
            ping_message += f"\nHere are the most recent {mm_type.capitalize()} pings in our open arenas:"

        embed = discord.Embed(
            title=f"{mm_type.capitalize()} Pings in the last {round(self.bot.matchmaking_ping_time / 60)} Minutes:",
            colour=colour,
        )

        # Role mentions dont ping in an interaction response, so if the user uses the slash command version of the matchmaking commands,
        # we first need to acknowledge the interaction in some way and then send a followup message into the channel.
        if ctx.interaction:
            await ctx.send("Processing request...", ephemeral=True)

        if open_channel and not timeout:
            self.store_ping(ctx, mm_type, timestamp)

        searches = self.get_recent_pings(mm_type, timestamp)
        embed.description = searches

        # If you are on timeout, we still send an embed with the most recent pings in the open arenas.
        if timeout:
            await ctx.send(
                f"{ctx.author.mention}, you are on cooldown for another {round((timeout)/60)} minutes to use this command. \n"
                f"In the meantime, here are the most recent {mm_type.capitalize()} pings in our open arenas:",
                embed=embed,
            )
            return

        mm_message = await ctx.channel.send(
            ping_message,
            embed=embed,
        )
        mm_thread = await mm_message.create_thread(
            name=f"{mm_type.capitalize()} Arena of {ctx.author.name}",
            auto_archive_duration=60,
        )

        await mm_thread.add_user(ctx.author)
        await mm_thread.send(thread_message)

        if open_channel:
            await asyncio.sleep(self.bot.matchmaking_ping_time)
            self.delete_ping(ctx, mm_type)

    @commands.Cog.listener()
    async def on_thread_update(
        self, before: discord.Thread, after: discord.Thread
    ) -> None:
        """If a matchmaking thread is archived, we delete it. This is separate from the archive_threads task,
        because if a thread is archived manually, we want to delete it as well."""
        if (
            before.archived is False
            and after.archived is True
            and (
                after.parent_id in TGArenaChannelIDs.PUBLIC_ARENAS
                or after.parent_id in TGArenaChannelIDs.PRIVATE_ARENAS
                or after.parent_id in TGArenaChannelIDs.OPEN_RANKED_ARENAS
                or after.parent_id in TGArenaChannelIDs.CLOSED_RANKED_ARENAS
            )
        ):
            logger = self.bot.get_logger("bot.matchmaking")
            logger.info(f"Deleting archived thread {after.name} ({after.id})")
            await after.delete()

    @tasks.loop(minutes=15)
    async def archive_threads(self) -> None:
        """Deletes all threads in matchmaking channels that have no activity for 60 minutes.
        Runs every 15 minutes as to not spam the API too much."""
        # Just flattens the list of lists into a single list and iterates over it.
        for channel_id in [
            id
            for channels in [
                TGArenaChannelIDs.PUBLIC_ARENAS,
                TGArenaChannelIDs.PRIVATE_ARENAS,
                TGArenaChannelIDs.OPEN_RANKED_ARENAS,
                TGArenaChannelIDs.CLOSED_RANKED_ARENAS,
            ]
            for id in channels
        ]:
            channel = self.bot.get_channel(channel_id)

            # These are 100% either going to be GuildChannels or None, but why not rule out everything else too.
            if not isinstance(channel, discord.abc.GuildChannel):
                continue

            for thread in channel.threads:
                # Both the id and the message can be None.
                if thread.last_message_id is None:
                    continue

                try:
                    last_message = await thread.fetch_message(thread.last_message_id)
                except discord.NotFound:
                    continue

                if (
                    discord.utils.utcnow().timestamp()
                    - last_message.created_at.timestamp()
                    >= 3600
                ):
                    logger = self.bot.get_logger("bot.matchmaking")
                    logger.info(
                        f"Deleting thread {thread.name} ({thread.id}) automatically because of inactivity."
                    )
                    await thread.delete()

    @archive_threads.before_loop
    async def before_archive_threads(self) -> None:
        await self.bot.wait_until_ready()

    @commands.hybrid_command(
        aliases=["matchmaking", "matchmakingsingles", "mmsingles", "Singles"]
    )
    @commands.cooldown(1, 600, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def singles(self, ctx: commands.Context) -> None:
        """Used for 1v1 Matchmaking with competitive rules."""
        await self.handle_request(ctx, "singles")

    @singles.error
    async def singles_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        await self.handle_request(ctx, "singles", timeout=error.retry_after)

    @commands.hybrid_command(aliases=["matchmakingdoubles", "mmdoubles", "Doubles"])
    @commands.cooldown(1, 600, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def doubles(self, ctx: commands.Context) -> None:
        """Used for 2v2 Matchmaking."""
        await self.handle_request(ctx, "doubles")

    @doubles.error
    async def doubles_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        await self.handle_request(ctx, "doubles", timeout=error.retry_after)

    @commands.hybrid_command(aliases=["matchmakingfunnies", "mmfunnies", "Funnies"])
    @commands.cooldown(1, 600, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        message="Optional message, for example the ruleset you want to use."
    )
    async def funnies(self, ctx: commands.Context, *, message: str = None) -> None:
        """Used for 1v1 Matchmaking with non-competitive rules."""
        await self.handle_request(ctx, "funnies", message=message)

    @funnies.error
    async def funnies_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        await self.handle_request(ctx, "funnies", timeout=error.retry_after)

    @commands.hybrid_command(aliases=["rankedmm", "rankedmatchmaking", "rankedsingles"])
    @commands.cooldown(1, 120, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def ranked(self, ctx: commands.Context) -> None:
        """Used for 1v1 competitive ranked matchmaking."""
        await self.handle_request(ctx, "ranked")

    @ranked.error
    async def ranked_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        await self.handle_request(ctx, "ranked", timeout=error.retry_after)

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def recentpings(self, ctx: commands.Context) -> None:
        """Gets you a menu where you can see the recent pings of each Matchmaking Type."""
        await ctx.send(
            "Here are all available ping types:", view=DropdownPings(self.bot)
        )

    @commands.hybrid_command(aliases=["clearmmrequests", "clearmm", "clearmatchmaking"])
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def clearmmpings(self, ctx: commands.Context) -> None:
        """Clears the Matchmaking Pings manually."""
        self.clear_mmrequests()
        await ctx.send("Cleared the matchmaking pings!")


async def setup(bot) -> None:
    await bot.add_cog(Matchmaking(bot))
    print("Matchmaking cog loaded")
