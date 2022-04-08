import json
from datetime import datetime, timezone

import aiosqlite
import discord
from discord.ext import commands

import utils.check
import utils.embed
from utils.ids import TGChannelIDs


class Starboard(commands.Cog):
    """
    Contains the Starboard commands and listeners.
    Currently we only use this for our Charity Events.
    """

    def __init__(self, bot):
        self.bot = bot

    starboard_channel = TGChannelIDs.STARBOARD_CHANNEL
    listening_channels = TGChannelIDs.STARBOARD_LISTENING_CHANNELS

    async def update_starboard_message(
        self, reaction: discord.Reaction, message_id: int
    ):
        """
        Updates the starboard message with the new value for the reaction count
        whenever a reaction is removed or added.
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

    @commands.command()
    @utils.check.is_moderator()
    async def starboardemoji(self, ctx, emoji: str):
        """
        Sets the Starboard Emoji.
        The bot does need access to this Emoji.
        """
        try:
            await ctx.message.add_reaction(emoji)
        except discord.HTTPException:
            await ctx.send("Please enter a valid emoji.")
            return

        with open(r"./json/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["emoji"] = str(emoji)

        with open(r"./json/starboard.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"Changed the emoji to: `{str(emoji)}`")

    @commands.command()
    @utils.check.is_moderator()
    async def starboardthreshold(self, ctx, i: int):
        """
        Changes the threshold of reactions needed for the bot to post the message to the starboard channel.
        """
        if i < 1:
            await ctx.send("Please input a valid integer.")
            return

        with open(r"./json/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["threshold"] = i

        with open(r"./json/starboard.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"Changed the threshold to: `{i}`")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # the listener for reactions for the starboard.
        # first we check if the reaction happened in the right channel.
        if payload.channel_id not in self.listening_channels:
            return

        with open(r"./json/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # these prevent error messages in my console if the setup wasnt done yet.
        if "emoji" not in data:
            data["emoji"] = "placeholder"

        if "threshold" not in data:
            data["threshold"] = 100

        if str(payload.emoji) != data["emoji"]:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # dont want to update any old messages, 1 week seems fine
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

                # just editing the number on already existing messages
                if len(matching_entry) != 0:
                    await self.update_starboard_message(reaction, matching_entry[0][0])
                    return

                # if it doesnt already exist, it creates a new message
                star_channel = await self.bot.fetch_channel(self.starboard_channel)

                # again dont want error messages,
                # so if the content is invalid it gets replaced by a whitespace character
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
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # if the amount of reactions to a starboard message decrease,
        # we also wanna update the message then
        if payload.channel_id not in self.listening_channels:
            return

        with open(r"./json/starboard.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # these prevent error messages in my console if the setup wasnt done yet.
        if "emoji" not in data:
            data["emoji"] = "placeholder"

        if "threshold" not in data:
            data["threshold"] = 100

        if str(payload.emoji) != data["emoji"]:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # dont want to update any old messages, 1 week seems fine
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

                # just editing the number on already existing messages
                if len(matching_entry) != 0:
                    await self.update_starboard_message(reaction, matching_entry[0][0])
                    return

    @starboardemoji.error
    async def starboardemoji_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please input the emoji you want the starboard to respond to."
            )
        else:
            raise error

    @starboardthreshold.error
    async def starboardthreshold_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please input the number you want the new threshold to be for the starboard."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please input an integer!")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Starboard(bot))
    print("Starboard cog loaded")
