from itertools import cycle

import aiosqlite
import discord
from discord.ext import commands, tasks

from cogs.levels import Levels
from utils.ids import BGChannelIDs, BGRoleIDs, GuildIDs, TGChannelIDs, TGRoleIDs


class Events(commands.Cog):
    """Contains the event listeners, Welcome/Booster messages,
    Autorole, Status updates, and so on.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.change_status.start()

    def cog_unload(self) -> None:
        self.change_status.cancel()

    # Status cycles through these, update these once in a while to keep it fresh.
    status = cycle(
        [
            "type {prefix}help",
            "Always watching 👀",
            "What is love?",
            "Executing Plan Z.",
            "...with your heart.",
            "Harder, better, faster, stronger.",
            "Reading menu...",
            "Read the rules!",
            "I'm in your area.",
            "Gambling... 🎰",
            "1% Evil, 99% Hot Gas.",
            "↑ ↑ ↓ ↓ ← → ← → B A Start",
            "{members} Members",
            "Version {version}",
        ]
    )

    @tasks.loop(seconds=600)
    async def change_status(self) -> None:
        """Changes the status every 10 Minutes."""
        await self.bot.change_presence(
            activity=discord.Game(
                next(self.status).format(
                    members=len(set(self.bot.get_all_members())),
                    version=self.bot.version_number,
                    prefix=self.bot.main_prefix,
                )
            )
        )

    @change_status.before_loop
    async def before_change_status(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await Levels.create_new_profile(self, member)

        async with aiosqlite.connect("./db/database.db") as db:
            matching_user = await db.execute_fetchall(
                """SELECT * FROM muted WHERE user_id = :user_id""",
                {"user_id": member.id},
            )
            user_level = await db.execute_fetchall(
                """SELECT level FROM level WHERE id = :id""",
                {"id": member.id},
            )

        if member.guild.id == GuildIDs.TRAINING_GROUNDS:
            channel = self.bot.get_channel(TGChannelIDs.GENERAL_CHANNEL)
            rules = self.bot.get_channel(TGChannelIDs.RULES_CHANNEL)

            # Checking if the user is muted when he joins.
            if len(matching_user) != 0:
                # Getting both the cadet role and the muted role
                # since you dont really have to accept the rules if you come back muted.
                muted_role = discord.utils.get(
                    member.guild.roles, id=TGRoleIDs.MUTED_ROLE
                )
                await member.add_roles(muted_role)
                await Levels.update_level_role(
                    self, member, user_level[0][0], member.guild
                )

                await channel.send(
                    f"Welcome back, {member.mention}! You are still muted, so maybe check back later."
                )
                return

            # If not this is the normal greeting.
            await channel.send(
                f"{member.mention} has joined the ranks! What's shaking?\n"
                f"Please take a look at the {rules.mention} channel for information about server events/functions!"
            )

        elif member.guild.id == GuildIDs.BATTLEGROUNDS:
            channel = self.bot.get_channel(BGChannelIDs.OFF_TOPIC_CHANNEL)
            rules_channel = self.bot.get_channel(BGChannelIDs.RULES_CHANNEL)
            traveller = discord.utils.get(
                member.guild.roles, id=BGRoleIDs.TRAVELLER_ROLE
            )

            if len(matching_user) != 0:
                muted_role = discord.utils.get(
                    member.guild.roles, id=BGRoleIDs.MUTED_ROLE
                )
                await member.add_roles(muted_role)
                await member.add_roles(traveller)
                await channel.send(
                    f"Welcome back, {member.mention}! You are still muted, so maybe check back later."
                )
                return

            await member.add_roles(traveller)
            await channel.send(
                f"{member.mention} has entered the battlegrounds. ⚔️\n"
                "If you are interested on getting in on some crew battle action, "
                f"head to {rules_channel.mention} to get familiar with how the server works!"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        # Adds/removes a VC role when you join/leave a VC channel.
        voice_channel = TGChannelIDs.GENERAL_VOICE_CHAT
        if (
            (before.channel is None or before.channel.id != voice_channel)
            and after.channel is not None
            and after.channel.id == voice_channel
        ):
            try:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
                await member.add_roles(vc_role)
            except discord.HTTPException:
                pass

        if (
            (after.channel is None or after.channel.id != voice_channel)
            and before.channel is not None
            and before.channel.id == voice_channel
        ):
            try:
                guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
                vc_role = discord.utils.get(guild.roles, id=TGRoleIDs.VOICE_ROLE)
                await member.remove_roles(vc_role)
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        # For tracking the last 5 username updates.
        if before.name != after.name:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """INSERT INTO usernames VALUES (:user_id, :old_name, :timestamp)""",
                    {
                        "user_id": before.id,
                        "old_name": before.name,
                        "timestamp": int(discord.utils.utcnow().timestamp()),
                    },
                )

                # This will keep only the lastest 5 entries, in order to not flood the db too much.
                # I think the timestamp + user id will be enough to identify a unique entry,
                # not sure if you can even change your name twice in 1s, rate limit wise.
                await db.execute(
                    """DELETE FROM usernames WHERE user_id = :user_id AND timestamp NOT IN
                    (SELECT timestamp FROM usernames WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 5)""",
                    {"user_id": before.id},
                )

                await db.commit()

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        # For tracking the last 5 nickname updates.
        if before.display_name not in [after.display_name, before.name]:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """INSERT INTO nicknames VALUES (:user_id, :old_name, :guild_id, :timestamp)""",
                    {
                        "user_id": before.id,
                        "old_name": before.display_name,
                        "guild_id": before.guild.id,
                        "timestamp": int(discord.utils.utcnow().timestamp()),
                    },
                )

                await db.execute(
                    """DELETE FROM nicknames WHERE user_id = :user_id AND timestamp NOT IN
                    (SELECT timestamp FROM nicknames WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT 5)""",
                    {"user_id": before.id},
                )

                await db.commit()

        # For announcing boosts/premium memberships.
        if len(before.roles) < len(after.roles):
            channel = self.bot.get_channel(TGChannelIDs.ANNOUNCEMENTS_CHANNEL)

            new_role = next(role for role in after.roles if role not in before.roles)

            # For a new boost.
            if new_role.id == TGRoleIDs.BOOSTER_ROLE:
                await channel.send(f"{after.mention} has boosted the server! 🥳🎉")

            # For when someone new subs to the premium thing.
            if new_role.id == TGRoleIDs.PREMIUM_ROLE:
                await channel.send(
                    f"{after.mention} is now a Premium Member of the server! 🥳🎉"
                )

        # We also take away the colour roles if you stop boosting.
        if len(before.roles) > len(after.roles):
            old_role = next(role for role in before.roles if role not in after.roles)

            if old_role.id == TGRoleIDs.BOOSTER_ROLE:
                for role in TGRoleIDs.COLOUR_ROLES:
                    try:
                        removerole = discord.utils.get(after.guild.roles, id=role)
                        if removerole in after.roles:
                            await after.remove_roles(removerole)
                    except discord.HTTPException:
                        pass

        # This here gives out the recruit role on a successful member screening,
        # on join was terrible because of the android app, for whatever reason.
        try:
            if before.bot or after.bot:
                return

            if (
                before.pending
                and not after.pending
                and before.guild.id == GuildIDs.TRAINING_GROUNDS
            ):
                await Levels.create_new_profile(self, after)

                async with aiosqlite.connect("./db/database.db") as db:
                    user_level = await db.execute_fetchall(
                        """SELECT level FROM level WHERE id = :id""",
                        {"id": after.id},
                    )

                    await Levels.update_level_role(
                        self, after, user_level[0][0], after.guild
                    )

        except AttributeError:
            pass

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context) -> None:
        logger = self.bot.get_logger("bot.commands")
        logger.info(
            f"Command successfully ran: {ctx.prefix}{ctx.invoked_with} "
            f"(invoked by {str(ctx.author)})"
        )

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        self.bot.commands_ran += 1

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        logger = self.bot.get_logger("bot.app_commands")
        logger.info(
            f"Application Command successfully ran: {interaction.id} (invoked by {str(interaction.user)})"
        )
        self.bot.commands_ran += 1

    @commands.Cog.listener()
    async def on_socket_event_type(self, event_type: str) -> None:
        self.bot.events_listened_to += 1

    # These just log when the bot loses/regains connection
    @commands.Cog.listener()
    async def on_connect(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.info("Connected to discord.")

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.warning("Lost connection to discord.")

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        logger = self.bot.get_logger("bot.connection")
        logger.info("Resumed connection to discord.")


async def setup(bot) -> None:
    await bot.add_cog(Events(bot))
    print("Events cog loaded")
