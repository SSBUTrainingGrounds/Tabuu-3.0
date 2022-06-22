import os

import discord
from discord.ext import commands

from utils.ids import GuildIDs


class Owner(commands.Cog):
    """Contains commands that can only be used by the owner
    that relate to basic functionality of the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sync", "syncommands"])
    @commands.is_owner()
    async def synccommands(
        self, ctx: commands.Context, target_guild: discord.Guild = None
    ):
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
    async def reloadcogs(self, ctx: commands.Context, *, cogs: str = None):
        """Command for manually reloading all cogs.
        Can only be used by the owner of the bot.
        """
        if cogs is None:
            # If the user doesnt specify which cog to reload, we relaod them all.
            # Embeds can have up to 25 fields, we are at 22 cogs currently.
            # Need a different solution when we go over that.
            embed = discord.Embed(
                title="Reloading cogs...", colour=discord.Colour.blue()
            )
            for filename in os.listdir(r"./cogs"):
                if filename.endswith(".py"):
                    try:
                        await self.bot.unload_extension(f"cogs.{filename[:-3]}")
                        await self.bot.load_extension(f"cogs.{filename[:-3]}")
                        embed.add_field(
                            name=f"✅ Successfully reloaded {filename[:-3]} ✅",
                            value="Ready to go.",
                            inline=False,
                        )
                    except Exception as exc:
                        embed.add_field(
                            name=f"❌ FAILED TO RELOAD {filename[:-3]} ❌",
                            value=exc,
                            inline=False,
                        )
        else:
            embed = discord.Embed(
                title="Reloading cog(s)...", colour=discord.Colour.blue()
            )
            for cog in cogs.split(","):
                cog = cog.strip()
                try:
                    await self.bot.unload_extension(f"cogs.{cog}")
                    await self.bot.load_extension(f"cogs.{cog}")
                    embed.add_field(
                        name=f"✅ Successfully reloaded {cog} ✅",
                        value="Ready to go.",
                        inline=False,
                    )
                except Exception as exc:
                    embed.add_field(
                        name=f"❌ FAILED TO RELOAD {cog} ❌",
                        value=exc,
                        inline=False,
                    )

        await ctx.send(embed=embed)

    @reloadcogs.error
    async def reloadcogs_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("You are not the owner of this bot!")
        else:
            raise error

    @synccommands.error
    async def synccommands_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("You are not the owner of this bot!")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Owner(bot))
    print("Owner cog loaded")
