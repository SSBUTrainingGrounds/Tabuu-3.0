import discord
from discord.ext import commands
import random


class RpsButtons(discord.ui.View):
    """
    Contains the RPS Game Buttons.
    Made this its own cog because of this Button subclass,
    which does take over quite some space.
    """

    def __init__(self, ctx, member):
        super().__init__()
        self.ctx = ctx
        self.member = member
        self.authorchoice = None
        self.memberchoice = None
        # set it to 1 min, default one was 3 mins thought that was a bit too long
        self.timeout = 60

    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.gray)
    async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Registers the author and user input for Rock.
        Stops if both parties made a choice.
        I dont know why the Rock Emoji doesnt display properly here btw,
        it does on Discord.
        """
        await interaction.response.send_message("You chose Rock!", ephemeral=True)
        if interaction.user.id == self.ctx.author.id:
            self.authorchoice = "Rock"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Rock"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Paper", emoji="📝", style=discord.ButtonStyle.gray)
    async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Registers the author and user input for Paper.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Paper!", ephemeral=True)
        if interaction.user.id == self.ctx.author.id:
            self.authorchoice = "Paper"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Paper"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.gray)
    async def scissors(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """
        Registers the author and user input for Scissors.
        Stops if both parties made a choice.
        """
        await interaction.response.send_message("You chose Scissors!", ephemeral=True)
        if interaction.user.id == self.ctx.author.id:
            self.authorchoice = "Scissors"
        if interaction.user.id == self.member.id:
            self.memberchoice = "Scissors"
        if self.authorchoice is not None and self.memberchoice is not None:
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        # basically ignores every other member except the author and mentioned member
        if interaction.user == self.member or interaction.user == self.ctx.author:
            return True
        else:
            return False


class Rpsgame(commands.Cog):
    """
    Contains the command to execute the RPS Game.
    """

    def __init__(self, bot):
        self.bot = bot

    # never heard of those alternate names but wikipedia says they exist so might as well add them
    @commands.command(aliases=["rockpaperscissors", "rochambeau", "roshambo"])
    async def rps(self, ctx, member: discord.Member = None):
        """
        Plays a Game of Rock, Paper, Scissors with either a mentioned user,
        or my bot, if you do not mention a user.
        """
        if member is None:
            member = self.bot.user

        # basic checks for users
        if member == ctx.author:
            await ctx.send("Please don't play matches with yourself.")
            return

        if member.bot and member.id != self.bot.user.id:
            await ctx.send(
                "Please do not play with other bots, they are too predictable."
            )
            return

        view = RpsButtons(ctx, member)
        init_message = await ctx.send(
            f"Rock, Paper, Scissors: \n{ctx.author.name} vs {member.name}\nChoose wisely:",
            view=view,
        )

        # if the bot plays it just chooses randomly
        if member.id == self.bot.user.id:
            view.memberchoice = random.choice(["Rock", "Paper", "Scissors"])

        # waits for the button to stop or timeout
        await view.wait()

        # checks the results
        # if its the same we can just call it off here,
        # need a check if one of the responses is not none for the error message below
        if view.authorchoice == view.memberchoice and view.authorchoice is not None:
            await init_message.reply(
                f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**It's a draw!**"
            )
            return

        author_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {ctx.author.mention}!**"
        member_winner_message = f"{ctx.author.mention} chose {view.authorchoice}!\n{member.mention} chose {view.memberchoice}!\n**The winner is: {member.mention}!**"

        # since draws are already ruled out the rest of the logic isnt too bad, still a whole lot of elif statements though
        if view.authorchoice == "Rock" and view.memberchoice == "Paper":
            await init_message.reply(member_winner_message)
        elif view.authorchoice == "Rock" and view.memberchoice == "Scissors":
            await init_message.reply(author_winner_message)
        elif view.authorchoice == "Paper" and view.memberchoice == "Rock":
            await init_message.reply(author_winner_message)
        elif view.authorchoice == "Paper" and view.memberchoice == "Scissors":
            await init_message.reply(member_winner_message)
        elif view.authorchoice == "Scissors" and view.memberchoice == "Rock":
            await init_message.reply(member_winner_message)
        elif view.authorchoice == "Scissors" and view.memberchoice == "Paper":
            await init_message.reply(author_winner_message)

        # if the match didnt go through as planned:
        elif view.authorchoice is None and view.memberchoice is None:
            await init_message.reply(
                f"Match timed out! Both parties took too long to pick a choice!"
            )
        elif view.authorchoice is None:
            await init_message.reply(
                f"Match timed out! {ctx.author.mention} took too long to pick a choice!"
            )
        elif view.memberchoice is None:
            await init_message.reply(
                f"Match timed out! {member.mention} took too long to pick a choice!"
            )

        # and the fallback
        else:
            await init_message.reply(f"Something went wrong! Please try again.")

    # basic error handling
    @rps.error
    async def rps_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Rpsgame(bot))
    print("Rpsgame cog loaded")
