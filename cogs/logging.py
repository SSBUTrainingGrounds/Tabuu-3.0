from io import StringIO
from typing import Sequence

import discord
from discord.ext import commands

import utils.embed
from utils.ids import GetIDFunctions


class Logging(commands.Cog):
    """Logs every little user update or message update into the logs channel."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        # Username change.
        if before.name != after.name:
            embed = discord.Embed(
                title="**✏️ Username changed ✏️**",
                description=f"Before: {before.name}\nAfter: {after.name}",
                colour=discord.Colour.orange(),
            )
            embed.set_author(
                name=f"{str(after)} ({after.id})", icon_url=after.display_avatar.url
            )
            embed.timestamp = discord.utils.utcnow()
            # We send the embed in every server that we have in common with the user.
            # If the bot is in another server without log channels,
            # this would throw an error so we check with the walrus operator.
            for server in after.mutual_guilds:
                if logs := self.bot.get_channel(
                    GetIDFunctions.get_logchannel(server.id)
                ):
                    await logs.send(embed=embed)

        # Avatar change.
        if before.display_avatar.url != after.display_avatar.url:
            embed = discord.Embed(
                title="**📷 Avatar changed 📷**",
                description="New avatar below:",
                colour=discord.Colour.dark_gray(),
            )
            embed.set_thumbnail(url=before.display_avatar.url)
            embed.set_image(url=after.display_avatar.url)
            embed.set_author(
                name=f"{str(after)} ({after.id})", icon_url=after.display_avatar.url
            )
            embed.timestamp = discord.utils.utcnow()
            for server in after.mutual_guilds:
                if logs := self.bot.get_channel(
                    GetIDFunctions.get_logchannel(server.id)
                ):
                    await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        # If someone changes their nickname on this server.
        if before.display_name != after.display_name:
            embed = discord.Embed(
                title="**✏️ Nickname changed ✏️**",
                description=f"Before: {before.display_name}\nAfter: {after.display_name}",
                colour=discord.Colour.orange(),
            )
            embed.set_author(
                name=f"{str(after)} ({after.id})", icon_url=after.display_avatar.url
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(before.guild.id)
            ):
                await logs.send(embed=embed)

        # Roles change.
        if before.roles != after.roles:
            # User gains a role.
            if len(before.roles) < len(after.roles):
                new_role = next(
                    role for role in after.roles if role not in before.roles
                )
                embed = discord.Embed(
                    title="**📈 User gained role 📈**",
                    description=f"Role gained: {new_role.mention}",
                    colour=discord.Colour.green(),
                )
                embed.set_author(
                    name=f"{str(after)} ({after.id})", icon_url=after.display_avatar.url
                )
                embed.timestamp = discord.utils.utcnow()
                if logs := self.bot.get_channel(
                    GetIDFunctions.get_logchannel(before.guild.id)
                ):
                    await logs.send(embed=embed)

            # User loses a role.
            if len(before.roles) > len(after.roles):
                old_role = next(
                    role for role in before.roles if role not in after.roles
                )
                embed = discord.Embed(
                    title="**📉 User lost role 📉**",
                    description=f"Role lost: {old_role.mention}",
                    colour=discord.Colour.dark_red(),
                )
                embed.set_author(
                    name=f"{str(after)} ({after.id})", icon_url=after.display_avatar.url
                )
                embed.timestamp = discord.utils.utcnow()
                if logs := self.bot.get_channel(
                    GetIDFunctions.get_logchannel(before.guild.id)
                ):
                    await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="**🎆 New member joined 🎆**",
            description=f"{str(member)} has joined the server!\n\n"
            f"**Account created:**\n{discord.utils.format_dt(member.created_at, style='R')}",
            colour=discord.Colour.green(),
        )
        embed.set_author(
            name=f"{str(member)} ({member.id})", icon_url=member.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(member.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        # @everyone is considered a role too, so we remove that from the list.
        everyone_role = discord.utils.get(member.guild.roles, name="@everyone")
        roles = [role.mention for role in member.roles if role is not everyone_role]

        # We reverse the list so the top roles get mentioned first.
        roles.reverse()

        # Users may leave without a role to their name (except @everyone i guess)
        role_description = f"{' '.join(roles)}" if roles else "No roles"

        embed = discord.Embed(
            title="** 🚶 Member left the server 🚶**",
            description=f"{str(member)} has left the server. \n**Lost roles:** \n{role_description}",
            colour=discord.Colour.dark_red(),
        )
        embed.set_author(
            name=f"{str(member)} ({member.id})", icon_url=member.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(member.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        # Dont want dms to be included, same in the below listeners.
        if not after.guild:
            return

        # Also dont care about bot message edits.
        if after.author.bot:
            return

        # Sometimes the message content may be the same, so we skip that, too.
        if before.content == after.content:
            return

        # Discord released an update where they allow nitro users to send messages with up to 4000 chars in them,
        # but an embed can only have 6000 chars in them.
        # So we need to add in a check to not get dumb errors.
        # A description fits 4096 chars, so we cap it off at 2k each.
        # 2000 chars is still the limit for non-nitro users so it should be mostly fine.
        if len(after.content[2000:]) > 0:
            after.content = "Content is too large to fit in a single embed."
        if len(before.content[2000:]) > 0:
            before.content = "Content is too large to fit in a single embed."

        # If you send an empty message and then edit it (like when you upload pics), the before field cannot be empty.
        if len(before.content) == 0:
            before.content = "\u200b"

        embed = discord.Embed(
            title=f"**✍️ Edited Message in {after.channel.name}! ✍️**",
            description=f"**New Content:**\n{after.content}\n\n**Old Content:**\n{before.content}",
            colour=discord.Colour.orange(),
        )
        embed.set_author(
            name=f"{str(after.author)} ({after.author.id})",
            icon_url=after.author.display_avatar.url,
        )

        embed.add_field(name="Message ID:", value=f"{after.id}\n{after.jump_url}")
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(before.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if not message.guild:
            return

        if message.author.bot:
            return

        embed = discord.Embed(
            title=f"**❌ Deleted Message in {message.channel.name}! ❌**",
            description=f"**Content:**\n{message.content}",
            colour=discord.Colour.dark_red(),
        )
        embed.set_author(
            name=f"{str(message.author)} ({message.author.id})",
            icon_url=message.author.display_avatar.url,
        )

        embed = utils.embed.add_attachments_to_embed(embed, message)

        embed.add_field(name="Message ID:", value=message.id)
        embed.timestamp = discord.utils.utcnow()

        # As far as i can tell, the maximum message possible with 4k chars + 10 attachments + 1 sticker
        # just barely fits in one embed, the limit for embeds are 6k chars total.
        # So we might wanna keep watching this in case of errors.
        if logs := self.bot.get_channel(
            GetIDFunctions.get_logchannel(message.guild.id)
        ):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]) -> None:
        embed = discord.Embed(
            title=f"**❌ Bulk message deletion in {messages[0].channel.name}! ❌**",
            description=f"{len(messages)} messages were deleted!",
            colour=discord.Colour.dark_red(),
        )
        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()

        # Creates the file with the deleted messages.
        message_list = [
            f"{str(message.author)} said at {message.created_at.replace(microsecond=0)} UTC: \n"
            f"{message.content}\n\n"
            for message in messages
        ]

        buffer = StringIO("".join(message_list))
        f = discord.File(buffer, filename="deleted_messages.txt")

        if logs := self.bot.get_channel(
            GetIDFunctions.get_logchannel(messages[0].guild.id)
        ):
            # The file could theoratically be too large to send, the limit is 8MB.
            # Realistically we will never, ever hit this.
            try:
                await logs.send(embed=embed, file=f)
            except discord.HTTPException:
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_remove(
        self, reaction: discord.Reaction, user: discord.User
    ) -> None:
        if not reaction.message.guild:
            return

        if user.bot:
            return

        # TODO: Add support for super reactions when discord.py supports it.

        emoji_id = "Default" if isinstance(reaction.emoji, str) else reaction.emoji.id

        embed = discord.Embed(
            title="**👎 Reaction removed! 👎**",
            description=f"Emoji: {reaction.emoji} ({emoji_id})\n"
            f"Reaction Count: {reaction.count + 1} -> {reaction.count}\nMessage: {reaction.message.jump_url}",
            colour=discord.Colour.dark_orange(),
        )
        embed.set_author(
            name=f"{str(user)} ({user.id})", icon_url=user.display_avatar.url
        )
        embed.set_thumbnail(
            url=None if isinstance(reaction.emoji, str) else reaction.emoji.url
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(
            GetIDFunctions.get_logchannel(reaction.message.guild.id)
        ):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None:
        embed = discord.Embed(
            title="**🚫 New ban! 🚫**",
            description=f"{str(user)} has been banned from this server!",
            colour=discord.Colour.dark_red(),
        )
        embed.set_author(
            name=f"{str(user)} ({user.id})", icon_url=user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        embed = discord.Embed(
            title="**🔓 New unban! 🔓**",
            description=f"{str(user)} has been unbanned from this server!",
            colour=discord.Colour.green(),
        )
        embed.set_author(
            name=f"{str(user)} ({user.id})", icon_url=user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(
        self, before: discord.Guild, after: discord.Guild
    ) -> None:
        if before.name != after.name:
            embed = discord.Embed(
                title="🏠 Server name updated! 🏠",
                description=f"Old name: {before.name}\nNew name: {after.name}",
                colour=discord.Colour.dark_grey(),
            )
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(after.id)):
                await logs.send(embed=embed)

        if before.icon != after.icon:
            embed = discord.Embed(
                title="**📷 Server icon changed 📷**",
                description="New icon below:",
                colour=discord.Colour.dark_gray(),
            )
            if before.icon:
                embed.set_thumbnail(url=before.icon.url)

            if after.icon:
                embed.set_image(url=after.icon.url)
            else:
                embed.add_field(
                    name="Server icon has been deleted.", value="\u200b", inline=False
                )

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(after.id)):
                await logs.send(embed=embed)

        if before.banner != after.banner:
            embed = discord.Embed(
                title="**📷 Server banner changed 📷**",
                description="New banner below:",
                colour=discord.Colour.dark_gray(),
            )
            if before.banner:
                embed.set_thumbnail(url=before.banner.url)

            if after.banner:
                embed.set_image(url=after.banner.url)
            else:
                embed.add_field(
                    name="Server banner has been deleted.", value="\u200b", inline=False
                )

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(after.id)):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        embed = discord.Embed(
            title="📜 New channel created! 📜",
            description=f"Name: #{channel.name}\nCategory: {channel.category}",
            colour=discord.Color.green(),
        )
        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(
            GetIDFunctions.get_logchannel(channel.guild.id)
        ):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        embed = discord.Embed(
            title="❌ Channel deleted! ❌",
            description=f"Name: #{channel.name}\nCategory: {channel.category}",
            colour=discord.Colour.red(),
        )
        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(
            GetIDFunctions.get_logchannel(channel.guild.id)
        ):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        # We just log those two here, since the other stuff doesnt make much sense to log, imo.
        # position would get very spammy and permissions are hard to display in an embed.
        if before.name != after.name:
            embed = discord.Embed(
                title="📜 Channel name updated! 📜",
                description=f"Old name: #{before.name}\nNew name: #{after.name}",
                colour=discord.Colour.dark_grey(),
            )
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

        if before.category != after.category:
            embed = discord.Embed(
                title=f"📜 Channel category updated for {after.name}! 📜",
                description=f"Old category: {before.category}\nNew category: #{after.category}",
                colour=discord.Colour.dark_grey(),
            )
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild: discord.Guild,
        before: Sequence[discord.Emoji],
        after: Sequence[discord.Emoji],
    ) -> None:
        if len(before) > len(after):
            old_emoji = next(emoji for emoji in before if emoji not in after)

            embed = discord.Embed(
                title="😭 Emoji deleted! 😭",
                description=f"Name: {old_emoji.name}\nID: {old_emoji.id}",
                colour=discord.Colour.red(),
            )
            embed.set_image(url=old_emoji.url)
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
                await logs.send(embed=embed)

        if len(before) < len(after):
            new_emoji = next(emoji for emoji in after if emoji not in before)

            embed = discord.Embed(
                title="😀 New emoji created! 😀",
                description=f"Name: {new_emoji.name}\nID: {new_emoji.id}",
                colour=discord.Colour.yellow(),
            )
            embed.set_image(url=new_emoji.url)
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_stickers_update(
        self,
        guild: discord.Guild,
        before: Sequence[discord.Sticker],
        after: Sequence[discord.Sticker],
    ) -> None:
        if len(before) > len(after):
            old_sticker = next(sticker for sticker in before if sticker not in after)

            embed = discord.Embed(
                title="😭 Sticker deleted! 😭",
                description=f"Name: {old_sticker.name}\nID: {old_sticker.id}",
                colour=discord.Colour.red(),
            )
            embed.set_image(url=old_sticker.url)
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
                await logs.send(embed=embed)

        if len(before) < len(after):
            new_sticker = next(sticker for sticker in after if sticker not in before)

            embed = discord.Embed(
                title="😀 New sticker created! 😀",
                description=f"Name: {new_sticker.name}\nID: {new_sticker.id}",
                colour=discord.Colour.yellow(),
            )
            embed.set_image(url=new_sticker.url)
            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(guild.id)):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        invite_uses = invite.max_uses if invite.max_uses > 0 else "Unlimited"
        expiration = (
            discord.utils.format_dt(invite.expires_at) if invite.expires_at else "Never"
        )

        embed = discord.Embed(
            title="✉️ New invite created! ✉️",
            description=f"From: {str(invite.inviter)}\nDestination: {invite.channel.mention}\n"
            f"Uses: {invite_uses}\nExpiration: {expiration}",
            colour=discord.Colour.green(),
        )
        embed.set_author(
            name=f"{str(invite.inviter)} ({invite.inviter.id})",
            icon_url=invite.inviter.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(invite.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        embed = discord.Embed(
            title="✨ New role created! ✨",
            description=f"Name: {role.name}\nID: {role.id}",
            colour=role.colour,
        )
        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(role.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        embed = discord.Embed(
            title="❌ Role deleted! ❌",
            description=f"Name: {role.name}\nID: {role.id}",
            colour=role.colour,
        )
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)

        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(role.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(
        self, before: discord.Role, after: discord.Role
    ) -> None:
        if before.name != after.name:
            embed = discord.Embed(
                title="🔧 Role name updated! 🔧",
                description=f"Old name: {before.name}\nNew name: {after.name}",
                colour=after.colour,
            )
            if after.icon:
                embed.set_thumbnail(url=after.icon.url)

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

        if before.colour != after.colour:
            embed = discord.Embed(
                title=f"🔧 {after.name} colour updated! 🔧",
                description=f"Old colour: {before.colour}\nNew colour: {after.colour}",
                colour=after.colour,
            )
            if after.icon:
                embed.set_thumbnail(url=after.icon.url)

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

        if before.icon != after.icon:
            embed = discord.Embed(
                title=f"🔧 {after.name} icon updated! 🔧",
                description="New icon below:",
                colour=after.colour,
            )
            if before.icon:
                embed.set_thumbnail(url=before.icon.url)

            if after.icon:
                embed.set_image(url=after.icon.url)
            else:
                embed.add_field(
                    name="Role icon has been deleted.", value="\u200b", inline=False
                )

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

        if before.unicode_emoji != after.unicode_emoji:
            embed = discord.Embed(
                title=f"🔧 {after.name} emoji updated! 🔧",
                description=f"Old emoji: {before.unicode_emoji}\nNew emoji: {after.unicode_emoji}",
                colour=after.colour,
            )

            embed.set_author(
                name=f"{str(self.bot.user)} ({self.bot.user.id})",
                icon_url=self.bot.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        embed = discord.Embed(
            title="🧵 New thread created! 🧵",
            description=f"Name: {thread.name}\nID: {thread.id}\n"
            f"Channel: {thread.parent.mention}\nCreator: {str(thread.owner)}\n"
            f"Archives after {thread.auto_archive_duration} minutes of inactivity.",
            colour=discord.Colour.blue(),
        )

        embed.set_author(
            name=f"{str(thread.owner)} ({thread.owner.id})",
            icon_url=thread.owner.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(thread.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_delete(self, thread: discord.Thread) -> None:
        embed = discord.Embed(
            title="❌ Thread deleted! ❌",
            description=f"Name: {thread.name}\nID: {thread.id}\n"
            f"Channel: {thread.parent.mention}\nCreator: {str(thread.owner)}",
            colour=discord.Colour.red(),
        )
        embed.set_author(
            name=f"{str(thread.owner)} ({thread.owner.id})",
            icon_url=thread.owner.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(thread.guild.id)):
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_update(
        self, before: discord.Thread, after: discord.Thread
    ) -> None:
        # This event doesnt seem to fire if the thread gets un-archived,
        # so we only log it when a thread gets archived, and not the other way around.
        if not before.archived and after.archived:
            embed = discord.Embed(
                title="🗃️ Thread archived! 🗃️",
                description=f"Name: {before.name}\nID: {before.id}\n"
                f"Channel: {before.parent.mention}\nCreator: {str(before.owner)}",
                colour=discord.Colour.dark_orange(),
            )

            embed.set_author(
                name=f"{str(before.owner)} ({before.owner.id})",
                icon_url=before.owner.display_avatar.url,
            )

            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(before.guild.id)
            ):
                await logs.send(embed=embed)

        if before.name != after.name:
            embed = discord.Embed(
                title="🧵 Thread name updated! 🧵",
                description=f"Old name: {before.name}\nNew name: {after.name}\n\n"
                f"Channel: {before.parent.mention}",
                colour=discord.Colour.purple(),
            )

            embed.set_author(
                name=f"{str(after.owner)} ({after.owner.id})",
                icon_url=after.owner.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()
            if logs := self.bot.get_channel(
                GetIDFunctions.get_logchannel(after.guild.id)
            ):
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent) -> None:
        end_time = discord.utils.format_dt(event.end_time) if event.end_time else "None"

        embed = discord.Embed(
            title="🎇 New event created! 🎇",
            description=f"Name: {event.name}\nID: {event.id}\n"
            f"Description: {event.description}\n\nLocation: {event.location}\n"
            f"Start time: {discord.utils.format_dt(event.start_time)}\nEnd time: {end_time}",
            colour=discord.Colour.og_blurple(),
        )

        if event.cover_image:
            embed.set_image(url=event.cover_image.url)

        embed.set_author(
            name=f"{str(self.bot.user)} ({self.bot.user.id})",
            icon_url=self.bot.user.display_avatar.url,
        )

        embed.timestamp = discord.utils.utcnow()
        if logs := self.bot.get_channel(GetIDFunctions.get_logchannel(event.guild.id)):
            await logs.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Logging(bot))
    print("Logging cog loaded")
