import discord
from discord.ext import commands, tasks
import json
import time
from datetime import datetime, timedelta
import asyncio

#
#this file here contains our matchmaking system
#

class Matchmaking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.clear_mmrequests() #clears the mm files on bot startup, otherwise pings would get stuck in there forever when i shut the bot down


    @commands.command(aliases=['matchmaking', 'matchmakingsingles', 'mmsingles', 'Singles'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def singles(self, ctx):
        arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
        special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108) #above are public arenas, these are private arenas
        guild = self.bot.get_guild(739299507795132486) #ssbutg server
        timestamp = time.strftime("%H:%M") #timestamp for storing, simplified to only hours/mins

        singles_role = discord.utils.get(guild.roles, id=739299507799326842)
        if ctx.message.channel.id in arena_channels: #code for the public arenas
            with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
                singles = json.load(f)
            singles_mm = ctx.message.author
            channel = ctx.message.channel.id
            singles[f'{singles_mm.id}'] = {}
            singles[f'{singles_mm.id}'] = {"channel": channel, "time": timestamp} #storing the mm request
            list_of_searches = [] #list for later

            for singles_mm in singles: #gets every active mm request
                channel_mm = singles[f'{singles_mm}']['channel']
                timecode = singles[f'{singles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M") #this block gets the time difference in minutes
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000: #band aid fix, im only storing the hours/minutes so if a ping from before midnight gets called after, the negative of that number appears
                    minutes = minutes + 1440 #we can fix that by just adding a whole day which is 1440 mins
                list_of_searches.append(f"<@!{singles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches) #stores the requests in a string, not a list
            embed = discord.Embed(title="Singles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_red())
            await ctx.send(f"{ctx.author.mention} is looking for {singles_role.mention} games!", embed=embed)

            with open(r'/root/tabuu bot/json/singles.json', 'w') as f:
                json.dump(singles, f, indent=4) #writes it to the file

            await asyncio.sleep(1800) #waits 30 mins, then deletes the request. if there are 2 requests the first one will get overwritten and on the second delete we will get a keyerror, which isnt a problem
            with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
                singles = json.load(f)
            del singles[f'{ctx.message.author.id}']
            with open(r'/root/tabuu bot/json/singles.json', 'w') as f:
                json.dump(singles, f, indent=4)
            
        elif ctx.message.channel.id in special_arenas: #code for private arenas, same thing but doesnt add your ping to the list
            with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
                singles = json.load(f)
            list_of_searches = []
            for singles_mm in singles:
                channel_mm = singles[f'{singles_mm}']['channel']
                timecode = singles[f'{singles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{singles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Singles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_red())
            await ctx.send(f"{ctx.author.mention} is looking for {singles_role.mention} games!\nHere are the most recent Singles pings in our open arenas:", embed=embed)

        else: #code for every other channel
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)


    @singles.error #on cooldown error, just pulls up the same list with a cooldown message
    async def singles_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
            special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108) #above are public arenas, these are private arenas
            timestamp = time.strftime("%H:%M") #timestamp for storing, simplified to only hours/mins
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
                    singles = json.load(f)
                list_of_searches = []
                for singles_mm in singles:
                    channel_mm = singles[f'{singles_mm}']['channel']
                    timecode = singles[f'{singles_mm}']['time']
                    old_ping = datetime.strptime(timecode, "%H:%M")
                    new_ping = datetime.strptime(timestamp, "%H:%M")
                    timedelta = new_ping - old_ping
                    seconds = timedelta.total_seconds()
                    minutes = round(seconds/60)
                    if minutes < -1000:
                        minutes = minutes + 1440
                    list_of_searches.append(f"<@!{singles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
                list_of_searches.reverse()
                searches = ''.join(list_of_searches)
                if len(searches) == 0:
                    searches = "Looks like no one has pinged recently :("
                embed = discord.Embed(title="Singles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_red())
                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Singles pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        raise error


    #for the doubles/funnies commands, pretty much everything is the same, just slightly altered the names

    @commands.command(aliases=['matchmakingdoubles', 'mmdoubles', 'Doubles'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def doubles(self, ctx):
        arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
        special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)
        guild = self.bot.get_guild(739299507795132486)
        timestamp = time.strftime("%H:%M")

        doubles_role = discord.utils.get(guild.roles, id=739299507799326841)
        if ctx.message.channel.id in arena_channels:
            with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
                doubles = json.load(f)

            doubles_mm = ctx.message.author
            channel = ctx.message.channel.id
            doubles[f'{doubles_mm.id}'] = {}
            doubles[f'{doubles_mm.id}'] = {"channel": channel, "time": timestamp}
            list_of_searches = []

            for doubles_mm in doubles:
                channel_mm = doubles[f'{doubles_mm}']['channel']
                timecode = doubles[f'{doubles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{doubles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            embed = discord.Embed(title="Doubles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_blue())
            await ctx.send(f"{ctx.author.mention} is looking for {doubles_role.mention} games!", embed=embed)

            with open(r'/root/tabuu bot/json/doubles.json', 'w') as f:
                json.dump(doubles, f, indent=4)

            await asyncio.sleep(1800) #30 mins
            with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
                doubles = json.load(f)
            del doubles[f'{ctx.message.author.id}']
            with open(r'/root/tabuu bot/json/doubles.json', 'w') as f:
                json.dump(doubles, f, indent=4)

        elif ctx.message.channel.id in special_arenas:
            with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
                doubles = json.load(f)
            list_of_searches = []
            for doubles_mm in doubles:
                channel_mm = doubles[f'{doubles_mm}']['channel']
                timecode = doubles[f'{doubles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{doubles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Doubles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_blue())
            await ctx.send(f"{ctx.author.mention} is looking for {doubles_role.mention} games!\nHere are the most recent Doubles pings in our open arenas:", embed=embed)

        else:
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)

    @doubles.error
    async def doubles_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
            special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)
            timestamp = time.strftime("%H:%M")
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
                    doubles = json.load(f)
                list_of_searches = []
                for doubles_mm in doubles:
                    channel_mm = doubles[f'{doubles_mm}']['channel']
                    timecode = doubles[f'{doubles_mm}']['time']
                    old_ping = datetime.strptime(timecode, "%H:%M")
                    new_ping = datetime.strptime(timestamp, "%H:%M")
                    timedelta = new_ping - old_ping
                    seconds = timedelta.total_seconds()
                    minutes = round(seconds/60)
                    if minutes < -1000:
                        minutes = minutes + 1440
                    list_of_searches.append(f"<@!{doubles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
                list_of_searches.reverse()
                searches = ''.join(list_of_searches)
                if len(searches) == 0:
                    searches = "Looks like no one has pinged recently :("
                embed = discord.Embed(title="Doubles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_blue())
                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Doubles pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        raise error



    @commands.command(aliases=['matchmakingfunnies', 'mmfunnies', 'Funnies'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def funnies(self, ctx):
        arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
        special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)
        guild = self.bot.get_guild(739299507795132486)
        timestamp = time.strftime("%H:%M")

        funnies_role = discord.utils.get(guild.roles, id=739299507795132495)
        if ctx.message.channel.id in arena_channels:
            with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
                funnies = json.load(f)

            funnies_mm = ctx.message.author
            channel = ctx.message.channel.id
            funnies[f'{funnies_mm.id}'] = {}
            funnies[f'{funnies_mm.id}'] = {"channel": channel, "time": timestamp}
            list_of_searches = []

            for funnies_mm in funnies:
                channel_mm = funnies[f'{funnies_mm}']['channel']
                timecode = funnies[f'{funnies_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{funnies_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            embed = discord.Embed(title="Funnies pings in the last 30 Minutes:", description=searches, colour=discord.Colour.green())
            await ctx.send(f"{ctx.author.mention} is looking for {funnies_role.mention} games!", embed=embed)

            with open(r'/root/tabuu bot/json/funnies.json', 'w') as f:
                json.dump(funnies, f, indent=4)

            await asyncio.sleep(1800) #30 mins
            with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
                funnies = json.load(f)
            del funnies[f'{ctx.message.author.id}']
            with open(r'/root/tabuu bot/json/funnies.json', 'w') as f:
                json.dump(funnies, f, indent=4)

        elif ctx.message.channel.id in special_arenas:
            with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
                funnies = json.load(f)
            list_of_searches = []
            for funnies_mm in funnies:
                channel_mm = funnies[f'{funnies_mm}']['channel']
                timecode = funnies[f'{funnies_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{funnies_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Funnies pings in the last 30 Minutes:", description=searches, colour=discord.Colour.green())
            await ctx.send(f"{ctx.author.mention} is looking for {funnies_role.mention} games!\nHere are the most recent Funnies pings in our open arenas:", embed=embed)

        else:
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)

    @funnies.error
    async def funnies_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            arena_channels = (739299508403437626, 739299508403437627, 739299508403437628, 739299508688519198, 739299508688519200, 742190378051960932, 749016706529361920, 814726078010228737)
            special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)
            timestamp = time.strftime("%H:%M")
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
                    funnies = json.load(f)
                list_of_searches = []
                for funnies_mm in funnies:
                    channel_mm = funnies[f'{funnies_mm}']['channel']
                    timecode = funnies[f'{funnies_mm}']['time']
                    old_ping = datetime.strptime(timecode, "%H:%M")
                    new_ping = datetime.strptime(timestamp, "%H:%M")
                    timedelta = new_ping - old_ping
                    seconds = timedelta.total_seconds()
                    minutes = round(seconds/60)
                    if minutes < -1000:
                        minutes = minutes + 1440
                    list_of_searches.append(f"<@!{funnies_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
                list_of_searches.reverse()
                searches = ''.join(list_of_searches)
                if len(searches) == 0:
                    searches = "Looks like no one has pinged recently :("
                embed = discord.Embed(title="Funnies pings in the last 30 Minutes:", description=searches, colour=discord.Colour.green())
                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Funnies pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        raise error



    #added this command so that if a ping gets stuck in the files i dont have to restart the bot
    @commands.command(aliases=['clearmmrequests', 'clearmm', 'clearmatchmaking'])
    @commands.has_permissions(administrator=True)
    async def clearmmpings(self, ctx):
        await self.clear_mmrequests() #just calls the function below
        await ctx.send("Cleared the matchmaking pings!")

    @clearmmpings.error
    async def clearmmpings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        raise error


    @commands.command()
    async def recentpings(self, ctx, mm_type):
        timestamp = time.strftime("%H:%M")
        if mm_type.lower() == "singles":
            with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
                singles = json.load(f)
            list_of_searches = []
            for singles_mm in singles:
                channel_mm = singles[f'{singles_mm}']['channel']
                timecode = singles[f'{singles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{singles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Singles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_red())
            await ctx.send(embed=embed)
            return
        if mm_type.lower() == "doubles":
            with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
                doubles = json.load(f)
            list_of_searches = []
            for doubles_mm in doubles:
                channel_mm = doubles[f'{doubles_mm}']['channel']
                timecode = doubles[f'{doubles_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{doubles_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Doubles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_blue())
            await ctx.send(embed=embed)
            return
        if mm_type.lower() == "funnies":
            with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
                funnies = json.load(f)
            list_of_searches = []
            for funnies_mm in funnies:
                channel_mm = funnies[f'{funnies_mm}']['channel']
                timecode = funnies[f'{funnies_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M")
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000:
                    minutes = minutes + 1440
                list_of_searches.append(f"<@!{funnies_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches)
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Funnies pings in the last 30 Minutes:", description=searches, colour=discord.Colour.green())
            await ctx.send(embed=embed)
            return
        elif mm_type.lower() == "ranked":
            with open(r'/root/tabuu bot/json/rankedpings.json', 'r') as f:
                rankedusers = json.load(f)
            
            list_of_searches = [] #list for later

            for ranked_mm in rankedusers: #gets every active mm request
                rankrole = rankedusers[f'{ranked_mm}']['rank']
                channel_mm = rankedusers[f'{ranked_mm}']['channel']
                timecode = rankedusers[f'{ranked_mm}']['time']
                old_ping = datetime.strptime(timecode, "%H:%M") #this block gets the time difference in minutes
                new_ping = datetime.strptime(timestamp, "%H:%M")
                timedelta = new_ping - old_ping
                seconds = timedelta.total_seconds()
                minutes = round(seconds/60)
                if minutes < -1000: #band aid fix, im only storing the hours/minutes so if a ping from before midnight gets called after, the negative of that number appears
                    minutes = minutes + 1440 #we can fix that by just adding a whole day which is 1440 mins
                list_of_searches.append(f"<@&{rankrole}> | <@!{ranked_mm}>, in <#{channel_mm}>, {minutes} minutes ago\n")
            list_of_searches.reverse()
            searches = ''.join(list_of_searches) #stores the requests in a string, not a list
            if len(searches) == 0:
                searches = "Looks like no one has pinged recently :("
            embed = discord.Embed(title="Ranked pings in the last 30 Minutes:", description=searches, colour=discord.Colour.blue())
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send("Invalid input! Please choose either singles, doubles, funnies or ranked.")
            pass

    @recentpings.error
    async def recentpings_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Invalid input! Please choose either singles, doubles, funnies or ranked.")
        raise error




    #this clears the mm files so that no ping gets stuck if i restart the bot
    async def clear_mmrequests(self):

        #deleting singles file

        with open(r'/root/tabuu bot/json/singles.json', 'r') as f:
            singles = json.load(f)
        
        singles_requests = []

        for user in singles:
            singles_requests.append(user)

        for user in singles_requests:
            del singles[user]
        
        with open(r'/root/tabuu bot/json/singles.json', 'w') as f:
            json.dump(singles, f, indent=4)

        print("singles file cleared!")

        #deleting doubles file

        with open(r'/root/tabuu bot/json/doubles.json', 'r') as f:
            doubles = json.load(f)
        
        doubles_requests = []

        for user in doubles:
            doubles_requests.append(user)

        for user in doubles_requests:
            del doubles[user]
        
        with open(r'/root/tabuu bot/json/doubles.json', 'w') as f:
            json.dump(doubles, f, indent=4)

        print("doubles file cleared!")

        #deleting funnies file

        with open(r'/root/tabuu bot/json/funnies.json', 'r') as f:
            funnies = json.load(f)
        
        funnies_requests = []

        for user in funnies:
            funnies_requests.append(user)

        for user in funnies_requests:
            del funnies[user]
        
        with open(r'/root/tabuu bot/json/funnies.json', 'w') as f:
            json.dump(funnies, f, indent=4)

        print("funnies file cleared!")

        #deleting ranked file

        with open(r'/root/tabuu bot/json/rankedpings.json', 'r') as f:
            ranked = json.load(f)
        
        ranked_requests = []
        
        for user in ranked:
            ranked_requests.append(user)
        
        for user in ranked_requests:
            del ranked[user]
        
        with open(r'/root/tabuu bot/json/rankedpings.json', 'w') as f:
            json.dump(ranked, f, indent=4)

        print("ranked file cleared!")


def setup(bot):
    bot.add_cog(Matchmaking(bot))
    print("Matchmaking cog loaded")