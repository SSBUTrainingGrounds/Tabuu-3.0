import os

import discord
from discord.ext import commands

from utils.ids import GuildIDs


class Owner(commands.Cog):
    """Contains commands that can only be used by the owner
    that relate to basic functionality of the bot.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["sync", "syncommands"])
    @commands.is_owner()
    async def synccommands(
        self, ctx: commands.Context, target_guild: discord.Guild = None
    ) -> None:
        """Syncs the locally added application commands to the discord client."""

        initial_message = await ctx.send("Syncing Commands...")

        if target_guild is None:
            guilds = 0
            total_commands = 0
            for guild in GuildIDs.ALL_GUILDS:
                try:
                    cmds = await self.bot.tree.sync(guild=guild)
                    total_commands += len(cmds)
                    guilds += 1
                except discord.errors.Forbidden:
                    pass

            await initial_message.edit(
                content=f"Successfully synced {total_commands} total Application Command(s) to {guilds} Server(s)."
            )
        else:
            try:
                cmds = await self.bot.tree.sync(guild=target_guild)

                await initial_message.edit(
                    content=f"Successfully synced {len(cmds)} Application Command(s) to the {target_guild.name} Server."
                )
            except discord.errors.Forbidden as exc:
                await initial_message.edit(
                    content=f"Could not sync Application Command(s) on the {target_guild.name} Server: {exc}"
                )

    @commands.command(aliases=["reloadcog"])
    @commands.is_owner()
    async def reloadcogs(self, ctx: commands.Context, *, cogs: str = None) -> None:
        """Command for manually reloading all cogs.
        Can only be used by the owner of the bot.
        """
        message = ""
        if cogs is None:
            for filename in os.listdir(r"./cogs"):
                if filename.endswith(".py"):
                    cog = filename[:-3]
                    try:
                        await self.bot.unload_extension(f"cogs.{filename[:-3]}")
                        await self.bot.load_extension(f"cogs.{filename[:-3]}")
                        message += f"✅ Successfully reloaded **{cog}**\n"
                    except Exception as exc:
                        message += f"❌ FAILED TO RELOAD **{cog}**\n{exc}\n"
        else:
            for cog in cogs.split(","):
                cog = cog.strip()
                try:
                    await self.bot.unload_extension(f"cogs.{cog}")
                    await self.bot.load_extension(f"cogs.{cog}")
                    message += f"✅ Successfully reloaded **{cog}**\n"
                except Exception as exc:
                    message += f"❌ FAILED TO RELOAD **{cog}**\n{exc}\n"

        embed = discord.Embed(
            title="Reloading cog(s)...",
            colour=discord.Colour.blue(),
            description=message,
        )
        await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
    print("Owner cog loaded")
