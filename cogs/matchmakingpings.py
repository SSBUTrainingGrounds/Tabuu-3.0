import discord
from discord.ext import commands, tasks
import json
from .matchmaking import Matchmaking
from .ranking import Ranking
from utils.ids import TGArenaChannelIDs
import utils.logger


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
            timestamp = discord.utils.utcnow().timestamp()

            searches = await Matchmaking.get_recent_pings(self, "singles", timestamp)

            singles_embed = discord.Embed(
                title="Singles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_red())

            await interaction.response.send_message(embed=singles_embed, ephemeral=True)

        elif self.values[0] == 'Doubles':
            timestamp = discord.utils.utcnow().timestamp()
            
            searches = await Matchmaking.get_recent_pings(self, "doubles", timestamp)
            
            doubles_embed = discord.Embed(
                title="Doubles pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.dark_blue())

            await interaction.response.send_message(embed=doubles_embed, ephemeral=True)

        elif self.values[0] == 'Funnies':
            timestamp = discord.utils.utcnow().timestamp()

            searches = await Matchmaking.get_recent_pings(self, "funnies", timestamp)
            
            funnies_embed = discord.Embed(
                title="Funnies pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.green())

            await interaction.response.send_message(embed=funnies_embed, ephemeral=True)

        elif self.values[0] == 'Ranked':
            timestamp = discord.utils.utcnow().timestamp()

            searches = await Ranking.get_recent_ranked_pings(self, timestamp)

            ranked_embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:", 
                description=searches, 
                colour=discord.Colour.blue())

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

        self.clear_mmrequests()


    #if a matchmaking thread gets inactive, it gets deleted right away to clear space
    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        if before.archived is False and after.archived is True:
            if after.parent_id in TGArenaChannelIDs.PUBLIC_ARENAS or after.parent_id in TGArenaChannelIDs.RANKED_ARENAS:
                await after.delete()


    @commands.command()
    async def recentpings(self, ctx):
        await ctx.send("Here are all available ping types:", view=DropdownPings())



    @commands.command(aliases=['clearmmrequests', 'clearmm', 'clearmatchmaking'])
    @commands.has_permissions(administrator=True)
    async def clearmmpings(self, ctx):
        await self.clear_mmrequests()
        await ctx.send("Cleared the matchmaking pings!")

    @clearmmpings.error
    async def clearmmpings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error



    #this clears the mm files so that no ping gets stuck if i restart the bot
    def clear_mmrequests(self):
        logger = utils.logger.get_logger("bot.mm")
        logger.info("Starting to delete pings in the matchmaking files...")

        #deleting singles file

        with open(r'./json/singles.json', 'r') as f:
            singles = json.load(f)
        
        singles_requests = []

        for user in singles:
            singles_requests.append(user)

        for user in singles_requests:
            del singles[user]
        
        with open(r'./json/singles.json', 'w') as f:
            json.dump(singles, f, indent=4)

        logger.info("Singles file cleared!")

        #deleting doubles file

        with open(r'./json/doubles.json', 'r') as f:
            doubles = json.load(f)
        
        doubles_requests = []

        for user in doubles:
            doubles_requests.append(user)

        for user in doubles_requests:
            del doubles[user]
        
        with open(r'./json/doubles.json', 'w') as f:
            json.dump(doubles, f, indent=4)

        logger.info("Doubles file cleared!")

        #deleting funnies file

        with open(r'./json/funnies.json', 'r') as f:
            funnies = json.load(f)
        
        funnies_requests = []

        for user in funnies:
            funnies_requests.append(user)

        for user in funnies_requests:
            del funnies[user]
        
        with open(r'./json/funnies.json', 'w') as f:
            json.dump(funnies, f, indent=4)

        logger.info("Funnies file cleared!")

        #deleting ranked file

        with open(r'./json/rankedpings.json', 'r') as f:
            ranked = json.load(f)
        
        ranked_requests = []
        
        for user in ranked:
            ranked_requests.append(user)
        
        for user in ranked_requests:
            del ranked[user]
        
        with open(r'./json/rankedpings.json', 'w') as f:
            json.dump(ranked, f, indent=4)

        logger.info("Ranked file cleared!")



def setup(bot):
    bot.add_cog(Matchmakingpings(bot))
    print("Matchmakingpings cog loaded")