import random
from math import floor

import discord
from discord import app_commands
from discord.ext import commands

from utils.ids import GuildIDs


class Funcommands(commands.Cog):
    """Contains the "funny" commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(aliases=["uwu"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def tabuwu(self, ctx: commands.Context) -> None:
        """Well..."""

        messages = [
            "Stop this, you're making a fool of yourself",
            "Take a break from the internet",
            "Why do you exist?",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command(aliases=["tabuujoke"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def joke(self, ctx: commands.Context) -> None:
        """Jokes. May or may not make you laugh."""

        messages = [
            "I invented a new word! Plagiarism!",
            "?v cloud bair",
            "What's the best thing about Switzerland?\nI don't know, but the flag is a big plus.",
            "It takes guts to be an organ donor.",
            "What do you call a band of Tabuus?\nThe Blue Man Group! I'm sorry.",
            "What do you call a belt made of watches?\nA waist of time",
            "Did you hear about the new high-tech broom?\nIt's sweeping the nation!",
            "You know, working in a mirror factory is something I could really see myself doing",
            "I broke my hand last week, but on the other hand, I'm ok",
            "Did you hear about the new restaurant on the moon?\nThe food is great, but it has no atmosphere!",
            "What do sprinters eat before a race?\nNothing, they fast",
            "What's the difference between a regular joke and a dad joke?\nIt should be a-parent",
            "I took the shell off my racing snail to try to make him go faster.\nIt just made him more slug-ish",
            "Why did the chicken go to the seance?\nTo get to the other side",
            "When does a joke become a dad joke?\nWhen the punchline becomes a parent",
            "I recently bought some perfume, but it didn't smell like anything.\nIt made no scents.",
            "Why does a clock break when it gets hungry?\nIt goes back four seconds.",
            "What's the problem with eating a clock?\nIt's very time consuming!",
            "I used to love my job collecting leaves.\nI was raking it in!",
            "To the person who invented 0: Thanks for nothing!",
            "What do you call a magic dog?\nA Labra-cadabra-dor.",
            "Whats a windmill's favorite music?\nI don't know, but it's a big metal fan.",
            "How do rabbits travel?\nBy Hareplane!",
            "Where do sharks like to go on vacation?\nFinland!",
            "Where do hamsters like to go on vacation?\nHamsterdam!",
            "Where do bees like to go on vacation?\nStingapore!",
            "Where do sheep like to go on vacation?\nThe Baa-hamas!",
            "Where do cows like to go on vacation?\nMoo York!",
            "That car looks nice, but the muffler seems exhausted.",
            "What country's capital is growing the fastest?\nIreland, every day it's Dublin!",
            "I made a pencil with two erasers.\nIt was pointless.",
            "How do celebs stay cool in the summer?\nThey have many fans!",
            "What kind of car do sheep drive?\nA lamb-orghini!",
            "What did the accountants say while auditing?\nThis is taxing!",
            "Where do kings get crowned?\nOn their head!",
            "Why did king arthur go to the dentist?\nTo get his teeth crowned!",
            "Did you hear about the restaurant on the moon?\nThe food is good, but there's no atmosphere!",
            "Did you hear about the antennas that got married?\nThe wedding was good, but the reception was amazing!",
            "What is corn's favorite day?\nNew ears day!",
            "What is a cow's favorite day?\nMoo years eve!",
            "Who performs surgery underwater?\nA Sturgeon!",
            "A Friend of mine dug a hole in the garden and filled it with water.\nI think he meant well.",
            "I Ordered a chicken and an egg. I'll let you know which comes first.",
            "Did you know Cheese is the most humble of dairy products?\nIt's the most grate-ful!",
            "I was going to tell a joke about pizza, but it's a little cheesy.",
            "Singing in the shower is fun until you get soap in your mouth.\nThen it's a soap opera!",
            "I know some jokes about umbrellas, but they usually go over people's heads.",
            "What did the raindrop feel when it hit the window?\nThe Pane!",
            "What is drinking water's favorite dance?\nTap!",
            "I'm reading a book about anti-gravity.\nIt's impossible to put it down!",
            "How do we know flowers are friendly in the spring?\nThey have a lot of new buds!",
            "Can bees fly in the rain?\nNot without their yellow jacket!",
            "What is a rabbit's favorite bedtime story?\nOne with a hoppy ending!",
            "What did the doctor say to the skeleton with a temperature of 102?\nLooks like you're running a femur!",
            "Why don't skeletons like spicy food?\nThey don't have the stomach for it!",
            "How much fun is it to wash clothes?\nLoads!",
            "Why are poker players good at laundry?\nThey know how to fold em!",
            "What detergent does the little mermaid use?\nTide!",
            "How much does the combined laundry of white house weigh?\nA Washing-ton!",
            "A child saw her dad fall over while he was carrying laundry. She watched it all unfold.",
            "What's the best music for fishing?\nSomething catchy!",
            "How did the pirate get his ship so cheap?\nIt was on sail!",
            "What's the best kind of bird to work for construction?\nA crane!",
            "Do you know what cows read every day?\nThe moos-paper!",
            "Do you know what the apple said to the kangaroo?\nNothing, apples can't talk."
            "A woman Spilled her scrabble set on the road. She turned and asked me 'What's the word on the street?,",
            "What do chickens drive?\nA Coop!",
            "Where do Dogs park?\nIn the barking lot!",
            "Motherhood is a fairy tale in reverse. You start in a beautiful gown and end up cleaning up everyone's messes.",
            "Why did the cookie cry?\nHis mom was a wafer too long!",
            "What is a parade of bunnies hopping backwards called?\nA receding hare-line!",
            "What did the wind turbine say to the engineer?\nI'm a big fan of your work!",
            "How do you stop newspapers from flying away?\nUse a news anchor!",
            "Why is there so much wind in the sports stadium?\nBecause of all the fans!",
            "Why are basketball  players afraid of summer vacation?\nThey don't want to get called for travelling!",
            "What did the bees say during the heatwave?\nBoy it's swarm!",
            "What do you do if you get rejected when trying to get a job at the sunscreen company?\nReapply!",
            "What do you call a funny mountain?\nHill-arious!",
            "How does the moon cut his hair?\nE-clips-it!",
            "The baby corn asked the mama corn 'Where's pop-corn?'",
            "The waiter asked me 'Do you wanna box for your leftovers?'\nI said 'No, but I'll arm wrestle you for them.'",
            "Did you know it's illegal to laugh loudly in Hawaii?\nYou have to keep it to a-low-ha!",
            "How much room does it take for fungi to grow?\nAs mush space as necessary!",
            "||Help I'm trapped in a joke command!||",
            "Why couldn't the sesame seed leave the casino?\nIt was on a roll!",
            "How fast is milk?\nIt's pasteurize before you know it!",
            "What kind of music are balloons afraid of?\nPop music!",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def john(self, ctx: commands.Context) -> None:
        """Random excuse why you lost the last Game of Smash."""

        messages = [
            "I only lost cause my router called me mean names",
            "I only lost cause I dont care for this stupid game anymore",
            "There is no johns, I lost fair and square",
            "I only lost cause Tabuu gave me second hand smoke",
            "I only lost cause I put my foot on the desk again and it disconnected my lan",
            "I only lost cause Arto burned down my freaking house mid-set",
            "I only lost because i got weirdganted",
            "I only lost cause my slime controller got drift",
            "I only lost cause I got muted mid-set",
            "I only lost because I was trying to get pinned in #number-chain",
            "I only lost cause arto accidentally banned me from this server",
            "I only lost because I didn't DI away from plats",
            "I only lost cause spoon pinged everyone again",
            "I only lost because someone pinged %singles in our arena midmatch",
            "I only lost cause ewans bald head was blinding me",
            "I only lost cause i was distracted by ewan explaining scottish independence to me",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def hypemeup(self, ctx: commands.Context) -> None:
        """Hypes you up for the next Game of Smash."""

        messages = [
            "Whose better than you? \nNobody. That's who.",
            "This is your day to shine!",
            "Get ready to clip this one!",
            "Nobody does it like you!",
            "If you wanna be the best you gotta beat the best!",
            "If anyone can do it, it's you!",
            "Never back down from a challenge!",
            "Make this game legendary!",
            "Go out there and GET. THOSE. CLIPS. 👏",
            "See you in grand finals!",
            "Whoa now, leave some stocks for the rest of us!",
            "They're gonna remember this one!",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command(name="8ball")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(question="Your question to the magic 8ball.")
    async def _8ball(self, ctx: commands.Context, *, question: str = None) -> None:
        """Ask the magic 8ball."""

        if question is None:
            await ctx.send("Please input a question for the magic 8-ball.")
            return

        messages = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        question = discord.utils.remove_markdown(question)

        try:
            await ctx.send(
                f"{ctx.author.mention} asked: `{question}`:\n{random.choice(messages)}"
            )
        # This is in the case if a user inputs a question with more than 2000 chars in length,
        # the bot cant respond with the question.
        except discord.HTTPException:
            await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(question="Your question.")
    async def who(self, ctx: commands.Context, *, question: str = None) -> None:
        """Returns a random online member of the server as a response."""

        if ctx.guild is None:
            await ctx.send("You cannot use this command in my DM channel.")
            return

        if question is None:
            await ctx.send("Please input a question so I can look for the right user.")
            return

        question = discord.utils.remove_markdown(question)

        # Only gets online members.
        online_members = [
            member
            for member in ctx.guild.members
            if member.status != discord.Status.offline
        ]
        user = random.choice(online_members)
        try:
            await ctx.send(
                f"{ctx.author.mention} asked: `Who {question}`:\n{discord.utils.escape_markdown(str(user))}"
            )
        except discord.HTTPException:
            await ctx.send(discord.utils.escape_markdown(str(user)))

    @commands.hybrid_command(aliases=["ship", "relationship"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user1="The first user.",
        user2="The second user, leave empty to compare to yourself.",
    )
    async def friendship(
        self, ctx: commands.Context, user1: discord.User, user2: discord.User = None
    ) -> None:
        """The friendship status between two users."""
        if not user2:
            user2 = ctx.author

        # The relationship between you and yourself should always be 100, of course.
        rating = 100 if user1.id == user2.id else (user1.id + user2.id) % 100

        message = ("█" * floor(rating / 5)).ljust(20, "░")

        emojis = [
            "😡",
            "😠",
            "🙄",
            "😒",
            "😐",
            "🙂",
            "😀",
            "😄",
            "😁",
            "🥰",
            "😍",
        ]

        await ctx.send(
            f"The friendship status of {discord.utils.escape_markdown(user1.name)} "
            f"and {discord.utils.escape_markdown(user2.name)} is...\n"
            f"**{message} - {rating}%** {emojis[floor(rating / 10)] * 3}"
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def parzcoin(self, ctx: commands.Context) -> None:
        amount = random.randint(100, 999)
        percent = random.randint(0, 100)
        direction = random.choice(["UP 📈", "DOWN 📉"])

        await ctx.send(
            f"Parz Coin is {direction} {percent}% in the last hour!\nCurrent worth: 0.00000000{amount} USD"
        )


async def setup(bot) -> None:
    await bot.add_cog(Funcommands(bot))
    print("Funcommands cog loaded")
