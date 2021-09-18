import discord
from discord.ext import commands, tasks
import json
import asyncio
import time
from datetime import datetime, timedelta

#
#this file will contain our ranking system
#

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #getting a list with all the recent pings
    #we need a different approach than normal here because the rank also gets saved in a ranked ping
    #also this is its own function because we need to export it to matchmakingpings
    async def get_recent_ranked_pings(self, timestamp: float):
        with open(r'./json/rankedpings.json', 'r') as f:
            user_pings = json.load(f)

        list_of_searches = []

        for ping in user_pings:
            ping_rank = user_pings[f'{ping}']['rank']
            ping_channel = user_pings[f'{ping}']['channel']
            ping_timestamp = user_pings[f'{ping}']['time']

            difference = timestamp - ping_timestamp

            minutes = round(difference / 60)

            if minutes < 31:
                list_of_searches.append(f"<@&{ping_rank}> | <@!{ping}>, in <#{ping_channel}>, {minutes} minutes ago\n")

        list_of_searches.reverse()
        searches = ''.join(list_of_searches)

        if len(searches) == 0:
            searches = "Looks like no one has pinged recently :("

        return searches


    @commands.command(aliases=['ranked', 'rankedmatchmaking', 'rankedsingles'])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def rankedmm(self, ctx):
        #this is a basic mm command, just pings the role and checks the channel. also has a cooldown
        allowed_channels = (835582101926969344, 835582155446681620, 836018137119850557, 836018172238495744, 836018255113748510)
        if ctx.channel.id not in allowed_channels:
            await ctx.send("Please only use this command in the ranked matchmaking arenas.")
            ctx.command.reset_cooldown(ctx)
            return

        timestamp = discord.utils.utcnow().timestamp()
        
        with open(r'./json/ranking.json', 'r') as f:
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
        
        with open(r'./json/rankedpings.json', 'r') as fp:
            rankedusers = json.load(fp)
        
        #stores your ping
        rankedusers[f'{ctx.author.id}'] = {}
        rankedusers[f'{ctx.author.id}'] = {"rank": pingrole.id, "channel": ctx.channel.id, "time": timestamp}
        
        with open(r'./json/rankedpings.json', 'w') as fp:
            json.dump(rankedusers, fp, indent=4)

        #gets all of the other active pings
        searches = await self.get_recent_ranked_pings(timestamp)

        embed = discord.Embed(
            title="Ranked pings in the last 30 Minutes:", 
            description=searches, 
            colour=discord.Colour.blue())

        mm_message = await ctx.send(f"{ctx.author.mention} is looking for ranked matchmaking games! {pingrole.mention}", embed=embed)
        mm_thread = await mm_message.create_thread(name=f"Ranked Arena of {ctx.author.name}", auto_archive_duration=60)
        await mm_thread.add_user(ctx.author)
        await mm_thread.send(f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent and for reporting matches.")

        #waits 30 mins and deletes the ping afterwards
        await asyncio.sleep(1800)

        with open(r'./json/rankedpings.json', 'r') as fp:
            rankedusers = json.load(fp)

        try:
            del rankedusers[f'{ctx.message.author.id}']
        except KeyError:
            print("tried to delete a ranked ping but the deletion failed")

        with open(r'./json/rankedpings.json', 'w') as fp:
            json.dump(rankedusers, fp, indent=4)


    @commands.command(aliases=['reportgame'], cooldown_after_parsing=True)
    @commands.cooldown(1, 41, commands.BucketType.user) #1 use, 41s cooldown, per user
    @commands.guild_only() #cant be used in dms
    async def reportmatch(self, ctx, user: discord.Member):
        #the winning person should use this command to report a match

        allowed_channels = (835582101926969344, 835582155446681620, 836018137119850557)
        
        #since only threads have a parent_id, we need a special case for these to not throw any errors.
        if str(ctx.channel.type) == "public_thread":
            if ctx.channel.parent_id not in allowed_channels:
                await ctx.send("Please only use this command in the ranked matchmaking arenas or the threads within.")
                ctx.command.reset_cooldown(ctx)
                return
        else:
            if ctx.channel.id not in allowed_channels:
                await ctx.send("Please only use this command in the ranked matchmaking arenas or the threads within.")
                ctx.command.reset_cooldown(ctx)
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
        

        with open(r'./json/ranking.json', 'r+') as f: #r+ is read & write
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

        winnerdiff = winnerupdate - ranking[f'{ctx.author.id}']['elo']
        loserdiff = ranking[f'{user.id}']['elo'] - loserupdate

        ranking[f'{ctx.author.id}']['wins'] += 1 #updating their win/lose count
        ranking[f'{user.id}']['losses'] += 1

        ranking[f'{ctx.author.id}']['matches'].append('W')
        ranking[f'{user.id}']['matches'].append('L')

        ranking[f'{ctx.author.id}']['elo'] = winnerupdate #writing the new elo to the file
        ranking[f'{user.id}']['elo'] = loserupdate

        with open(r'./json/ranking.json', 'w') as f:
            json.dump(ranking, f, indent=4)

        async def updaterankroles(user): #checks the elo of the user, and assigns the elo role based on that
            elo = ranking[f'{user.id}']['elo']
            elo800role = discord.utils.get(ctx.guild.roles, id=835559992965988373)
            elo950role = discord.utils.get(ctx.guild.roles, id=835559996221554728)
            elo1050role = discord.utils.get(ctx.guild.roles, id=835560000658341888)
            elo1200role = discord.utils.get(ctx.guild.roles, id=835560003556999199)
            elo1300role = discord.utils.get(ctx.guild.roles, id=835560006907985930)
            elomaxrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)

            elo_roles = [elo800role, elo950role, elo1050role, elo1200role, elo1300role, elomaxrole]

            #the role change only triggers if the user does not have their current elo role, so its fine to remove ALL others first and then give the new one out
            if elo < 800:
                if elo800role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo800role)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo950role)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1050role)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1200role)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1300role)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elomaxrole)


        if ranking[f'{ctx.author.id}']['wins'] + ranking[f'{ctx.author.id}']['losses'] > 4: #only assigns these roles after 5 games
            elo = ranking[f'{ctx.author.id}']['elo']
            await updaterankroles(ctx.author)
        
        if ranking[f'{user.id}']['wins'] + ranking[f'{user.id}']['losses'] > 4:
            elo = ranking[f'{user.id}']['elo']
            await updaterankroles(user) 



        await ctx.send(f"Game successfully reported!\n{ctx.author.mention} won!\nUpdated Elo score: {ctx.author.mention} = {winnerupdate} (+{winnerdiff}) | {user.mention} = {loserupdate} (-{loserdiff})")


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

        with open(r'./json/ranking.json', 'r+') as f: #r+ is read & write
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

        winnerdiff = winnerupdate - ranking[f'{user1.id}']['elo']
        loserdiff = ranking[f'{user2.id}']['elo'] - loserupdate

        ranking[f'{user1.id}']['wins'] += 1 #updating their win/lose count
        ranking[f'{user2.id}']['losses'] += 1

        ranking[f'{user1.id}']['matches'].append('W')
        ranking[f'{user2.id}']['matches'].append('L')

        ranking[f'{user1.id}']['elo'] = winnerupdate #writing the new elo to the file
        ranking[f'{user2.id}']['elo'] = loserupdate

        with open(r'./json/ranking.json', 'w') as f:
            json.dump(ranking, f, indent=4)


        async def updaterankroles(user):
            elo = ranking[f'{user.id}']['elo']
            elo800role = discord.utils.get(ctx.guild.roles, id=835559992965988373)
            elo950role = discord.utils.get(ctx.guild.roles, id=835559996221554728)
            elo1050role = discord.utils.get(ctx.guild.roles, id=835560000658341888)
            elo1200role = discord.utils.get(ctx.guild.roles, id=835560003556999199)
            elo1300role = discord.utils.get(ctx.guild.roles, id=835560006907985930)
            elomaxrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)

            elo_roles = [elo800role, elo950role, elo1050role, elo1200role, elo1300role, elomaxrole]

            if elo < 800:
                if elo800role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo800role)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo950role)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1050role)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1200role)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1300role)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elomaxrole)


        if ranking[f'{user1.id}']['wins'] + ranking[f'{user1.id}']['losses'] > 4:
            elo = ranking[f'{user1.id}']['elo']
            await updaterankroles(user1)
        
        if ranking[f'{user2.id}']['wins'] + ranking[f'{user2.id}']['losses'] > 4:
            elo = ranking[f'{user2.id}']['elo']
            await updaterankroles(user2) 

        await ctx.send(f"Game successfully reported!\n{user1.mention} won!\nUpdated Elo score: {user1.mention} = {winnerupdate} (+{winnerdiff}) | {user2.mention} = {loserupdate} (-{loserdiff})\nGame was forcefully reported by: {ctx.author.mention}")



    @commands.command(aliases=['rankedstats'])
    async def rankstats(self, ctx, member: discord.Member = None):
        selfcheck = False
        if member is None:
            member = ctx.author
            selfcheck = True
        
        with open(r'./json/ranking.json', 'r') as f:
            ranking = json.load(f)

        eloscore = ranking[f'{member.id}']['elo']
        wins = ranking[f'{member.id}']['wins']
        losses = ranking[f'{member.id}']['losses']
        last5games = ranking[f'{member.id}']['matches'][-5:] #gets the last 5 games played
        gamelist = (''.join(last5games[::-1])) #reverses that list, makes it more intuitive to read

        embed = discord.Embed(title=f"Ranked stats of {str(member)}", colour=member.colour)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Elo score", value=eloscore, inline=True)
        embed.add_field(name="Wins", value=wins, inline=True)
        embed.add_field(name="Losses", value=losses, inline=True)
        embed.add_field(name="Last Matches", value=gamelist, inline=True)
        embed.set_footer(text="React within 120s to turn ranked notifications on or off until the next match" if selfcheck is True else "")

        embed_message = await ctx.send(embed=embed)

        if selfcheck is True: #if you invoked your command yourself, this here executes, with the choice of removing or adding your ranked role
            await embed_message.add_reaction("🔔")
            await embed_message.add_reaction("🔕")

            def reaction_check(reaction, member):
                return member.id == ctx.author.id and reaction.message.id == embed_message.id and str(reaction.emoji) in ["🔔", "🔕"]
            
            try:
                reaction, member = await self.bot.wait_for("reaction_add", timeout=120.0, check=reaction_check)
            except asyncio.TimeoutError:
                return
            else:
                if str(reaction.emoji) == "🔔":
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
                    await ctx.author.add_roles(pingrole)
                elif str(reaction.emoji) == "🔕":
                    elo800role = discord.utils.get(ctx.guild.roles, id=835559992965988373)
                    elo950role = discord.utils.get(ctx.guild.roles, id=835559996221554728)
                    elo1050role = discord.utils.get(ctx.guild.roles, id=835560000658341888)
                    elo1200role = discord.utils.get(ctx.guild.roles, id=835560003556999199)
                    elo1300role = discord.utils.get(ctx.guild.roles, id=835560006907985930)
                    elomaxrole = discord.utils.get(ctx.guild.roles, id=835560009810444328)
                    roles = [elo800role, elo950role, elo1050role, elo1200role, elo1300role, elomaxrole]
                    for role in roles:
                        await ctx.author.remove_roles(role)
                else:
                    pass


    #leaderboards are admin only because we dont want people to obsess over rankings, these will stay hidden
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def leaderboard(self, ctx):
        with open(r'./json/ranking.json', 'r') as f:
            ranking = json.load(f)

        all_userinfo = []
                
        for user in ranking:
            eloscore = ranking[f'{user}']['elo']
            wins = ranking[f'{user}']['wins']
            lose = ranking[f'{user}']['losses']
            userinfo = (user, eloscore, wins, lose)
            all_userinfo.append(userinfo)

        all_userinfo.sort(key=lambda x:x[1]) #sorts them by their elo score
        all_userinfo.reverse() #reverses that list, top to bottom
        all_userinfo = all_userinfo[:10] #only gets top 10 entries

        rawstats = []

        rank = 1

        for i in all_userinfo:
            user = i[0]
            elo = i[1]
            wins = i[2]
            lose = i[3]
            rawstats.append(f"{rank} | <@!{user}> | {elo} | {wins}/{lose}\n")
            rank += 1

        embedstats = ''.join(rawstats) #needed for a neat embed

        embed = discord.Embed(title="Top 10 Players of SSBU TG Ranked Matchmaking", description=f"**Rank | Username | Elo score | W/L**\n{embedstats}", colour=discord.Colour.blue())
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)




    #some basic error handling
    @reportmatch.error
    async def reportmatch_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Please only use this command in the SSBU TG Discord Server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention the member that you beat in the match.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention the member that you beat in the match.")
        else:
            raise error


    @forcereportmatch.error
    async def forcereportmatch_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention the 2 members that have played in this match. First mention the winner, second mention the loser.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention the 2 members that have played in this match. First mention the winner, second mention the loser.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        else:
            raise error

    @rankstats.error
    async def rankstats_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("This user hasn't played a ranked match yet.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I couldn't find this member, make sure you have the right one or just leave it blank.")
        else:
            raise error

    @rankedmm.error
    async def rankedmm_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            allowed_channels = (835582101926969344, 835582155446681620, 836018137119850557)
            if ctx.channel.id not in allowed_channels:
                await ctx.send("Please only use this command in the ranked matchmaking arenas.")
                return
            
            timestamp = discord.utils.utcnow().timestamp()

            searches = await self.get_recent_ranked_pings(timestamp)

            embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.blue())
                
            await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent ranked pings:", embed=embed)
        else:
            raise error

    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error



def setup(bot):
    bot.add_cog(Ranking(bot))
    print("Ranking cog loaded")