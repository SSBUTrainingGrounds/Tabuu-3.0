import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta
import time


#
#this file holds the commands associated with the handling of matchmaking pings both ranked and unranked. recentpings with the dropdown and clearing of threads/mm pings
#


class Pings(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Singles', description='Singles Pings in the last 30 Minutes', emoji='🗡️'),
            discord.SelectOption(label='Doubles', description='Doubles Pings in the last 30 Minutes', emoji='⚔️'),
            discord.SelectOption(label='Funnies', description='Funnies Pings in the last 30 Minutes', emoji='😂'),
            discord.SelectOption(label='Ranked', description='Ranked Pings in the last 30 Minutes', emoji='🏆')
        ]

        super().__init__(placeholder='Which pings do you want to see?', min_values=1, max_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'Singles':
            timestamp = time.strftime("%H:%M")

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
            singles_embed = discord.Embed(title="Singles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_red())

            await interaction.response.send_message(embed=singles_embed, ephemeral=True)

        elif self.values[0] == 'Doubles':
            timestamp = time.strftime("%H:%M")
            
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
            doubles_embed = discord.Embed(title="Doubles pings in the last 30 Minutes:", description=searches, colour=discord.Colour.dark_blue())

            await interaction.response.send_message(embed=doubles_embed, ephemeral=True)

        elif self.values[0] == 'Funnies':
            timestamp = time.strftime("%H:%M")

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
            funnies_embed = discord.Embed(title="Funnies pings in the last 30 Minutes:", description=searches, colour=discord.Colour.green())

            await interaction.response.send_message(embed=funnies_embed, ephemeral=True)

        elif self.values[0] == 'Ranked':
            timestamp = time.strftime("%H:%M")

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
            ranked_embed = discord.Embed(title="Ranked pings in the last 30 Minutes:", description=searches, colour=discord.Colour.blue())

            await interaction.response.send_message(embed=ranked_embed, ephemeral=True)
            
        else:
            await interaction.response.send_message("Something went wrong! Please try again.", ephemeral=True)


class DropdownPings(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Pings())



class Matchmakingpings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.clear_mmrequests() #clears the mm files on bot startup, otherwise pings would get stuck in there forever when i shut the bot down

    #if a matchmaking thread gets inactive, it gets deleted right away to clear space
    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        arena_channels = (739299508403437626, 739299508403437627, 742190378051960932)
        ranked_arenas = (835582101926969344, 835582155446681620, 836018137119850557)
        if before.archived is False and after.archived is True:
            if after.parent_id in arena_channels or after.parent_id in ranked_arenas:
                await after.delete()



    @commands.command()
    async def recentpings(self, ctx):
        await ctx.send("Here are all available ping types:", view=DropdownPings())



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
        else:
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
    bot.add_cog(Matchmakingpings(bot))
    print("Matchmakingpings cog loaded")