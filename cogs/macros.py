import aiosqlite
import discord
from discord.ext import commands

import utils.check


class Macros(commands.Cog):
    """
    Contains the logic of adding/removing macros.
    As well as listening for them.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # listens for the macros
        async with aiosqlite.connect("./db/database.db") as db:
            macro_names = await db.execute_fetchall("""SELECT name FROM macros""")

            for name in macro_names:
                # it returns tuples, so we need the first (and only) entry
                name = name[0]
                if (
                    len(message.content.split()) == 1
                    and message.content == (f"{self.bot.command_prefix}{name}")
                    or message.content.startswith(f"{self.bot.command_prefix}{name} ")
                ):
                    matching_macro = await db.execute_fetchall(
                        """SELECT payload FROM macros WHERE name = :name""",
                        {"name": name},
                    )
                    payload = matching_macro[0][0]
                    await message.channel.send(payload)

                    self.bot.commands_ran += 1
                    await db.execute(
                        """UPDATE macros SET uses = uses + 1 WHERE name = :name""",
                        {"name": name},
                    )
                    await db.commit()

    @commands.command()
    @utils.check.is_moderator()
    async def createmacro(self, ctx, name: str, *, payload: str):
        """
        Creates a new macro with the desired name and payload and saves it in the database.
        """
        # converts them to only lower case
        name = name.lower()

        # every command registered
        command_list = [command.name for command in self.bot.commands]

        async with aiosqlite.connect("./db/database.db") as db:
            matching_macro = await db.execute_fetchall(
                """SELECT name FROM macros WHERE name = :name""", {"name": name}
            )

            # basic checks for invalid stuff
            if len(matching_macro) != 0:
                await ctx.send(
                    "This name was already taken. "
                    "If you want to update this macro please delete it first and then create it again."
                )
                return

            if name in command_list:
                await ctx.send(
                    "This name is already being used for a command! Please use a different one."
                )
                return

            if len(name[50:]) > 0:
                await ctx.send(
                    "The name of this macro is too long! Please try again with a shorter name."
                )
                return

            if len(payload[1500:]) > 0:
                await ctx.send(
                    "The output of this macro would be too big to send! Please try again with a shorter output."
                )
                return

            await db.execute(
                """INSERT INTO macros VALUES (:name, :payload, :uses, :author)""",
                {"name": name, "payload": payload, "uses": 0, "author": ctx.author.id},
            )

            await db.commit()

        await ctx.send(f"New macro `{name}` was created.\nOutput:\n`{payload}`")

    @commands.command()
    @utils.check.is_moderator()
    async def deletemacro(self, ctx, name: str):
        """
        Deletes a macro with the specified name from the database.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            macro_names = await db.execute_fetchall(
                """SELECT * FROM macros WHERE name = :name""", {"name": name}
            )

            # if the macro does not exist we want some kind of error message for the user
            if len(macro_names) == 0:
                await ctx.send(f"The macro `{name}` was not found. Please try again.")
                return

            await db.execute(
                """DELETE FROM macros WHERE name = :name""", {"name": name}
            )

            await db.commit()

        await ctx.send(f"Deleted macro `{name}`")

    @commands.command(aliases=["macros", "listmacros", "macrostats"])
    async def macro(self, ctx, *, macro: str = None):
        """
        Gives you detailed information about a macro,
        or lists every macro saved.
        """
        if macro is None:
            async with aiosqlite.connect("./db/database.db") as db:
                macro_list = await db.execute_fetchall("""SELECT name FROM macros""")

            # it returns a list of tuples,
            # so we need to extract them
            macro_names = [m[0] for m in macro_list]
            await ctx.send(
                "The registered macros are:\n"
                f"`{self.bot.command_prefix}{f', {self.bot.command_prefix}'.join(macro_names)}`"
            )
            return

        async with aiosqlite.connect("./db/database.db") as db:
            matching_macro = await db.execute_fetchall(
                """SELECT * FROM macros WHERE name = :name""", {"name": macro}
            )

        # if the macro does not exist we want some kind of error message for the user
        if len(matching_macro) == 0:
            await ctx.send(
                f"I could not find this macro. List all macros with `{self.bot.command_prefix}macros`."
            )
            return

        name, payload, uses, author_id = matching_macro[0]

        embed = discord.Embed(
            title="Macro info",
            color=0x007377,
            description=f"**Name:** {self.bot.command_prefix}{name}\n**Uses:** {uses}\n"
            f"**Author:**<@{author_id}>\n**Output:**\n{payload}\n",
        )

        await ctx.send(embed=embed)

    # the error handling for the commands above
    # fairly self-explanatory
    @createmacro.error
    async def createmacro_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You need to input the macro name and then the desired output."
            )
        elif isinstance(
            error, (commands.ExpectedClosingQuoteError, commands.UnexpectedQuoteError)
        ):
            await ctx.send(
                "Please do not create a macro with the `\"` letter. Use `'` instead."
            )
        else:
            raise error

    @deletemacro.error
    async def deletemacro_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input the macro you want to delete.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Macros(bot))
    print("Macros cog loaded")
