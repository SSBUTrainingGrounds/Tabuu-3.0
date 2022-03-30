import asyncio

import discord
from discord.ext import commands

import utils.check
from utils.ids import AdminVars, GuildIDs, GuildNames
from utils.role import search_role


class Admin(commands.Cog):
    """
    Contains most general purpose Admin Commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @utils.check.is_moderator()
    async def clear(self, ctx, amount=1):
        """
        Clears the last X messages from the channel the command is used in.
        If you do not specify an amount it defaults to 1.
        """
        if amount < 1:
            await ctx.send("Please input a valid number!")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(
            f"Successfully deleted `{len(deleted)}` messages, {ctx.author.mention}"
        )

    @commands.command()
    @utils.check.is_moderator()
    async def delete(self, ctx, *messages: discord.Message):
        """
        Deletes one or more messages via Message ID.
        The messages have to be in the same channel the command is used in.
        """
        for message in messages:
            await message.delete()
        await ctx.message.delete()

    @commands.command()
    @utils.check.is_moderator()
    async def ban(self, ctx, user: discord.User, *, reason):
        """
        Bans a user from the current server with the specified reason, also tries to DM the user.
        Asks you for confirmation beforehand, because the Mod Team couldn't stop playing with this command.
        """

        def check(m):
            return (
                m.content.lower() in ("y", "n")
                and m.author == ctx.author
                and m.channel == ctx.channel
            )

        # if the reason provided is too long for the embed, we'll just cut it off
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
                # tries to dm them first, need a try/except block
                # cause you can ban ppl not on your server, or ppl can block your bot
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

    @commands.command()
    @utils.check.is_moderator()
    async def unban(self, ctx, user: discord.User):
        """
        Unbans a user from the current server.
        """
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned!")

    @commands.command(aliases=["syncbans"])
    @utils.check.is_moderator()
    async def syncbanlist(self, ctx):
        """
        Only available on the Battlegrounds Server.
        Automatically bans every user who is banned on the Training Grounds Server.
        Warning: Very slow & inefficient.
        """
        if ctx.guild.id != GuildIDs.BATTLEGROUNDS:
            await ctx.send(
                f"This command is only available on the {GuildNames.BATTLEGROUNDS} server!"
            )
            return

        tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        bans = await tg_guild.bans()

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

    @commands.command()
    @utils.check.is_moderator()
    async def kick(self, ctx, member: discord.Member, *, reason):
        """
        Kicks a user from the current server with the specified reason, also tries to DM the user.
        Asks you for confirmation beforehand, because the Mod Team couldn't stop playing with this command.
        Very similar to the ban command.
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

    @commands.command()
    @utils.check.is_moderator()
    async def addrole(self, ctx, member: discord.Member, *, input_role):
        """
        Adds the specified role to the specified member.
        """
        role = search_role(ctx.guild, input_role)

        await member.add_roles(role)
        await ctx.send(f"{member.mention} was given the {role} role.")

    @commands.command()
    @utils.check.is_moderator()
    async def removerole(self, ctx, member: discord.Member, *, input_role):
        """
        Removes the specified role from the specified member.
        """
        role = search_role(ctx.guild, input_role)

        await member.remove_roles(role)
        await ctx.send(f"{member.mention} no longer has the {role} role.")

    @commands.command()
    @utils.check.is_moderator()
    async def records(self, ctx):
        """
        Links our ban records google doc.
        """
        await ctx.send(f"Link to our ban records:\n{AdminVars.BAN_RECORDS}")

    @commands.command()
    @utils.check.is_moderator()
    async def rename(self, ctx, member: discord.Member, *, name=None):
        """
        Renames the specified member to the specified name.
        """
        await member.edit(nick=name)
        await ctx.send(
            f"Changed the display name of {discord.utils.escape_markdown(str(member))} to `{name}`."
        )

    # error handling for the commands above
    # they all are fairly similar
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a reason for the kick!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
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
        elif isinstance(error, commands.CommandInvokeError):
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
        elif isinstance(error, commands.CommandInvokeError):
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
        elif isinstance(error, commands.CommandInvokeError):
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
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "I didn't find a good match for the role you provided. "
                "Please be more specific, or mention the role, or use the Role ID."
            )
        else:
            raise error

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please input a valid number!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "I could not delete one or more of these messages! "
                "Make sure they were not send too long ago or try a different amount."
            )
        else:
            raise error

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send(
                "Could not find a message with that ID! "
                "Make sure you are in the same channel as the message(s) you want to delete."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please supply one or more valid message IDs")
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
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Something went wrong! Please try again.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Admin(bot))
    print("Admin cog loaded")
