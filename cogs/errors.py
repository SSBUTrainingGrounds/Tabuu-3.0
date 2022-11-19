import aiosqlite
from discord.ext import commands
from stringmatch import Match


class Errors(commands.Cog):
    """Contains generic error handlers and other error related stuff for the bot.
    Command specific errors are handled in the file of the command itself.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger = self.bot.get_logger("bot.commands")
        logger.error(
            f"Command triggered an Error: {ctx.prefix}{ctx.invoked_with} "
            f"(invoked by {str(ctx.author)}) - Error message: {error}"
        )

        # If a command is not found, we search for the closest match.
        if isinstance(error, commands.CommandNotFound):
            command_list = [
                command.qualified_name for command in self.bot.walk_commands()
            ]

            async with aiosqlite.connect("./db/database.db") as db:
                all_macros = await db.execute_fetchall("""SELECT name FROM macros""")

            # Appending all macro names to the list to get those too.
            command_list.extend(m[0] for m in all_macros)

            if ctx.invoked_with in command_list:
                return

            match = Match(ignore_case=True, include_partial=True, latinise=True)
            if command_match := match.get_best_match(
                ctx.invoked_with, command_list, score=30
            ):
                await ctx.send(
                    "I could not find this command. "
                    f"Did you mean `{ctx.prefix}{command_match}`?\n"
                    f"Type `{ctx.prefix}help` for all available commands."
                )
            else:
                await ctx.send(
                    "I could not find this command.\n"
                    f"Type `{ctx.prefix}help` for all available commands."
                )

        # Just some generic messages for generic errors.
        # Note that there is no generic cooldown handler, because of the special matchmaking cooldowns.
        # Everything else that commonly shows up should be covered here.
        elif isinstance(
            error,
            (
                commands.MissingPermissions,
                commands.NotOwner,
                commands.MissingRole,
                commands.MissingAnyRole,
            ),
        ):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error,
            (
                commands.BotMissingPermissions,
                commands.BotMissingRole,
                commands.BotMissingAnyRole,
            ),
        ):
            await ctx.send("I don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"You are missing the required argument `{error.param.name}`."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                "I could not find this user. Make sure you have the right ID, or mention them."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                "I could not find this member. Make sure they are on this server and you have the right ID, or mention them."
            )
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                "I could not find this role. Make sure you have the right name or ID."
            )
        elif isinstance(error, (commands.ChannelNotFound, commands.ThreadNotFound)):
            await ctx.send(
                "I could not find this channel. Make sure you have the right name or ID."
            )
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send(
                "I could not find this message. Make sure you have the right ID."
            )
        elif isinstance(error, commands.EmojiNotFound):
            await ctx.send(
                "I could not find this emoji. Make sure you have the right name or ID."
            )
        elif isinstance(error, commands.PartialEmojiConversionFailure):
            await ctx.send(
                "I couldn't find information on this emoji! Make sure this is not a default emoji."
            )
        elif isinstance(error, commands.MissingRequiredAttachment):
            await ctx.send("You are missing the required attachment.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled.")


async def setup(bot) -> None:
    await bot.add_cog(Errors(bot))
    print("Errors cog loaded")
