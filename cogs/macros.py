import discord
from discord.ext import commands, tasks


#
#this file here contains most macros, they all just link to stuff or send the same pre-made messages every time
#

class Macros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #invite link
    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Here's the invite link to our server: https://discord.gg/ssbutg") #if this link expires, change it

    #coaching info
    @commands.command()
    async def coaching(self, ctx):
        await ctx.send("It seems like you are looking for coaching: make sure to tell us what exactly you need so we can best assist you!\n\n1. Did you specify which character you need help with?\n2. Are you looking for general advice, character-specific advice, both?\n3. How well do you understand general game mechanics on a scale of 1-5 (1 being complete beginner and 5 being knowledgeable)?\n4. Region?\n5. What times are you available?\n\nPlease keep in mind if you are very new to the game or have a basic understanding, it is recommended to first learn more via resources like Izaw's Art of Smash series (which you can find on YouTube) or other resources we have pinned in <#739299508403437621>.")

    #links to our calendar
    @commands.command(aliases=['calender', 'calandar', 'caIendar'])
    async def calendar(self, ctx): #the basic schedule for our server
        await ctx.send("https://calendar.google.com/calendar/embed?src=ssbu.traininggrounds%40gmail.com&ctz=America%2FNew_York")

    #links to the power ranking, keep updated every now and then
    @commands.command()
    async def pr(self, ctx):
        await ctx.send("https://braacket.com/league/SSBU_TG5")

    #links to our resource document
    @commands.command()
    async def resources(self, ctx):
        await ctx.send("https://docs.google.com/document/d/1JfxnXHLe0-rW-Z6sEjLQzB1puDsVP0UtOvaXz_EEXqE")

    #pic with our stagelist on it, change file when it changes
    @commands.command()
    async def stagelist(self, ctx):
        await ctx.send(file=discord.File(r"./files/stagelist.png")) 



    #our streamers use these shortcuts to promote their streams
    @commands.command()
    async def streamer(self, ctx):
        await ctx.send("Streamer commands: \n%neon, %scrooge, %tabuu, %xylenes, %tgstream") #needs updating every once in a while

    @commands.command()
    async def neon(self, ctx):
        await ctx.send("https://www.twitch.tv/neonsurvivor")

    @commands.command()
    async def scrooge(self, ctx):
        await ctx.send("https://www.twitch.tv/scroogemcduk")
    
    @commands.command()
    async def tabuu(self, ctx):
        await ctx.send("https://www.twitch.tv/therealtabuu")

    @commands.command()
    async def xylenes(self, ctx):
        await ctx.send("https://www.twitch.tv/FamilyC0mputer")

    @commands.command()
    async def tgstream(self, ctx):
        await ctx.send("https://www.twitch.tv/ssbutraininggrounds")



def setup(bot):
    bot.add_cog(Macros(bot))
    print("Macros cog loaded")