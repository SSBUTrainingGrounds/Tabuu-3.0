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
    @commands.command()
    @commands.guild_only() #cant be used in dms
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user. since the response time of the api isnt too great, i wanted to limit these requests
    async def updatelevel(self, ctx):

        botmessage = await ctx.send("Please wait a few seconds...") #again, api is sometimes very slow so we send this message out first

        userlevel = await mee6API.levels.get_user_level(ctx.author.id) #gets the level

        defaultrole = get(ctx.guild.roles, id=739299507799326843)
        level10 = get(ctx.guild.roles, id=827473860936990730)
        level25 = get(ctx.guild.roles, id=827473868766707762)
        level50 = get(ctx.guild.roles, id=827473874413289484)
        level75 = get(ctx.guild.roles, id=827583894776840212)

        
        if userlevel > 9 and userlevel < 25:
            if level10 not in ctx.author.roles:
                await ctx.author.add_roles(level10)
                await ctx.author.remove_roles(defaultrole)
                rolegiven = level10
        
        elif userlevel > 24 and userlevel < 50:
            if level25 not in ctx.author.roles:
                await ctx.author.add_roles(level25)
                await ctx.author.remove_roles(defaultrole)
                rolegiven = level25
            if level10 in ctx.author.roles:
                await ctx.author.remove_roles(level10)
            
        elif userlevel > 49 and userlevel < 75:
            if level50 not in ctx.author.roles:
                await ctx.author.add_roles(level50)
                await ctx.author.remove_roles(defaultrole)
                rolegiven = level50
            if level25 in ctx.author.roles:
                await ctx.author.remove_roles(level25)

        elif userlevel > 74:
            if level75 not in ctx.author.roles:
                await ctx.author.add_roles(level75)
                await ctx.author.remove_roles(defaultrole)
                rolegiven = level75
            if level50 in ctx.author.roles:
                await ctx.author.remove_roles(level50)

        


        try: #if rolegiven isnt referenced, it will throw an error and the below message appears
            await botmessage.edit(content=f"{ctx.author.mention}, you are Level {userlevel}, and thus I have given you the {rolegiven} role.")
        except:
            await botmessage.edit(content=f"{ctx.author.mention}, you are Level {userlevel}, so no new role for you.")

    #generic error message
    @updatelevel.error
    async def updatelevel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command.")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in the SSBU TG Discord Server.")
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


        pageNumber = ceil(len(guild.members)/100) #gets the correct amount of pages
        for i in range(pageNumber):
            leaderboard_page = await mee6API.levels.get_leaderboard_page(i)
            for user in leaderboard_page["players"]:
                if int(user["id"]) in [guildMember.id for guildMember in guild.members]: #checks if the user is still in the guild
        
                    if user["level"] > 9 and user["level"] < 25:
                        user1 = await self.bot.fetch_user(user['id']) #no idea why i have to fetch the user first and then get the member second but it won't work otherwise
                        user2 = guild.get_member(user1.id) #also this step could take some time depending on the size of the guild
                        if level10 not in user2.roles:
                            await user2.add_roles(level10)
                            await user2.remove_roles(defaultrole)
                    
                    elif user["level"] > 24 and user["level"] < 50:
                        user1 = await self.bot.fetch_user(user['id']) #same here, i put this in the user level checks so it doesnt fetch everyone
                        user2 = guild.get_member(user1.id)
                        if level25 not in user2.roles:
                            await user2.add_roles(level25)
                            await user2.remove_roles(defaultrole)
                            await user2.remove_roles(level10)
                        
                    elif user["level"] > 49 and user["level"] < 75:
                        user1 = await self.bot.fetch_user(user['id'])
                        user2 = guild.get_member(user1.id)
                        if level50 not in user2.roles:
                            await user2.add_roles(level50)
                            await user2.remove_roles(defaultrole)
                            await user2.remove_roles(level25)
                    
                    elif user["level"] > 74:
                        user1 = await self.bot.fetch_user(user['id'])
                        user2 = guild.get_member(user1.id)
                        if level75 not in user2.roles:
                            await user2.add_roles(level75)
                            await user2.remove_roles(defaultrole)
                            await user2.remove_roles(level50)
        
        print("level roles updated!")







def setup(bot):
    bot.add_cog(Mee6api(bot))
    print("Mee6api cog loaded")