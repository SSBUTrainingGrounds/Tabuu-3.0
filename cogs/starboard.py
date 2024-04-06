import json
from datetime import datetime, timezone

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

import utils.check
import utils.embed
from utils.ids import GuildIDs, TGChannelIDs


class Starboard(commands.Cog):
    """Contains the Starboard commands and listeners.
    Currently we only use this for our Charity Events.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    starboard_channel = TGChannelIDs.STARBOARD_CHANNEL
    listening_channels = TGChannelIDs.STARBOARD_LISTENING_CHANNELS

    async def update_starboard_message(
        self, reaction: discord.Reaction, message_id: int
    ) -> None:
        """Updates the starboard message with the new value for the
        reaction count whenever a reaction is removed or added.
        """
        star_channel = await self.bot.fetch_channel(self.starboard_channel)

        try:
            edit_message = await star_channel.fetch_message(message_id)
            new_embed = edit_message.embeds[0]
            new_value = f"**{reaction.count} {str(reaction.emoji)}**"

            if new_embed.fields[0].value == new_value:
                return

            new_embed.set_field_at(0, name="\u200b", value=new_value)
            await edit_message.edit(embed=new_embed)
        except discord.errors.NotFound:
            return

    @commands.hybrid_group()
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def starboard(self, ctx: commands.Context) -> None:
        """Lists the group commands for the starboard."""
        if ctx.invoked_subcommand:
            return

        embed = discord.Embed(
            title="Available subcommands:",
            description=f"`{ctx.prefix}starboard emoji <emoji>`\n"
            f"`{ctx.prefix}starboard threshold <number>`\n",
            colour=self.bot.colour,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @starboard.command(name="emoji")
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.describe(emoji="The new emoji for the starboard.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def starboard_emoji(self, ctx: commands.Context, emoji: str) -> None:
        """Sets the Starboard Emoji.
        The bot does need access to this Emoji.
        """
        if ctx.interaction:
            await ctx.defer()
            message = await ctx.interaction.original_response()
        else:
            message = ctx.message

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            await ctx.send("Please enter a valid emoji.")
            return

        with open(r"./files/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["emoji"] = emoji

        with open(r"./files/starboard.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"Changed the emoji to: `{emoji}`")

    @starboard.command(name="threshold")
    @app_commands.guilds(*GuildIDs.ADMIN_GUILDS)
    @app_commands.describe(threshold="The new threshold for the starboard.")
    @app_commands.default_permissions(administrator=True)
    @utils.check.is_moderator()
    async def starboard_threshold(self, ctx: commands.Context, threshold: int) -> None:
        """Changes the Starboard threshold.
        This is the reactions needed for the bot to post the message to the starboard channel.
        """
        if threshold < 1:
            await ctx.send("Please input a valid integer.")
            return

        with open(r"./files/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["threshold"] = threshold

        with open(r"./files/starboard.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"Changed the threshold to: `{threshold}`")

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        # The listener for reactions for the starboard.
        # First we check if the reaction happened in the right channel.
        if payload.channel_id not in self.listening_channels:
            return

        with open(r"./files/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # These prevent error messages in my console if the setup wasnt done yet.
        if "emoji" not in data:
            data["emoji"] = "placeholder"

        if "threshold" not in data:
            data["threshold"] = 100

        if str(payload.emoji) != data["emoji"]:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Dont want to update any old messages, 1 week seems fine.
        if (datetime.now(timezone.utc) - message.created_at).days > 7:
            return

        for reaction in message.reactions:
            if (
                str(reaction.emoji) == data["emoji"]
                and reaction.count >= data["threshold"]
            ):
                async with aiosqlite.connect("./db/database.db") as db:
                    matching_entry = await db.execute_fetchall(
                        """SELECT starboard_id FROM starboardmessages WHERE :original_id = original_id""",
                        {"original_id": payload.message_id},
                    )

                # Just editing the number on already existing messages.
                if len(matching_entry) != 0:
                    await self.update_starboard_message(reaction, matching_entry[0][0])
                    return

                # If it doesnt already exist, it creates a new message.
                star_channel = await self.bot.fetch_channel(self.starboard_channel)

                # Again dont want error messages,
                # so if the content is invalid it gets replaced by a whitespace character.
                if len(message.content) == 0 or len(message.content[2000:]) > 0:
                    message.content = "\u200b"

                embed = discord.Embed(
                    description=message.content,
                    colour=message.author.colour,
                )
                embed.add_field(
                    name="\u200b",
                    value=f"**{reaction.count} {str(reaction.emoji)}**",
                )
                embed.add_field(
                    name="\u200b",
                    value=f"[Message Link]({message.jump_url})",
                )
                embed.set_author(
                    name=f"{str(message.author)} ({message.author.id})",
                    icon_url=message.author.display_avatar.url,
                )
                embed.set_footer(text=f"{message.id}")
                embed.timestamp = discord.utils.utcnow()

                embed = utils.embed.add_attachments_to_embed(embed, message)

                star_message = await star_channel.send(embed=embed)

                async with aiosqlite.connect("./db/database.db") as db:
                    await db.execute(
                        """INSERT INTO starboardmessages VALUES (:original_id, :starboard_id)""",
                        {
                            "original_id": message.id,
                            "starboard_id": star_message.id,
                        },
                    )
                    await db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        # If the amount of reactions to a starboard message decrease,
        # we also wanna update the message then.
        if payload.channel_id not in self.listening_channels:
            return

        with open(r"./files/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # These prevent error messages in my console if the setup wasnt done yet.
        if "emoji" not in data:
            data["emoji"] = "placeholder"

        if "threshold" not in data:
            data["threshold"] = 100

        if str(payload.emoji) != data["emoji"]:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Dont want to update any old messages, 1 week seems fine.
        if (datetime.now(timezone.utc) - message.created_at).days > 7:
            return

        for reaction in message.reactions:
            if (
                str(reaction.emoji) == data["emoji"]
                and reaction.count >= data["threshold"]
            ):
                async with aiosqlite.connect("./db/database.db") as db:
                    matching_entry = await db.execute_fetchall(
                        """SELECT starboard_id FROM starboardmessages WHERE :original_id = original_id""",
                        {"original_id": payload.message_id},
                    )

                # Just editing the number on already existing messages.
                if len(matching_entry) != 0:
                    await self.update_starboard_message(reaction, matching_entry[0][0])
                    return

    @starboard_threshold.error
    async def starboard_threshold_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please input an integer!")


async def setup(bot) -> None:
    await bot.add_cog(Starboard(bot))
    print("Starboard cog loaded")
