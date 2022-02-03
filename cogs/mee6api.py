import discord
from discord.ext import commands, tasks
from mee6_py_api import API
from math import ceil
from utils.ids import GuildNames, GuildIDs, TGLevelRoleIDs
import utils.logger

# this is purposefully not made into GuildIDs.TRAINING_GROUNDS.
# even in testing i want the TG leaderboard, not the leaderboard of my testing server. change it if you want to.
mee6API = API(739299507795132486)


class Mee6api(commands.Cog):
    """
    This class calls the Mee6 API, gets the Level of a User and assigns the Level Role to them.
    Both manually via a Command and automatically via a Task.
    """

    def __init__(self, bot):
        self.bot = bot

        self.update_roles.start()

    def cog_unload(self):
        self.update_roles.cancel()

    @commands.command(aliases=["updatelvl", "updaterank"], cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def updatelevel(self, ctx, member: discord.Member = None):
        """
        Updates your Level Role manually.
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

        # sometimes the API can take a while to respond.
        botmessage = await ctx.send("Please wait a few seconds...")

        userlevel = await mee6API.levels.get_user_level(member.id, dont_use_cache=True)

        defaultrole = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)
        level10 = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.LEVEL_10_ROLE)
        level25 = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.LEVEL_25_ROLE)
        level50 = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.LEVEL_50_ROLE)
        level75 = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.LEVEL_75_ROLE)
        level100 = discord.utils.get(ctx.guild.roles, id=TGLevelRoleIDs.LEVEL_100_ROLE)

        levelroles = [defaultrole, level10, level25, level50, level75, level100]

        rolegiven = None

        if userlevel > 9 and userlevel < 25:
            if level10 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level10)
                rolegiven = level10

        elif userlevel > 24 and userlevel < 50:
            if level25 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level25)
                rolegiven = level25

        elif userlevel > 49 and userlevel < 75:
            if level50 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level50)
                rolegiven = level50

        elif userlevel > 74 and userlevel < 100:
            if level75 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level75)
                rolegiven = level75

        elif userlevel > 99:
            if level100 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level100)
                rolegiven = level100

        if rolegiven is None:
            await botmessage.edit(
                content=f"{member.mention}, you are Level {userlevel}, so no new role for you."
            )
        else:
            await botmessage.edit(
                content=f"{member.mention}, you are Level {userlevel}, and thus I have given you the {rolegiven} role."
            )

    # generic error message
    @updatelevel.error
    async def updatelevel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                f"This command can only be used in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention a valid member, or leave it blank.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "Something went wrong! Either the API is down or the user was not in the leaderboard yet. Please try again later."
            )
        else:
            raise error

    @tasks.loop(hours=23)
    async def update_roles(self):
        """
        Updates the Level Roles of every User in the Server automatically, every 23 hours.
        Pretty much the same as the Command above, with a few minor tweaks.
        Right now we have 4000 Members and this takes around 1:10 Minutes.
        We'll see how this scales in the future.
        """

        logger = utils.logger.get_logger("bot.level")
        logger.info("Starting to update level roles...")

        guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        defaultrole = discord.utils.get(guild.roles, id=TGLevelRoleIDs.RECRUIT_ROLE)
        level10 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_10_ROLE)
        level25 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_25_ROLE)
        level50 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_50_ROLE)
        level75 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_75_ROLE)
        level100 = discord.utils.get(guild.roles, id=TGLevelRoleIDs.LEVEL_100_ROLE)

        levelroles = [defaultrole, level10, level25, level50, level75, level100]

        # gets the correct amount of pages
        pageNumber = ceil(len(guild.members) / 100)
        for i in range(pageNumber):
            leaderboard_page = await mee6API.levels.get_leaderboard_page(i)
            for user in leaderboard_page["players"]:
                # checks if the user even is in the guild
                if int(user["id"]) in [guildMember.id for guildMember in guild.members]:

                    # need to fetch the member, since get_member is unreliable.
                    # even with member intents it kind of fails sometimes since not all members are cached
                    # this fetching step can take some time depending on guild size
                    # we also just can remove all level roles since this code only triggers if you rank up. after that add the new role
                    if user["level"] > 9 and user["level"] < 25:
                        member = await guild.fetch_member(user["id"])
                        if level10 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level10)

                    elif user["level"] > 24 and user["level"] < 50:
                        member = await guild.fetch_member(user["id"])
                        if level25 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level25)

                    elif user["level"] > 49 and user["level"] < 75:
                        member = await guild.fetch_member(user["id"])
                        if level50 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level50)

                    elif user["level"] > 74 and user["level"] < 100:
                        member = await guild.fetch_member(user["id"])
                        if level75 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level75)

                    elif user["level"] > 99:
                        member = await guild.fetch_member(user["id"])
                        if level100 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level100)

        logger.info("Successfully updated level roles!")

    @update_roles.before_loop
    async def before_update_roles(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Mee6api(bot))
    print("Mee6api cog loaded")
