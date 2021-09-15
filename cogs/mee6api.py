import discord
from discord.ext import commands, tasks
from mee6_py_api import API
from discord.utils import get
from math import ceil

#
#this file here gets the mee6 level and assigns the matching role
#

mee6API = API(739299507795132486) #ssbutg leaderboard

class Mee6api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self): #the pylint below is required, so that we dont get a false error
        self.update_roles.start() #pylint: disable=no-member


    #command if someone wants to do it manually
    @commands.command(aliases=["updatelvl"], cooldown_after_parsing=True)
    @commands.guild_only() #cant be used in dms
    @commands.cooldown(1, 300, commands.BucketType.user) #1 use, 5m cooldown, per user. since the response time of the api isnt too great, i wanted to limit these requests
    async def updatelevel(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if member.bot:
            await ctx.send("Please do not use this command on bots.")
            ctx.command.reset_cooldown(ctx)
            return

        botmessage = await ctx.send("Please wait a few seconds...") #again, api is sometimes very slow so we send this message out first

        userlevel = await mee6API.levels.get_user_level(member.id) #gets the level

        defaultrole = get(ctx.guild.roles, id=739299507799326843)
        level10 = get(ctx.guild.roles, id=827473860936990730)
        level25 = get(ctx.guild.roles, id=827473868766707762)
        level50 = get(ctx.guild.roles, id=827473874413289484)
        level75 = get(ctx.guild.roles, id=827583894776840212)

        levelroles = [defaultrole, level10, level25, level50, level75]

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

        elif userlevel > 74:
            if level75 not in member.roles:
                for role in levelroles:
                    if role in member.roles:
                        await member.remove_roles(role)
                await member.add_roles(level75)
                rolegiven = level75


        if rolegiven is None:
            await botmessage.edit(content=f"{member.mention}, you are Level {userlevel}, so no new role for you.")
        else:
            await botmessage.edit(content=f"{member.mention}, you are Level {userlevel}, and thus I have given you the {rolegiven} role.")


    #generic error message
    @updatelevel.error
    async def updatelevel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in the SSBU TG Discord Server.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention a valid member, or leave it blank.")
        else:
            raise error



    #task that assigns roles automatically
    @tasks.loop(hours=23) #have set it to 23 hours so that it doesnt overlap often with the warnloop daily task, but doesnt matter that much
    async def update_roles(self):
        #pretty much the same command as above, just with different names so that it works for everyone in the server and also in a background task

        await self.bot.wait_until_ready() #waits until the bot is connected fully and then starts the task, otherwise not everything is cached properly

        guild = self.bot.get_guild(739299507795132486)

        defaultrole = get(guild.roles, id=739299507799326843)
        level10 = get(guild.roles, id=827473860936990730)
        level25 = get(guild.roles, id=827473868766707762)
        level50 = get(guild.roles, id=827473874413289484)
        level75 = get(guild.roles, id=827583894776840212)

        levelroles = [defaultrole, level10, level25, level50, level75]

        pageNumber = ceil(len(guild.members)/100) #gets the correct amount of pages
        for i in range(pageNumber):
            leaderboard_page = await mee6API.levels.get_leaderboard_page(i)
            for user in leaderboard_page["players"]:
                if int(user["id"]) in [guildMember.id for guildMember in guild.members]: #checks if the user is still in the guild
        
                    #need to fetch the member, since get_member is unreliable.
                    #even with member intents it kind of fails sometimes since not all members are cached
                    #this fetching step can take some time depending on guild size
                    #we also just can remove all level roles since this code only triggers if you rank up. after that add the new role
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
                    
                    elif user["level"] > 74:
                        member = await guild.fetch_member(user["id"])
                        if level75 not in member.roles:
                            for role in levelroles:
                                if role in member.roles:
                                    await member.remove_roles(role)
                            await member.add_roles(level75)
        
        print("level roles updated!")






def setup(bot):
    bot.add_cog(Mee6api(bot))
    print("Mee6api cog loaded")