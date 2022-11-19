import asyncio
import random
from typing import Optional, Union

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

import utils.check
import utils.search
from utils.ids import AdminVars, GuildIDs, GuildNames


class Admin(commands.Cog):
    """Contains most general purpose Admin Commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(amount="The amount of messages to delete.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def clear(self, ctx: commands.Context, amount: int = 1) -> None:
        """Clears the last X messages from the channel the command is used in.
        If you do not specify an amount it defaults to 1.
        """
        if amount < 1:
            await ctx.send("Please input a valid number!")
            return

        await ctx.defer()

        deleted = await ctx.channel.purge(limit=amount + 1)

        # Using channel.send for the slash command, it would otherwise try to reply to the deleted message.
        await ctx.channel.send(
            f"Successfully deleted `{len(deleted)}` messages, {ctx.author.mention}"
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user to ban.", reason="The reason for the ban.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def ban(
        self, ctx: commands.Context, user: discord.User, *, reason: str
    ) -> None:
        """Bans a user from the current server.
        Asks you for confirmation beforehand.
        Tries to DM the user the reasoning along with the ban records.
        """

        def check(m: discord.Message) -> bool:
            return (
                m.content.lower() in ("y", "n")
                and m.author == ctx.author
                and m.channel == ctx.channel
            )

        # If the reason provided is too long for the embed, we'll just cut it off
        if len(reason[2000:]) > 0:
            reason = reason[:2000]

        embed = discord.Embed(
            title=f"{str(user)} ({user.id})",
            description=f"**Reason:** {reason}",
            colour=discord.Colour.dark_red(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(
            f"{ctx.author.mention}, are you sure you want to ban this user? "
            "**Type y to verify** or **Type n to cancel**.",
            embed=embed,
        )

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"Ban for {user.mention} timed out, try again.")
            return
        else:
            if msg.content.lower() == "y":
                # Tries to dm them first, need a try/except block.
                # Because you can ban people not on your server, or they can block your bot, etc.
                try:
                    await user.send(
                        f"You have been banned from the {ctx.guild.name} Server for the following reason: \n"
                        f"```{reason}```\n"
                        f"Check here to see the earliest you are able to appeal your ban (if at all): <{AdminVars.BAN_RECORDS}>\n\n"
                        f"Please use this form if you wish to appeal your ban: {AdminVars.APPEAL_FORM}"
                    )
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.admin")
                    logger.warning(
                        f"Tried to message ban reason to {str(user)}, but it failed: {exc}"
                    )

                await ctx.guild.ban(user, reason=reason)
                await ctx.send(f"{user.mention} has been banned!")
            elif msg.content.lower() == "n":
                await ctx.send(f"Ban for {user.mention} cancelled.")
                return

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user to unban.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def unban(self, ctx: commands.Context, user: discord.User) -> None:
        """Removes the ban of a user from the current server."""
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned!")

    @commands.hybrid_command(aliases=["syncbans"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def syncbanlist(self, ctx: commands.Context):
        """Automatically bans every user who is banned on the Training Grounds Server.
        Only available on the Battlegrounds Server.
        Warning: Very slow & inefficient.
        """
        if ctx.guild.id != GuildIDs.BATTLEGROUNDS:
            await ctx.send(
                f"This command is only available on the {GuildNames.BATTLEGROUNDS} server!"
            )
            return

        await ctx.defer()

        tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        bans = [entry async for entry in tg_guild.bans(limit=None)]

        await ctx.send("Syncing ban list... Please wait a few seconds.")

        i = 0

        for u in bans:
            try:
                await ctx.guild.fetch_ban(u.user)
            except discord.NotFound:
                await ctx.guild.ban(
                    u.user,
                    reason=f"Automatic ban because user was banned on the {GuildNames.TG} server.",
                )
                await ctx.send(f"Banned {discord.utils.escape_markdown(str(u.user))}!")
                i += 1

        await ctx.send(f"Ban list was successfully synced. Banned {i} users.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The user to kick.", reason="The reason for the kick."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def kick(
        self, ctx: commands.Context, member: discord.Member, *, reason: str
    ) -> None:
        """Bans a user from the current server.
        Asks you for confirmation beforehand.
        Tries to DM the user the reasoning, similar to the ban command.
        """

        def check(m: discord.Message) -> bool:
            return (
                m.content.lower() in ("y", "n")
                and m.author == ctx.author
                and m.channel == ctx.channel
            )

        if len(reason[2000:]) > 0:
            reason = reason[:2000]

        embed = discord.Embed(
            title=f"{str(member)} ({member.id})",
            description=f"**Reason:** {reason}",
            colour=discord.Colour.dark_orange(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(
            f"{ctx.author.mention}, are you sure you want to kick this user? "
            "**Type y to verify** or **Type n to cancel**.",
            embed=embed,
        )

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"Kick for {member.mention} timed out, try again.")
            return
        else:
            if msg.content.lower() == "y":
                try:
                    await member.send(
                        f"You have been kicked from the {ctx.guild.name} Server for the following reason: \n"
                        f"```{reason}```\n"
                        f"If you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                    )
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.admin")
                    logger.warning(
                        f"Tried to message kick reason to {str(member)}, but it failed: {exc}"
                    )

                await member.kick(reason=reason)
                await ctx.send(f"Kicked {member}!")
            elif msg.content.lower() == "n":
                await ctx.send(f"Kick for {member.mention} cancelled.")
                return

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to add a role to.", role="The role to add."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def addrole(
        self, ctx: commands.Context, member: discord.Member, *, role: str
    ) -> None:
        """Adds a role to a member."""
        matching_role = utils.search.search_role(ctx.guild, role)

        await member.add_roles(matching_role)
        await ctx.send(f"{member.mention} was given the {matching_role} role.")

    @addrole.autocomplete("role")
    async def addrole_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        return utils.search.autocomplete_choices(
            current, [role.name for role in interaction.guild.roles]
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to remove a role from.", role="The role to remove."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def removerole(
        self, ctx: commands.Context, member: discord.Member, *, role: str
    ) -> None:
        """Removes a role from a member."""
        matching_role = utils.search.search_role(ctx.guild, role)

        await member.remove_roles(matching_role)
        await ctx.send(f"{member.mention} no longer has the {matching_role} role.")

    @removerole.autocomplete("role")
    async def removerole_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        return utils.search.autocomplete_choices(
            current, [role.name for role in interaction.guild.roles]
        )

    @commands.hybrid_group()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def editrole(self, ctx: commands.Context) -> None:
        """Lists the group commands for editing a role."""
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{ctx.prefix}editrole name <role> <new name>`\n"
            f"`{ctx.prefix}editrole colour <role> <hex colour>`\n"
            f"`{ctx.prefix}editrole icon <role> <emoji/attachment>`\n"
            f"`{ctx.prefix}editrole mentionable <role> <True/False>`\n",
            colour=self.bot.colour,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @editrole.command(name="name")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        role="The role to edit the name of.", name="The new name of the role."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def editrole_name(
        self, ctx: commands.Context, role: discord.Role, *, name: str
    ) -> None:
        """Edits the name of a role."""
        old_role_name = role.name

        # Unfortunately we have to handle the Forbidden error here,
        # since the error handler will not handle it easily.
        try:
            await role.edit(name=name)
            await ctx.send(f"Changed name of {old_role_name} to {name}.")
        except discord.errors.Forbidden:
            await ctx.send("I do not have the required permissions to edit this role.")

    @editrole.command(name="colour", aliases=["color"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        role="The role to edit the colour of.",
        hex_colour="The new colour, in the hex format.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def editrole_colour(
        self, ctx: commands.Context, role: discord.Role, hex_colour: str
    ) -> None:
        """Edits the colour of a role, use a hex colour code."""
        # Hex colour codes are 7 digits long and start with #
        if not hex_colour.startswith("#") or len(hex_colour) != 7:
            await ctx.send(
                "Please choose a valid hex colour code. "
                f"Example: `{ctx.prefix}editrole colour role #8a0f84`"
            )
            return

        hex_colour = hex_colour.replace("#", "0x")

        try:
            colour = int(hex_colour, 16)
        except ValueError:
            await ctx.send(
                "Please choose a valid hex colour code. "
                f"Example: `{ctx.prefix}editrole colour role #8a0f84`"
            )
            return

        try:
            await role.edit(colour=colour)
            await ctx.send(f"Changed colour of {role.name} to {hex_colour}")
        except discord.errors.Forbidden:
            await ctx.send("I do not have the required permissions to edit this role.")

    @editrole.command(name="icon")
    @utils.check.is_moderator()
    async def editrole_icon(
        self,
        ctx: commands.Context,
        role: discord.Role,
        emoji: str = None,
        attachment: Optional[discord.Attachment] = None,
    ) -> None:
        """Edits the role icon with an emoji or an attachment."""

        await ctx.defer()

        async def apply_icon(asset: Union[discord.Emoji, discord.Attachment]):
            """This function reads the asset as a byte-like object
            and tries to insert that as the role icon.
            """
            try:
                asset_icon = await asset.read()
                await role.edit(display_icon=asset_icon)
                await ctx.send(
                    f"Edited the display icon of {role.name} to {asset.url} ."
                )
            # The normal Missing Permissions thing doesnt work here,
            # since this could raise a variety of errors.
            except (discord.errors.Forbidden, discord.errors.HTTPException) as exc:
                await ctx.send(f"Something went wrong:\n`{exc}`")

        # Role icons can be either emojis or images,
        # if none of these are specified, we remove the icon.
        if not emoji and not attachment:
            try:
                await role.edit(display_icon=None)
                await ctx.send(f"Removed the display icon of {role.name}.")
            except discord.errors.Forbidden:
                await ctx.send(
                    "I do not have the required permissions to edit this role."
                )
            return

        # First we check if an Attachment is supplied.
        if attachment:
            if not attachment.url.endswith((".jpg", ".jpeg", ".png")):
                await ctx.send(
                    "Please either specify an emoji or attach an image to use as a role icon."
                )
                return
            await apply_icon(attachment)
            return

        # After that we check for an Emoji.
        emoji_converter = commands.EmojiConverter()
        try:
            emoji = await emoji_converter.convert(ctx, emoji)
            await apply_icon(emoji)
        except commands.EmojiNotFound:
            # We then check if it is a regular emoji.
            try:
                await role.edit(display_icon=emoji)
                await ctx.send(f"Edited the display icon of {role.name} to {emoji}.")
            except (discord.errors.Forbidden, discord.errors.HTTPException) as exc:
                await ctx.send(f"Something went wrong:\n`{exc}`")

    @editrole.command(name="mentionable", aliases=["mention"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        role="The role to edit the mentionable status of.",
        mentionable="The new mentionable status (True/False).",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def editrole_mentionable(
        self, ctx: commands.Context, role: discord.Role, mentionable: bool
    ) -> None:
        """Makes the role mentionable or unmentionable. Use a boolean type."""
        try:
            await role.edit(mentionable=mentionable)
            await ctx.send(f"Set {role.name} mentionable status to: {mentionable}.")
        except discord.errors.Forbidden:
            await ctx.send("I do not have the required permissions to edit this role.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def records(self, ctx: commands.Context) -> None:
        """Links our ban records google doc."""
        await ctx.send(f"Link to our ban records:\n{AdminVars.BAN_RECORDS}")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to rename.", name="The new name.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def rename(
        self, ctx: commands.Context, member: discord.Member, *, name: str = None
    ) -> None:
        """Renames a member to the specified name."""
        await member.edit(nick=name)
        await ctx.send(
            f"Changed the display name of {discord.utils.escape_markdown(str(member))} to `{name}`."
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        messageable="Where to send the message/reply to (Channel, Thread, Message).",
        message="The message I will send.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def say(
        self,
        ctx: commands.Context,
        messageable: str,
        *,
        message: str,
    ) -> None:
        """Repeats a message in a given channel or thread, or replies to a message."""
        destination = None

        # There is probably a better way to do this with slash commands,
        # but since neither Links nor other forms of valid IDs have any of those chars in it we can remove those
        # to be able to send to channels even if the user supplies the channel as #Example Channel.
        # With normal commands we could just use a Union Converter and save us the headache.
        messageable = messageable.strip("<>#")

        if messageable.isnumeric():
            destination = ctx.guild.get_channel_or_thread(int(messageable))

        if not destination:
            message_converter = commands.MessageConverter()
            destination = await message_converter.convert(ctx, messageable)
            await destination.reply(message)
        else:
            await destination.send(message)

        await ctx.send("Message sent!", ephemeral=True)

    @commands.hybrid_command(aliases=["nicknames", "usernames", "aliases"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user you want to see the last tracked names of.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def names(self, ctx: commands.Context, user: discord.User) -> None:
        """Gets you the current and past names of a User."""
        if user == self.bot.user:
            await ctx.send("Cannot look up the name history for this user!")
            return

        # Getting the stored past user- and nicknames.
        async with aiosqlite.connect("./db/database.db") as db:
            usernames = await db.execute_fetchall(
                """SELECT * FROM usernames WHERE user_id = :user_id""",
                {"user_id": user.id},
            )
            nicknames = await db.execute_fetchall(
                """SELECT * FROM nicknames WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        user_embed = [
            f"{discord.utils.escape_markdown(name)} - <t:{timestamp}:R>\n"
            for _, name, timestamp in usernames
        ]

        nick_embed = []
        for (_, name, guild_id, timestamp) in nicknames:
            guild = self.bot.get_guild(guild_id)
            guild_name = guild.name if guild else "Unknown Server"
            nick_embed.append(
                f"{discord.utils.escape_markdown(name)} - <t:{timestamp}:R> ({guild_name})\n"
            )

        # We want the most recent names to show up first.
        user_embed.reverse()
        nick_embed.reverse()

        # Also getting the current nicknames.
        current_nicknames = []
        for guild in user.mutual_guilds:
            member = guild.get_member(user.id)
            if member and member.display_name != user.name:
                current_nicknames.append(
                    f"{discord.utils.escape_markdown(member.display_name)} ({guild.name})\n"
                )

        embed_desc = (
            f"**Current Nicknames:** \n{''.join(current_nicknames) if current_nicknames else 'None'}\n\n"
            f"**Last 5 Nicknames:** \n{''.join(nick_embed) if nick_embed else 'None'}\n\n"
            f"**Last 5 Usernames:** \n{''.join(user_embed) if user_embed else 'None'}"
        )

        embed = discord.Embed(
            title=f"Last Known Names of {str(user)} ({user.id})",
            colour=self.bot.colour,
            description=embed_desc,
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_group()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def modnote(self, ctx: commands.Context) -> None:
        """Lists the group commands for setting and deleting notes."""
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{ctx.prefix}modnote set <@user> <note>`\n"
            f"`{ctx.prefix}modnote delete <@user> <note_id>`\n"
            f"`{ctx.prefix}modnote view <@user>`\n",
            colour=self.bot.colour,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @modnote.command(name="set")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user="The user for which you want to set the note.",
        note="The note of the user.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def modnote_set(
        self, ctx: commands.Context, user: discord.User, *, note: str
    ) -> None:
        """Sets a note on a user visible for the staff team."""
        note_id = random.randint(1000000, 9999999)
        timestamp = int(discord.utils.utcnow().timestamp())
        # Only getting the first 160 chars, should hopefully be enough.
        # The maximum limit for an embed is 6000 characters,
        # 160 + 80 (For the set by header) * 25 (Max number of embed fields) = 6000.
        note = note[:160]

        async with aiosqlite.connect("./db/database.db") as db:
            await db.execute(
                """INSERT INTO notes VALUES (:note_id, :user_id, :timestamp, :mod_id, :note)""",
                {
                    "note_id": note_id,
                    "user_id": user.id,
                    "timestamp": timestamp,
                    "mod_id": ctx.author.id,
                    "note": note,
                },
            )

            await db.commit()

        await ctx.send(
            f"Set a new note (ID: `{note_id}`) for {user.mention} to:\n`{note}`"
        )

    @modnote.command(name="view")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def modnote_view(self, ctx: commands.Context, user: discord.User) -> None:
        """Views all of the notes of a user."""
        async with aiosqlite.connect("./db/database.db") as db:
            user_notes = await db.execute_fetchall(
                """SELECT * FROM notes WHERE user_id = :user_id""",
                {"user_id": user.id},
            )

        if len(user_notes) == 0:
            await ctx.send("This user does not have any notes set.")
            return

        embed = discord.Embed(
            title=f"Saved notes for {str(user)} ({user.id})", colour=self.bot.colour
        )

        # Only getting the last 25, because that is the max number of embed fields.
        for (note_id, _, timestamp, mod_id, note) in reversed(user_notes[:25]):
            embed.add_field(
                name=f"ID: {note_id}",
                value=f"**Set at: <t:{timestamp}:F> by: <@{mod_id}>\nContent:**\n{note}\n",
                inline=False,
            )

        await ctx.send(embed=embed)

    @modnote.command(name="delete")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user="The user for which you want to delete a note from.",
        note_id="The ID of the note you want to delete.",
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def modnote_delete(
        self, ctx: commands.Context, user: discord.User, note_id: str
    ) -> None:
        """Deletes a moderator note from a user."""
        async with aiosqlite.connect("./db/database.db") as db:
            matching_note = await db.execute_fetchall(
                """SELECT * FROM notes WHERE user_id = :user_id AND note_id = :note_id""",
                {"user_id": user.id, "note_id": note_id},
            )

            if len(matching_note) == 0:
                await ctx.send(
                    "I could not find any note with this ID. \n"
                    f"View all of the notes of a user with `{ctx.prefix}modnote view <@user>`"
                )
                return

            await db.execute(
                """DELETE FROM notes WHERE user_id = :user_id AND note_id = :note_id""",
                {"user_id": user.id, "note_id": note_id},
            )
            await db.commit()

        await ctx.send(f"Deleted note ID {note_id}.")

    @modnote_delete.autocomplete("note_id")
    async def modnote_delete_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        if not interaction.namespace.user:
            return []

        async with aiosqlite.connect("./db/database.db") as db:
            user_notes = await db.execute_fetchall(
                """SELECT note_id FROM notes WHERE user_id = :user_id""",
                {"user_id": interaction.namespace.user.id},
            )

        note_ids = [str(note[0]) for note in user_notes]

        # We dont really need the fuzzy search here, this is all just numbers.
        choices = [
            app_commands.Choice(name=note_name, value=note_name)
            for note_name in note_ids
            if current in note_name
        ]

        return choices[:25]

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(user="The user you want to look up.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def lookup(self, ctx: commands.Context, user: discord.User) -> None:
        """Looks up every little detail of a user.
        Calls the userinfo, warndetails, names and modnote view commands."""
        await ctx.send("Collecting information...")

        # The userinfo command needs a server member.
        if member := ctx.guild.get_member(user.id):
            command = self.bot.get_command("userinfo")
            await ctx.invoke(command, member)
        else:
            await ctx.send("Could not get user info as the user is not in this server.")

        commands = [
            self.bot.get_command("warndetails"),
            self.bot.get_command("names"),
            self.bot.get_command("modnote view"),
        ]
        for command in commands:
            await ctx.invoke(command, user)

    @kick.error
    async def kick_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Invalid ID, please make sure you got the right one, or just mention a member."
            )

    @ban.error
    async def ban_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Invalid ID, please make sure you got the right one, or just mention a member."
            )

    @unban.error
    async def unban_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I couldn't find a ban for this ID, make sure you have the right one."
            )

    @addrole.error
    async def addrole_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )

    @removerole.error
    async def removerole_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )

    @editrole_name.error
    async def editrole_name_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Please specify a valid role name.")

    @editrole_mentionable.error
    async def editrole_mentionable_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadBoolArgument):
            await ctx.send("Please only use either True or False as the value.")

    @clear.error
    async def clear_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please input a valid number!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I could not delete one or more of these messages! "
                "Make sure they were not send too long ago or try a different amount."
            )

    @rename.error
    async def rename_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Something went wrong! Please try again.")

    @say.error
    async def say_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Please input a valid Channel, Thread or Message ID.")

    @modnote_delete.error
    async def modnote_delete_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please input a valid note ID!")


async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))
    print("Admin cog loaded")
