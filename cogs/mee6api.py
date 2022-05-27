from math import ceil

import discord
from discord import app_commands
from discord.ext import commands, tasks
from mee6_py_api import API

from utils.ids import GuildIDs, GuildNames, TGLevelRoleIDs

# this is purposefully not made into GuildIDs.TRAINING_GROUNDS.
# even in testing i want the TG leaderboard, not the leaderboard of my testing server. change it if you want to.
mee6API = API(739299507795132486)


class Mee6api(commands.Cog):
    """This class calls the Mee6 API, gets the Level of a User and assigns the Level Role to them.
    Both manually via a Command and automatically via a Task.
    """

    def __init__(self, bot):
        self.bot = bot

        self.update_roles.start()

    def cog_unload(self):
        self.update_roles.cancel()

    async def update_level_role(
        self, member: discord.Member, level: int, guild: discord.Guild
    ) -> discord.Role:
        """Assigns you a new role depending on your level and removes all of the other ones.
        Returns the new role.
        """
        rolegiven = None

        defaultrole = discord.utils.get(guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)
        level10 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_10_ROLE)
        level25 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_25_ROLE)
        level50 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_50_ROLE)
        level75 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_75_ROLE)
        level100 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_100_ROLE)

        levelroles = [defaultrole, level10, level25, level50, level75, level100]

        async def assign_level_role(assign_role: discord.Role) -> discord.Role:
            """Removes every other level role and assigns the correct one."""

            roles_to_remove = [role for role in levelroles if role is not assign_role]
            await member.remove_roles(*roles_to_remove)
            await member.add_roles(assign_role)
            return assign_role

        if level >= 100:
            if level100 not in member.roles:
                rolegiven = await assign_level_role(level100)

        elif level >= 75:
            if level75 not in member.roles:
                rolegiven = await assign_level_role(level75)

        elif level >= 50:
            if level50 not in member.roles:
                rolegiven = await assign_level_role(level50)

        elif level >= 25:
            if level25 not in member.roles:
                rolegiven = await assign_level_role(level25)

        elif level >= 10:
            if level10 not in member.roles:
                rolegiven = await assign_level_role(level10)

        return rolegiven

    @commands.hybrid_command(
        aliases=["updatelvl", "updaterank"], cooldown_after_parsing=True
    )
    @commands.guild_only()
    @commands.cooldown(1, 300, commands.BucketType.user)
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(member="The member you want to update the level role of.")
    async def updatelevel(self, ctx, member: discord.Member = None):
        """Updates your Level Role manually.
        Can also be used on the behalf of other users.
        """
        if ctx.guild.id != GuildIDs.TRAINING_GROUNDS:
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
            ctx.command.reset_cooldown(ctx)
            return

        if member is None:
            member = ctx.author

        if member.bot:
            await ctx.send("Please do not use this command on bots.")
            ctx.command.reset_cooldown(ctx)
            return

        # Sometimes the API can take a while to respond.
        botmessage = await ctx.send("Please wait a few seconds...")

        userlevel = await mee6API.levels.get_user_level(member.id, dont_use_cache=True)

        rolegiven = await self.update_level_role(member, userlevel, ctx.guild)

        if rolegiven is None:
            await botmessage.edit(
                content=f"{member.mention}, you are Level {userlevel}, so no new role for you."
            )
        else:
            await botmessage.edit(
                content=f"{member.mention}, you are Level {userlevel}, "
                f"and thus I have given you the {rolegiven} role."
            )

    @updatelevel.error
    async def updatelevel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"{ctx.author.mention}, you are on cooldown for another "
                f"{round((error.retry_after)/60)} minutes to use this command."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention a valid member, or leave it blank.")
        elif isinstance(
            error, (commands.CommandInvokeError, commands.HybridCommandError)
        ):
            await ctx.send(
                "Something went wrong! Either the API is down or the user was not in the leaderboard yet. "
                "Please try again later."
            )
        else:
            raise error

    @tasks.loop(hours=23)
    async def update_roles(self):
        """Updates the Level Roles of every User in the Server automatically, every 23 hours.
        Pretty much the same as the Command above, with a few minor tweaks.
        Right now we have 4000 Members and this takes around 1:10 Minutes.
        We'll see how this scales in the future.
        """

        logger = self.bot.get_logger("bot.level")
        logger.info("Starting to update level roles...")

        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        all_guild_member_ids = [guild_member.id for guild_member in guild.members]

        # Gets the correct amount of pages.
        page_number = ceil(len(guild.members) / 100)
        for i in range(page_number):
            leaderboard_page = await mee6API.levels.get_leaderboard_page(i)
            for user in leaderboard_page["players"]:
                # Need to fetch the member, since get_member is unreliable.
                # We only do this for members in the server and above level 10 though,
                # otherwise this would take ages.
                if int(user["id"]) in all_guild_member_ids and user["level"] >= 10:
                    member = await guild.fetch_member(user["id"])
                    await self.update_level_role(member, user["level"], guild)

        logger.info("Successfully updated level roles!")

    @update_roles.before_loop
    async def before_update_roles(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Mee6api(bot))
    print("Mee6api cog loaded")
