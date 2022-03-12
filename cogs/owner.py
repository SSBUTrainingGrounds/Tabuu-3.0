import discord
from discord.ext import commands
import os
from utils.ids import GuildIDs


class Owner(commands.Cog):
    """
    Contains commands that can only be used by the owner
    that relate to basic functionality of the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sync", "syncommands"])
    @commands.is_owner()
    async def synccommands(self, ctx, target_guild: discord.Guild = None):
        """
        Syncs the locally added application commands to the discord client.
        """
        initial_message = await ctx.send("Syncing Commands...")

        if target_guild is None:
            guilds = 0
            for guild in GuildIDs.ALL_GUILDS:
                try:
                    cmds = await self.bot.tree.sync(guild=guild)
                    guilds += 1
                except discord.errors.Forbidden:
                    pass

            await initial_message.edit(
                content=f"Successfully synced {len(cmds)} Application Command(s) to {len(GuildIDs.ALL_GUILDS)} Server(s)."
            )
        else:
            try:
                cmds = await self.bot.tree.sync(guild=target_guild)

                await initial_message.edit(
                    content=f"Successfully synced {len(cmds)} Application Command(s) to the {target_guild.name} Server."
                )
            except discord.errors.Forbidden:
                await initial_message.edit(
                    content=f"Could not sync Application Command(s) on the {target_guild.name} Server, due to Missing Permissions."
                )

    @commands.command(aliases=["reloadcog"])
    @commands.is_owner()
    async def reloadcogs(self, ctx, *, cogs: str = None):
        """
        Command for manually reloading all cogs, so i dont have to restart the bot for every change.
        Can only be used by the owner of the bot.
        """
        if cogs is None:
            # if the user doesnt specify which cog to reload, we relaod them all.
            # embeds can have up to 25 fields, we are at 21 cogs currently.
            # need a different solution when we go over that
            embed = discord.Embed(
                title="Reloading cogs...", colour=discord.Colour.blue()
            )
            for filename in os.listdir(r"./cogs"):
                if filename.endswith(".py"):
                    try:
                        self.bot.unload_extension(f"cogs.{filename[:-3]}")
                        self.bot.load_extension(f"cogs.{filename[:-3]}")
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
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Reloading cog...", colour=discord.Colour.blue()
            )
            for cog in cogs.split(","):
                cog = cog.strip()
                try:
                    self.bot.unload_extension(f"cogs.{cog}")
                    self.bot.load_extension(f"cogs.{cog}")
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

    # some error handling
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


def setup(bot):
    bot.add_cog(Owner(bot))
    print("Owner cog loaded")
