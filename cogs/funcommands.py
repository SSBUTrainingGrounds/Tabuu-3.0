import discord
from discord.ext import commands, tasks
import random

#
#this file here contains all of the 'funny' commands, they all just trigger random responses
#

class Funcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def uwu(self, ctx):
        messages = ["Stop this, you're making a fool of yourself",
        "Take a break from the internet",
        "Why do you exist?"]
        await ctx.send(random.choice(messages))

    @commands.command()
    async def tabuwu(self, ctx):
        messages = ["Stop this, you're making a fool of yourself",
        "Take a break from the internet",
        "Why do you exist?"]
        await ctx.send(random.choice(messages))

    @commands.command(aliases=['joke'])
    async def tabuujoke(self, ctx):
        messages = ["I invented a new word! Plagiarism!",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus.",
        "It takes guts to be an organ donor.",
        "What do you call a band of Tabuus? The Blue Man Group! I'm sorry.",
        "the_ultimate_bruh#0182",
        "What do you call a belt made of watches? A waist of time",
        "Did you hear about the new high-tech broom? It's sweeping the nation!"]
        await ctx.send(random.choice(messages))

    @commands.command()
    async def randomquote(self, ctx):
        messages = ['"Life isn\'t about waiting for the storm to pass. It\'s about learning to dance in the rain" ~ (UNKNOWN)',
        '"The difference between stupidity and genius is that genius has its limits" ~ Albert Einstein']
        await ctx.send(random.choice(messages))

    @commands.command()
    async def pickmeup(self, ctx): 
        messages = ["You are beautiful",
        "You got this! Don't give up, I believe in you.",
        "Watch this, you lovely user. It might help. https://www.youtube.com/watch?v=kGOQfLFzJj8"]
        item = random.choice(messages)
        await ctx.send(item)

    @commands.command()
    async def wisdom(self, ctx):
        messages = ['"Everything around you that you call life was made up by people that were no smarter than you, and you can change it. You can influence it. You can build your own things that other people can use." - Steve Jobs',
        'Sleep is the biggest key to success in anything you\'ll do.',
        'If you\'re having any trouble, inhale asbestos. Please do the opposite of what i said. Don\'t inhale asbestos. I love you.']
        await ctx.send(random.choice(messages))

    @commands.command()
    async def boo(self, ctx):
        messages = ['Looking for a scare, huh... TAXES Oooooh very scary',
        'Looking for a scare, huh... BIG DISJOINTS Oooooh super scary',
        'Looking for a scare, huh... NINTENDO SWITCH ONLINE Oooooh hella scary']
        await ctx.send(random.choice(messages))

    @commands.command()
    async def john(self, ctx):
        messages = ['I only lost cause my sister got me a god damn fucking McFlurry',
        'I only lost cause my router called me mean names',
        'I only lost cause I dont care for this stupid game anymore',
        'There is no johns, I lost fair and square',
        'I only lost cause Tabuu gave me second hand smoke',
        'I only lost cause I put my foot on the desk again and it disconnected my lan',
        'I only lost cause Arto burned down my freaking house mid-set',
        'I only lost cause sharpen was making too much noise in my basement',
        'I only lost because i got weirdganted',
        'I only lost cause my slime controller got drift',
        'I only lost cause i was distracted by ewan explaining scottish independence to me',
        'I only lost cause I got muted mid-set',
        'I only lost because I was trying to get pinned in #number-chain',
        'i only lost cause arto accidentally banned me from this server',
        'i only lost cause ewans bald head was blinding me',
        'I only lost because I didn’t DI away from plats',
        'I only lost cause spoon pinged everyone again',
        'I only lost because someone pinged %singles in our arena midmatch']
        await ctx.send(random.choice(messages))




def setup(bot):
    bot.add_cog(Funcommands(bot))
    print("Funcommands cog loaded")