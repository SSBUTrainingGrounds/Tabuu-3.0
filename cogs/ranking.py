import discord
from discord.ext import commands, tasks
import json
import asyncio

#
#this file will contain our ranking system
#

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['ranked', 'rankedmatchmaking', 'rankedsingles'])
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.guild_only()
    async def rankedmm(self, ctx):
        #this is a basic mm command, just pings the role and checks the channel. also has a cooldown
        allowed_channels = (835582101926969344, 835582155446681620, 836018137119850557, 836018172238495744, 836018255113748510)
        if ctx.channel.id not in allowed_channels:
            await ctx.send("Please only use this command in the ranked matchmaking arenas.")
            return
        
        with open(r'/root/tabuu bot/json/ranking.json', 'r') as f:
            ranking = json.load(f)

        try:
            elo = ranking[f'{ctx.author.id}']['elo'] #gets your elo score and the according value
            if elo < 800:
                pingrole = discord.utils.get(ctx.guild.roles, id=835559992965988373)
            if elo < 950 and elo > 799:
                pingrole = discord.utils.get(ctx.guild.roles, id=835559996221554728)
            if elo < 1050 and elo > 949:
                pingrole = discord.utils.get(ctx.guild.roles, id=835560000658341888)
            if elo < 1200 and elo > 1049:
                pingrole = discord.utils.get(ctx.guild.roles, id=835560003556999199)
            if elo < 1300 and elo > 1199:
                pingrole = discord.utils.get(ctx.guild.roles, id=835560006907985930)
            if elo > 1299:
                pingrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)
        except:
            pingrole = discord.utils.get(ctx.guild.roles, id=835560000658341888) #default elo role, in case someone isnt in the database
        
        await ctx.send(f"{ctx.author.mention} is looking for ranked matchmaking games! {pingrole.mention}")


    @commands.command(aliases=['reportgame'], cooldown_after_parsing=True)
    @commands.cooldown(1, 41, commands.BucketType.user) #1 use, 41s cooldown, per user
    @commands.guild_only() #cant be used in dms
    async def reportmatch(self, ctx, user: discord.Member):
        #the winning person should use this command to report a match

        allowed_channels = (835582101926969344, 835582155446681620, 836018137119850557, 836018172238495744, 836018255113748510)
        if ctx.channel.id not in allowed_channels:
            await ctx.send("Please only use this command in the ranked matchmaking arenas.")
            return

        if user is ctx.author: #to prevent any kind of abuse
            await ctx.send("Don't report matches with yourself please.")
            ctx.command.reset_cooldown(ctx)
            return
        
        if user.bot: #same here
            await ctx.send("Are you trying to play a match with bots?")
            ctx.command.reset_cooldown(ctx)
            return


        def check(message):
            return message.content.lower() == "y" and message.author == user and message.channel == ctx.channel

        await ctx.send(f"The winner of the match {ctx.author.mention} vs. {user.mention} is: {ctx.author.mention}! \n{user.mention} do you agree with the results? **Type y to verify.**")
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try reporting the match again.")
            return
        

        with open(r'/root/tabuu bot/json/ranking.json', 'r+') as f: #r+ is read & write
            ranking = json.load(f)

        if not f'{ctx.author.id}' in ranking: #if someone does not exist in the file, it'll create a "profile"
            ranking[f'{ctx.author.id}'] = {}
            ranking[f'{ctx.author.id}']['wins'] = 0
            ranking[f'{ctx.author.id}']['losses'] = 0
            ranking[f'{ctx.author.id}']['elo'] = 1000 #default value in the elo system
            ranking[f'{ctx.author.id}']['matches'] = []
        
        if not f'{user.id}' in ranking: #same here, for the mentioned user
            ranking[f'{user.id}'] = {}
            ranking[f'{user.id}']['wins'] = 0
            ranking[f'{user.id}']['losses'] = 0
            ranking[f'{user.id}']['elo'] = 1000
            ranking[f'{user.id}']['matches'] = []
        
        def expected(A, B): #the expected score of the match, used in the function below
            return 1 / (1 + 10 ** ((B - A) / 400))
        
        def elo(old, exp, score, k=32): #updates your elo rating
            return old + k * (score - exp)

        

        winnerexpected = expected(ranking[f'{ctx.author.id}']['elo'], ranking[f'{user.id}']['elo'])
        loserexpected = expected(ranking[f'{user.id}']['elo'], ranking[f'{ctx.author.id}']['elo'])

        winnerupdate = round(elo(ranking[f'{ctx.author.id}']['elo'], winnerexpected, 1)) #1 is a win, 0 is a loss. 0.5 would be a draw but there are no draws here
        loserupdate = round(elo(ranking[f'{user.id}']['elo'], loserexpected, 0))

        ranking[f'{ctx.author.id}']['wins'] += 1 #updating their win/lose count
        ranking[f'{user.id}']['losses'] += 1

        ranking[f'{ctx.author.id}']['matches'].append('W')
        ranking[f'{user.id}']['matches'].append('L')

        ranking[f'{ctx.author.id}']['elo'] = winnerupdate #writing the new elo to the file
        ranking[f'{user.id}']['elo'] = loserupdate

        with open(r'/root/tabuu bot/json/ranking.json', 'w') as f:
            json.dump(ranking, f, indent=4)

        async def updaterankroles(user): #checks the elo of the user, and assigns the elo role based on that
            elo = ranking[f'{user.id}']['elo']
            elo800role = discord.utils.get(ctx.guild.roles, id=835559992965988373)
            elo950role = discord.utils.get(ctx.guild.roles, id=835559996221554728)
            elo1050role = discord.utils.get(ctx.guild.roles, id=835560000658341888)
            elo1200role = discord.utils.get(ctx.guild.roles, id=835560003556999199)
            elo1300role = discord.utils.get(ctx.guild.roles, id=835560006907985930)
            elomaxrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)

            if elo < 800:
                if elo800role not in user.roles:
                    await user.add_roles(elo800role)
                    await user.remove_roles(elo950role, elo1050role, elo1200role, elo1300role, elomaxrole)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    await user.add_roles(elo950role)
                    await user.remove_roles(elo800role, elo1050role, elo1200role, elo1300role, elomaxrole)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    await user.add_roles(elo1050role)
                    await user.remove_roles(elo800role, elo950role, elo1200role, elo1300role, elomaxrole)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    await user.add_roles(elo1200role)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1300role, elomaxrole)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    await user.add_roles(elo1300role)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1200role, elomaxrole)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    await user.add_roles(elomaxrole)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1200role, elo1300role)


        if ranking[f'{ctx.author.id}']['wins'] + ranking[f'{ctx.author.id}']['losses'] > 4: #only assigns these roles after 5 games
            elo = ranking[f'{ctx.author.id}']['elo']
            await updaterankroles(ctx.author)
        
        if ranking[f'{user.id}']['wins'] + ranking[f'{user.id}']['losses'] > 4:
            elo = ranking[f'{user.id}']['elo']
            await updaterankroles(user) 



        await ctx.send(f"Game successfully reported!\n{ctx.author.mention} won!\nUpdated Elo score: {ctx.author.mention} = {winnerupdate} | {user.mention} = {loserupdate}")


    @commands.command(aliases=['forcereportgame'], cooldown_after_parsing=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 41, commands.BucketType.user) #1 use, 41s cooldown, per user
    async def forcereportmatch(self, ctx, user1: discord.Member, user2: discord.Member):
        #if someone abandons the game, a mod can step in and report that game for them
        #most of this command is just copied from the one above, with a few tweaks

        def check(message):
            return message.content.lower() == "y" and message.author == ctx.author and message.channel == ctx.channel

        await ctx.send(f"The winner of the match {user1.mention} vs. {user2.mention} is: {user1.mention}! \n{ctx.author.mention}, is that result correct? **Type y to verify.**")
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try reporting the match again.")
            return

        with open(r'/root/tabuu bot/json/ranking.json', 'r+') as f: #r+ is read & write
            ranking = json.load(f)

        if not f'{user1.id}' in ranking: #if someone does not exist in the file, it'll create a "profile"
            ranking[f'{user1.id}'] = {}
            ranking[f'{user1.id}']['wins'] = 0
            ranking[f'{user1.id}']['losses'] = 0
            ranking[f'{user1.id}']['elo'] = 1000 #default value in the elo system
            ranking[f'{user1.id}']['matches'] = []
        
        if not f'{user2.id}' in ranking: #same here, for the mentioned user
            ranking[f'{user2.id}'] = {}
            ranking[f'{user2.id}']['wins'] = 0
            ranking[f'{user2.id}']['losses'] = 0
            ranking[f'{user2.id}']['elo'] = 1000
            ranking[f'{user2.id}']['matches'] = []
        
        def expected(A, B): #the expected score of the match, used in the function below
            return 1 / (1 + 10 ** ((B - A) / 400))
        
        def elo(old, exp, score, k=32): #updates your elo rating
            return old + k * (score - exp)

        

        winnerexpected = expected(ranking[f'{user1.id}']['elo'], ranking[f'{user2.id}']['elo'])
        loserexpected = expected(ranking[f'{user2.id}']['elo'], ranking[f'{user1.id}']['elo'])

        winnerupdate = round(elo(ranking[f'{user1.id}']['elo'], winnerexpected, 1)) #1 is a win, 0 is a loss. 0.5 would be a draw but there are no draws here
        loserupdate = round(elo(ranking[f'{user2.id}']['elo'], loserexpected, 0))

        ranking[f'{user1.id}']['wins'] += 1 #updating their win/lose count
        ranking[f'{user2.id}']['losses'] += 1

        ranking[f'{user1.id}']['matches'].append('W')
        ranking[f'{user2.id}']['matches'].append('L')

        ranking[f'{user1.id}']['elo'] = winnerupdate #writing the new elo to the file
        ranking[f'{user2.id}']['elo'] = loserupdate

        with open(r'/root/tabuu bot/json/ranking.json', 'w') as f:
            json.dump(ranking, f, indent=4)


        async def updaterankroles(user):
            elo = ranking[f'{user.id}']['elo']
            elo800role = discord.utils.get(ctx.guild.roles, id=835559992965988373)
            elo950role = discord.utils.get(ctx.guild.roles, id=835559996221554728)
            elo1050role = discord.utils.get(ctx.guild.roles, id=835560000658341888)
            elo1200role = discord.utils.get(ctx.guild.roles, id=835560003556999199)
            elo1300role = discord.utils.get(ctx.guild.roles, id=835560006907985930)
            elomaxrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)

            if elo < 800:
                if elo800role not in user.roles:
                    await user.add_roles(elo800role)
                    await user.remove_roles(elo950role, elo1050role, elo1200role, elo1300role, elomaxrole)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    await user.add_roles(elo950role)
                    await user.remove_roles(elo800role, elo1050role, elo1200role, elo1300role, elomaxrole)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    await user.add_roles(elo1050role)
                    await user.remove_roles(elo800role, elo950role, elo1200role, elo1300role, elomaxrole)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    await user.add_roles(elo1200role)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1300role, elomaxrole)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    await user.add_roles(elo1300role)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1200role, elomaxrole)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    await user.add_roles(elomaxrole)
                    await user.remove_roles(elo800role, elo950role, elo1050role, elo1200role, elo1300role)


        if ranking[f'{user1.id}']['wins'] + ranking[f'{user1.id}']['losses'] > 4:
            elo = ranking[f'{user1.id}']['elo']
            await updaterankroles(user1)
        
        if ranking[f'{user2.id}']['wins'] + ranking[f'{user2.id}']['losses'] > 4:
            elo = ranking[f'{user2.id}']['elo']
            await updaterankroles(user2) 

        await ctx.send(f"Game successfully reported!\n{user1.mention} won!\nUpdated Elo score: {user1.mention} = {winnerupdate} | {user2.mention} = {loserupdate}\nGame was forcefully reported by: {ctx.author.mention}")



    @commands.command(aliases=['rankedstats'])
    async def rankstats(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        with open(r'/root/tabuu bot/json/ranking.json', 'r') as f:
            ranking = json.load(f)

        eloscore = ranking[f'{member.id}']['elo']
        wins = ranking[f'{member.id}']['wins']
        losses = ranking[f'{member.id}']['losses']
        last5games = ranking[f'{member.id}']['matches'][-5:] #gets the last 5 games played
        gamelist = (''.join(last5games[::-1])) #reverses that list, makes it more intuitive to read

        embed = discord.Embed(title=f"Ranked stats of {str(member)}", colour=member.colour)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Elo score", value=eloscore, inline=True)
        embed.add_field(name="Wins", value=wins, inline=True)
        embed.add_field(name="Losses", value=losses, inline=True)
        embed.add_field(name="Last Matches", value=gamelist, inline=True)

        await ctx.send(embed=embed)



    #some basic error handling
    @reportmatch.error
    async def reportmatch_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Please only use this command in the SSBU TG Discord Server.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention the member that you beat in the match.")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention the member that you beat in the match.")
        raise error


    @forcereportmatch.error
    async def forcereportmatch_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention the 2 members that have played in this match. First mention the winner, second mention the loser.")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention the 2 members that have played in this match. First mention the winner, second mention the loser.")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        raise error

    @rankstats.error
    async def rankstats_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("This user hasn't played a ranked match yet.")
        raise error

    @rankedmm.error
    async def rankedmm_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        raise error



def setup(bot):
    bot.add_cog(Ranking(bot))
    print("Ranking cog loaded")