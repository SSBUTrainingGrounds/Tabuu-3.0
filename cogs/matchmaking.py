import discord
from discord.ext import commands, tasks
import json
import asyncio

#
#this file here contains the basic unranked matchmaking system
#


#first we define the allowed channels here for the whole matchmaking system
arena_channels = (739299508403437626, 739299508403437627, 742190378051960932)
special_arenas = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)


class Matchmaking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #storing the matchmaking ping in the file
    async def store_ping(self, ctx, mm_type: str, timestamp: float):
        with open(r'./json/{filename}.json'.format(filename=mm_type), 'r') as f:
            user_pings = json.load(f)

        user_pings[f'{ctx.author.id}'] = {}
        user_pings[f'{ctx.author.id}'] = {"channel": ctx.channel.id, "time": timestamp}

        with open(r'./json/{filename}.json'.format(filename=mm_type), 'w') as f:
            json.dump(user_pings, f, indent=4)

    #deleting it again
    async def delete_ping(self, ctx, mm_type: str):
        with open(r'./json/{filename}.json'.format(filename=mm_type), 'r') as f:
            user_pings = json.load(f)

        try:
            del user_pings[f'{ctx.message.author.id}']
        except KeyError:
            print(f"tried to delete a {mm_type} ping but the deletion failed")

        with open(r'./json/{filename}.json'.format(filename=mm_type), 'w') as f:
            json.dump(user_pings, f, indent=4)


    #getting a list with all the recent pings
    async def get_recent_pings(self, mm_type: str, timestamp: float):
        with open(r'./json/{filename}.json'.format(filename=mm_type), 'r') as f:
            user_pings = json.load(f)

        list_of_searches = []

        for ping in user_pings:
            ping_channel = user_pings[f'{ping}']['channel']
            ping_timestamp = user_pings[f'{ping}']['time']

            difference = timestamp - ping_timestamp

            minutes = round(difference / 60)

            if minutes < 31:
                list_of_searches.append(f"<@!{ping}>, in <#{ping_channel}>, {minutes} minutes ago\n")

        list_of_searches.reverse()
        searches = ''.join(list_of_searches)

        if len(searches) == 0:
            searches = "Looks like no one has pinged recently :("

        return searches



    @commands.command(aliases=['matchmaking', 'matchmakingsingles', 'mmsingles', 'Singles'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def singles(self, ctx):
        timestamp = discord.utils.utcnow().timestamp()
        singles_role = discord.utils.get(ctx.guild.roles, id=739299507799326842)
        
        if ctx.message.channel.id in arena_channels:
            await self.store_ping(ctx, "singles", timestamp)
            
            searches = await self.get_recent_pings("singles", timestamp)

            embed = discord.Embed(
                title="Singles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_red())

            mm_message = await ctx.send(f"{ctx.author.mention} is looking for {singles_role.mention} games!", embed=embed)
            mm_thread = await mm_message.create_thread(name=f"Singles Arena of {ctx.author.name}", auto_archive_duration=60)

            await mm_thread.add_user(ctx.author)
            await mm_thread.send(f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent.")

            await asyncio.sleep(1800)

            await self.delete_ping(ctx, "singles")

            
        elif ctx.message.channel.id in special_arenas:
            searches = await self.get_recent_pings("singles", timestamp)

            embed = discord.Embed(
                title="Singles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_red())

            await ctx.send(f"{ctx.author.mention} is looking for {singles_role.mention} games!\nHere are the most recent Singles pings in our open arenas:", embed=embed)

        else:
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)

    @singles.error
    async def singles_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            timestamp = discord.utils.utcnow().timestamp()
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                searches = await self.get_recent_pings("singles", timestamp)

                embed = discord.Embed(
                    title="Singles pings in the last 30 Minutes:", 
                    description=searches, 
                    colour=discord.Colour.dark_red())

                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Singles pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        else:
            raise error



    @commands.command(aliases=['matchmakingdoubles', 'mmdoubles', 'Doubles'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def doubles(self, ctx):
        timestamp = discord.utils.utcnow().timestamp()
        doubles_role = discord.utils.get(ctx.guild.roles, id=739299507799326841)

        if ctx.message.channel.id in arena_channels:
            await self.store_ping(ctx, "doubles", timestamp)
            
            searches = await self.get_recent_pings("doubles", timestamp)

            embed = discord.Embed(
                title="Doubles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_blue())

            mm_message = await ctx.send(f"{ctx.author.mention} is looking for {doubles_role.mention} games!", embed=embed)
            mm_thread = await mm_message.create_thread(name=f"Doubles Arena of {ctx.author.name}", auto_archive_duration=60)

            await mm_thread.add_user(ctx.author)
            await mm_thread.send(f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent.")

            await asyncio.sleep(1800)

            await self.delete_ping(ctx, "doubles")

            
        elif ctx.message.channel.id in special_arenas:
            searches = await self.get_recent_pings("doubles", timestamp)

            embed = discord.Embed(
                title="Doubles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_blue())

            await ctx.send(f"{ctx.author.mention} is looking for {doubles_role.mention} games!\nHere are the most recent Doubles pings in our open arenas:", embed=embed)

        else:
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)

    @doubles.error
    async def doubles_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            timestamp = discord.utils.utcnow().timestamp()
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                searches = await self.get_recent_pings("doubles", timestamp)

                embed = discord.Embed(
                    title="Doubles pings in the last 30 Minutes:", 
                    description=searches, 
                    colour=discord.Colour.dark_blue())

                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Doubles pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        else:
            raise error


    @commands.command(aliases=['matchmakingfunnies', 'mmfunnies', 'Funnies'])
    @commands.cooldown(1, 600, commands.BucketType.user) #1 use, 10m cooldown, per user
    async def funnies(self, ctx):
        timestamp = discord.utils.utcnow().timestamp()
        funnies_role = discord.utils.get(ctx.guild.roles, id=739299507795132495)

        if ctx.message.channel.id in arena_channels:
            await self.store_ping(ctx, "funnies", timestamp)
            
            searches = await self.get_recent_pings("funnies", timestamp)

            embed = discord.Embed(
                title="Funnies pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.green())

            mm_message = await ctx.send(f"{ctx.author.mention} is looking for {funnies_role.mention} games!", embed=embed)
            mm_thread = await mm_message.create_thread(name=f"Funnies Arena of {ctx.author.name}", auto_archive_duration=60)

            await mm_thread.add_user(ctx.author)
            await mm_thread.send(f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent.")

            await asyncio.sleep(1800)

            await self.delete_ping(ctx, "funnies")

            
        elif ctx.message.channel.id in special_arenas:
            searches = await self.get_recent_pings("funnies", timestamp)

            embed = discord.Embed(
                title="Funnies pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.green())

            await ctx.send(f"{ctx.author.mention} is looking for {funnies_role.mention} games!\nHere are the most recent Funnies pings in our open arenas:", embed=embed)

        else:
            await ctx.send("Please only use this command in our arena channels!")
            ctx.command.reset_cooldown(ctx)

    @funnies.error
    async def funnies_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            timestamp = discord.utils.utcnow().timestamp()
            if ctx.message.channel.id in arena_channels or ctx.message.channel.id in special_arenas:
                searches = await self.get_recent_pings("funnies", timestamp)

                embed = discord.Embed(
                    title="Funnies pings in the last 30 Minutes:", 
                    description=searches, 
                    colour=discord.Colour.green())

                await ctx.send(f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent Funnies pings in our open arenas:", embed=embed)
            else:
                await ctx.send("Please only use this command in our arena channels!")
        else:
            raise error





def setup(bot):
    bot.add_cog(Matchmaking(bot))
    print("Matchmaking cog loaded")