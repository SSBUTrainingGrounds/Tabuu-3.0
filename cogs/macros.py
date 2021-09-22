import discord
from discord.ext import commands, tasks
import json


#
#this file here contains most macros, they all just link to stuff or send the same pre-made messages every time
#

class Macros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #listens for macros
    @commands.Cog.listener()
    async def on_message(self, message):
        with open(r'./json/macros.json', 'r') as f:
            macros = json.load(f)

        for name in macros:
            payload = macros[f'{name}']
            if len(message.content.split()) == 1 and message.content == (f"%{name}") or message.content.startswith(f"%{name} "):
                await message.channel.send(payload)


    #creates them and writes it to the json file
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createmacro(self, ctx, name, *, payload):
        with open(r'./json/macros.json', 'r') as f:
            macros = json.load(f)

        #converts them to only lower case
        name = name.lower()

        #every command registered
        command_list = [command.name for command in self.bot.commands]

        #basic checks for invalid stuff
        if name in macros:
            await ctx.send("This name was already taken. If you want to update this macro please delete it first and then create it again.")
            return
        
        if name in command_list:
            await ctx.send("This name is already being used for a command! Please use a different one.")
            return
        
        if len(name[50:]) > 0:
            await ctx.send("The name of this macro is too long! Please try again with a shorter name.")
            return

        if len(payload[1500:]) > 0:
            await ctx.send("The output of this macro would be too big to send! Please try again with a shorter output.")
            return

        macros[name] = payload
        
        with open(r'./json/macros.json', 'w') as f:
            json.dump(macros, f, indent=4)

        await ctx.send(f"New macro `{name}` was created. \nOutput: `{payload}`")


    #deletes the macros    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletemacro(self, ctx, name):
        with open(r'./json/macros.json', 'r') as f:
            macros = json.load(f)

        #needs to check if the macro exists obviously
        if name in macros:
            del macros[f'{name}']
        else:
            await ctx.send(f"The macro `{name}` was not found. Please try again.")
            return
        
        with open(r'./json/macros.json', 'w') as f:
            json.dump(macros, f, indent=4)

        await ctx.send(f"Deleted macro `{name}`")


    #lists the macros, no need for gating it behind admin perms
    @commands.command(aliases=['listmacro', 'macros', 'macro'])
    async def listmacros(self, ctx):
        with open(r'./json/macros.json', 'r') as f:
            macros = json.load(f)

        macro_list = []
        for name in macros:
            macro_list.append(name)

        await ctx.send(f"The registered macros are:\n`%{', %'.join(macro_list)}`")


    #the error handling for the above
    @createmacro.error
    async def createmacro_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input the macro name and then the desired output.")
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.send("Please do not create a macro with the `\"` letter. Use `'` instead.")
        elif isinstance(error, commands.UnexpectedQuoteError):
            await ctx.send("Please do not create a macro with the `\"` letter. Use `'` instead.")
        else:
            raise error
        
    @deletemacro.error
    async def deletemacro_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input the macro you want to delete.")
        else:
            raise error




    #below here are macros that are hard-coded. they may or may not be replaced by the system above in the future.
    #for now they remain here
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