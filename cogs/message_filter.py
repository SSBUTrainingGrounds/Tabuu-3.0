import re
import string

import discord
from discord.ext import commands

from cogs.warn import Warn
from utils.ids import AdminVars, GuildIDs, TGChannelIDs, TGRoleIDs

with open(r"./files/badwords.txt", encoding="utf-8") as file:
    file = file.read().split()


class MessageFilter(commands.Cog):
    """Contains the message filters.
    One is the very simple check for invite links,
    the other is the bad word filtering using regex,
    the latter then warns the user automatically.

    This really is not used anymore, since Discord rolled out an update with
    the possibility to blacklist certain words.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Dont want any recursive stuff to happen,
        # so any messages from tabuu 3.0 wont get checked, just in case.
        if message.author == self.bot.user:
            return

        # Wont check dm's either.
        if not message.guild:
            return

        if message.guild.id not in [g.id for g in GuildIDs.ADMIN_GUILDS]:
            return

        # Searches for invite links, no need for regex as there are a million ways to disguise invite links anyways.
        # This is just a basic filter which is not designed to stop 100% of invite links coming in
        if (
            (
                "discord.gg" in message.content
                or "discordapp.com/invite" in message.content
            )
            and message.guild.id == GuildIDs.TRAINING_GROUNDS
            and isinstance(message.author, discord.Member)
        ):
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            mod_role = discord.utils.get(guild.roles, id=TGRoleIDs.MOD_ROLE)
            promoter_role = discord.utils.get(guild.roles, id=TGRoleIDs.PROMOTER_ROLE)
            if (
                mod_role not in message.author.roles
                and promoter_role not in message.author.roles
                and message.channel.id not in TGChannelIDs.INVITE_LINK_WHITELIST
            ):
                await message.delete()
                await message.channel.send(
                    f"Please don't send invite links here {message.author.mention}"
                )

        # Searches for bad words using regex.
        # string.digits+string.whitespace+string.punctuation
        # add the above for very strict ruling, might end up with false positives.
        separators = ()
        # Add/remove these depending on strictness, do +'/'+'-' and so on for urls in the future maybe.
        excluded = string.ascii_letters + string.digits

        # Checks if a message contains one of the words in the badwords.txt file.
        for word in file:
            formatted_word = f"[{separators}]*".join(list(word))
            regex_true = re.compile(rf"{formatted_word}", re.IGNORECASE)
            regex_false = re.compile(
                rf"([{excluded}]+{word})|({word}[{excluded}]+)", re.IGNORECASE
            )

            # Checks if a word matches, and then double checks again.
            if (
                regex_true.search(message.content) is not None
                and regex_false.search(message.content) is None
            ):
                # Adds the warning.
                reason = (
                    "Automatic warning for using a blacklisted word:\n"
                    + message.content
                )

                if len(reason[1000:]) > 0:
                    reason = f"{reason[:997]}..."

                await Warn.add_warn(self, message.guild.me, message.author, reason)
                await message.channel.send(
                    f"{message.author.mention} has been automatically warned for using a blacklisted word!"
                )

                try:
                    await message.delete()
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.autowarn")
                    logger.warning(
                        f"Tried to delete a message for containing a blacklisted word, but it failed: {exc}"
                    )

                try:
                    await message.author.send(
                        f"You have been automatically warned in the {message.guild.name} Server "
                        "for sending a message containing a blacklisted word.\n"
                        f"{AdminVars.APPEAL_MESSAGE}"
                    )
                except discord.HTTPException as exc:
                    logger = self.bot.get_logger("bot.autowarn")
                    logger.warning(
                        f"Tried to message automatic warn reason to {str(message.author)}, but it failed: {exc}"
                    )

                # This function here checks the warn count on each user
                # and if it reaches a threshold it will mute/kick/ban the user.
                await Warn.check_warn_count(
                    self, message.guild, message.channel, message.author
                )

                break


async def setup(bot) -> None:
    await bot.add_cog(MessageFilter(bot))
    print("Message Filter cog loaded")
