import asyncio
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands

import utils.check
from utils.ids import AdminVars, GuildIDs, GuildNames
from utils.search import search_role


class Admin(commands.Cog):
    """Contains most general purpose Admin Commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(amount="The amount of messages to delete.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def clear(self, ctx: commands.Context, amount: int = 1):
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
    async def ban(self, ctx: commands.Context, user: discord.User, *, reason: str):
        """Bans a user from the current server.
        Asks you for confirmation beforehand.
        Tries to DM the user the reasoning along with the ban records.
        """

        def check(m):
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
                        f"Please contact {AdminVars.GROUNDS_KEEPER} for an appeal.\n{AdminVars.BAN_RECORDS}"
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
    async def unban(self, ctx: commands.Context, user: discord.User):
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
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Bans a user from the current server.
        Asks you for confirmation beforehand.
        Tries to DM the user the reasoning, similar to the ban command.
        """

        def check(m):
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
        member="The member to add a role to.", input_role="The role to add."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def addrole(
        self, ctx: commands.Context, member: discord.Member, *, input_role: str
    ):
        """Adds a role to a member."""
        role = search_role(ctx.guild, input_role)

        await member.add_roles(role)
        await ctx.send(f"{member.mention} was given the {role} role.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        member="The member to remove a role from.", input_role="The role to remove."
    )
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def removerole(
        self, ctx: commands.Context, member: discord.Member, *, input_role: str
    ):
        """Removes a role from a member."""
        role = search_role(ctx.guild, input_role)

        await member.remove_roles(role)
        await ctx.send(f"{member.mention} no longer has the {role} role.")

    @commands.group()
    @utils.check.is_moderator()
    async def editrole(self, ctx: commands.Context):
        """
        Lists the group commands for editing a role.
        """
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{self.bot.command_prefix}editrole name <role> <new name>`\n"
            f"`{self.bot.command_prefix}editrole colour <role> <hex colour>`\n"
            f"`{self.bot.command_prefix}editrole icon <role> <emoji/attachment>`\n"
            f"`{self.bot.command_prefix}editrole mentionable <role> <True/False>`\n",
            colour=0x007377,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @editrole.command(name="name")
    @utils.check.is_moderator()
    async def editrole_name(
        self, ctx: commands.Context, role: discord.Role, *, name: str
    ):
        """
        Edits the name of a role.
        """
        old_role_name = role.name

        # unfortunately we have to handle the Forbidden error here,
        # since the error handler will not handle it easily.
        try:
            await role.edit(name=name)
            await ctx.send(f"Changed name of {old_role_name} to {role.name}.")
        except discord.errors.Forbidden:
            await ctx.send("I do not have the required permissions to edit this role.")

    @editrole.command(name="colour", aliases=["color"])
    @utils.check.is_moderator()
    async def editrole_colour(
        self, ctx: commands.Context, role: discord.Role, hex_colour: str
    ):
        """
        Edits the colour of a role, use a hex colour code.
        """
        # hex colour codes are 7 digits long and start with #
        if not hex_colour.startswith("#") or len(hex_colour) != 7:
            await ctx.send(
                "Please choose a valid hex colour code. "
                f"Example: `{self.bot.command_prefix}editrole colour role #8a0f84`"
            )
            return

        hex_colour = hex_colour.replace("#", "0x")

        try:
            colour = int(hex_colour, 16)
        except ValueError:
            await ctx.send(
                "Please choose a valid hex colour code. "
                f"Example: `{self.bot.command_prefix}editrole colour role #8a0f84`"
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
        emoji: Union[discord.Emoji, str] = None,
    ):
        """
        Edits the role icon with an emoji or an attachment.
        """
        # role icons can be either emojis or images
        # if none of these are specified, we remove the icon
        if not emoji and not ctx.message.attachments:
            try:
                await role.edit(display_icon=None)
                await ctx.send(f"Removed the display icon of {role.name}.")
            except discord.errors.Forbidden:
                await ctx.send(
                    "I do not have the required permissions to edit this role."
                )
            return

        async def apply_icon(asset: Union[discord.Emoji, discord.Attachment]):
            """
            This function reads the asset as a byte-like object
            and tries to insert that as the role icon.
            """
            try:
                asset_icon = await asset.read()
                await role.edit(display_icon=asset_icon)
                await ctx.send(
                    f"Edited the display icon of {role.name} to {asset.url} ."
                )
            # the normal Missing Permissions thing doesnt work here,
            # since this could raise a variety of errors.
            except (discord.errors.Forbidden, discord.errors.HTTPException) as exc:
                await ctx.send(f"Something went wrong:\n`{exc}`")

        if emoji:
            # we first need to check for a custom emoji
            if isinstance(emoji, discord.Emoji):
                await apply_icon(emoji)
                return

            # or else if it is a regular emoji
            try:
                await role.edit(display_icon=emoji)
                await ctx.send(f"Edited the display icon of {role.name} to {emoji}.")
            except (discord.errors.Forbidden, discord.errors.HTTPException) as exc:
                await ctx.send(f"Something went wrong:\n`{exc}`")
            return

        # we check if the attachment its a supported icon type
        if not ctx.message.attachments[0].url.endswith((".jpg", ".jpeg", ".png")):
            await ctx.send(
                "Please either specify an emoji or attach an image to use as a role icon."
            )
            return

        await apply_icon(ctx.message.attachments[0])

    @editrole.command(name="mentionable", aliases=["mention"])
    @utils.check.is_moderator()
    async def editrole_mentionable(
        self, ctx: commands.Context, role: discord.Role, mentionable: bool
    ):
        """
        Makes the role mentionable or unmentionable. Use a boolean type.
        """
        try:
            await role.edit(mentionable=mentionable)
            await ctx.send(f"Set {role.name} mentionable status to: {mentionable}.")
        except discord.errors.Forbidden:
            await ctx.send("I do not have the required permissions to edit this role.")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def records(self, ctx: commands.Context):
        """Links our ban records google doc."""
        await ctx.send(f"Link to our ban records:\n{AdminVars.BAN_RECORDS}")

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member to rename.", name="The new name.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def rename(
        self, ctx: commands.Context, member: discord.Member, *, name: str = None
    ):
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
    ):
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

    # Error handling for the commands above.
    # They all are fairly similar
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a reason for the kick!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Invalid ID, please make sure you got the right one, or just mention a member."
            )
        else:
            raise error

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a reason for the ban!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Invalid ID, please make sure you got the right one, or just mention a member."
            )
        else:
            raise error

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member to unban.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("I could not find this user!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I couldn't find a ban for this ID, make sure you have the right one."
            )
        else:
            raise error

    @syncbanlist.error
    async def syncbanlist_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a role!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )
        else:
            raise error

    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a role!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )
        else:
            raise error

    @editrole.error
    async def editrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @editrole_name.error
    async def editrole_name_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Please specify a valid role.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a role and the new name of the role.")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Please specify a valid role name.")
        else:
            raise error

    @editrole_colour.error
    async def editrole_colour_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Please specify a valid role.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a role and a hex colour code.")
        else:
            raise error

    @editrole_icon.error
    async def editrole_icon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Please specify a valid role.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a role and an optional icon or emoji.")
        else:
            raise error

    @editrole_mentionable.error
    async def editrole_mentionable_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Please specify a valid role.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a role and if it should be mentionable.")
        elif isinstance(error, commands.BadBoolArgument):
            await ctx.send("Please only use either True or False as the value.")
        else:
            raise error

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please input a valid number!")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "I could not delete one or more of these messages! "
                "Make sure they were not send too long ago or try a different amount."
            )
        else:
            raise error

    @records.error
    async def records_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @rename.error
    async def rename_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please enter a valid member.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a member.")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Something went wrong! Please try again.")
        else:
            raise error

    @say.error
    async def say_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a destination and a message to repeat.")
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send("Please make sure to input a valid Message ID or Link.")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send("Please input a valid Channel, Thread or Message ID.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Admin(bot))
    print("Admin cog loaded")
