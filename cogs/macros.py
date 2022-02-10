import discord
from discord.ext import commands
import json


class Macros(commands.Cog):
    """
    Contains the logic of adding/removing macros.
    As well as listening for them.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # listens for the macros
        with open(r"./json/macros.json", "r") as f:
            macros = json.load(f)

        for name in macros:
            payload = macros[f"{name}"]
            if (
                len(message.content.split()) == 1
                and message.content == (f"%{name}")
                or message.content.startswith(f"%{name} ")
            ):
                await message.channel.send(payload)
                self.bot.commands_ran += 1

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createmacro(self, ctx, name, *, payload):
        """
        Creates a new macro with the desired name and payload and saves it in the json file.
        """
        with open(r"./json/macros.json", "r") as f:
            macros = json.load(f)

        # converts them to only lower case
        name = name.lower()

        # every command registered
        command_list = [command.name for command in self.bot.commands]

        # basic checks for invalid stuff
        if name in macros:
            await ctx.send(
                "This name was already taken. If you want to update this macro please delete it first and then create it again."
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

        macros[name] = payload

        with open(r"./json/macros.json", "w") as f:
            json.dump(macros, f, indent=4)

        await ctx.send(f"New macro `{name}` was created. \nOutput: `{payload}`")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletemacro(self, ctx, name):
        """
        Deletes a macro with the specified name from the json file.
        """
        with open(r"./json/macros.json", "r") as f:
            macros = json.load(f)

        # needs to check if the macro exists obviously
        if name in macros:
            del macros[f"{name}"]
        else:
            await ctx.send(f"The macro `{name}` was not found. Please try again.")
            return

        with open(r"./json/macros.json", "w") as f:
            json.dump(macros, f, indent=4)

        await ctx.send(f"Deleted macro `{name}`")

    @commands.command(aliases=["listmacro", "macros", "macro"])
    async def listmacros(self, ctx):
        """
        Lists every macro saved.
        """
        with open(r"./json/macros.json", "r") as f:
            macros = json.load(f)

        macro_list = []
        for name in macros:
            macro_list.append(name)

        await ctx.send(f"The registered macros are:\n`%{', %'.join(macro_list)}`")

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
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.send(
                "Please do not create a macro with the `\"` letter. Use `'` instead."
            )
        elif isinstance(error, commands.UnexpectedQuoteError):
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


def setup(bot):
    bot.add_cog(Macros(bot))
    print("Macros cog loaded")
