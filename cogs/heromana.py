from discord.ext import commands


class Heromana(commands.Cog):
    """
    Contains the Hero Mana Commands.
    They all just return the amount of Mana used for X move.
    Very self-explanatory.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mp4acceleratle(self, ctx):
        await ctx.send("The MP cost for *Acceleratle* is 13 MP.")

    @commands.command()
    async def mp4psycheup(self, ctx):
        await ctx.send("The MP cost for *Psyche Up* is 14 MP.")

    @commands.command()
    async def mp4oomph(self, ctx):
        await ctx.send("The MP cost for *Oomph* is 16 MP.")

    @commands.command()
    async def mp4whack(self, ctx):
        await ctx.send("The MP cost for *Whack* is 10 MP.")

    @commands.command()
    async def mp4thwack(self, ctx):
        await ctx.send("The MP cost for *Thwack* is 30 MP.")

    @commands.command()
    async def mp4sizz(self, ctx):
        await ctx.send("The MP cost for *Sizz* is 8 MP.")

    @commands.command()
    async def mp4bang(self, ctx):
        await ctx.send("The MP cost for *Bang* is 9 MP.")

    @commands.command()
    async def mp4kaboom(self, ctx):
        await ctx.send("The MP cost for *Kaboom* is 37 MP.")

    @commands.command()
    async def mp4magicburst(self, ctx):
        await ctx.send("The MP cost for *Magic Burst* is all MP.")

    @commands.command()
    async def mp4snooze(self, ctx):
        await ctx.send("The MP cost for *Snooze* is 16 MP.")

    @commands.command()
    async def mp4flameslash(self, ctx):
        await ctx.send("The MP cost for *Flame Slash* is 12 MP.")

    @commands.command()
    async def mp4kacrackleslash(self, ctx):
        await ctx.send("The MP cost for *Kacrackle Slash* is 11 MP.")

    @commands.command()
    async def mp4kamikazee(self, ctx):
        await ctx.send("The MP cost for *Kamikazee* is 1 MP.")

    @commands.command()
    async def mp4bounce(self, ctx):
        await ctx.send("The MP cost for *Bounce* is 14 MP.")

    @commands.command()
    async def mp4hocuspocus(self, ctx):
        await ctx.send(
            "The MP cost for *Hocus Pocus* is 4 MP (unless Magic Burst or MP is completely refilled/depleted)."
        )

    @commands.command()
    async def mp4heal(self, ctx):
        await ctx.send("The MP cost for *Heal* is 7 MP.")

    @commands.command()
    async def mp4zoom(self, ctx):
        await ctx.send("The MP cost for *Zoom* is 8 MP.")

    @commands.command()
    async def mp4hatchetman(self, ctx):
        await ctx.send("The MP cost for *Hatchet Man* is 15 MP.")

    @commands.command()
    async def mp4kaclang(self, ctx):
        await ctx.send("The MP cost for *Kaclang* is 6 MP.")

    @commands.command()
    async def mp4metalslash(self, ctx):
        await ctx.send("The MP cost for *Metal Slash* is 6 MP.")

    @commands.command()
    async def mp4frizz(self, ctx):
        await ctx.send("The MP cost for *Frizz* is 6 MP.")

    @commands.command()
    async def mp4frizzle(self, ctx):
        await ctx.send("The MP cost for *Frizzle* is 16 MP.")

    @commands.command()
    async def mp4kafrizz(self, ctx):
        await ctx.send("The MP cost for *Kafrizz* is 36 MP.")

    @commands.command()
    async def mp4zap(self, ctx):
        await ctx.send("The MP cost for *Zap* is 8 MP.")

    @commands.command()
    async def mp4zapple(self, ctx):
        await ctx.send("The MP cost for *Zapple* is 18 MP.")

    @commands.command()
    async def mp4kazap(self, ctx):
        await ctx.send("The MP cost for *Kazap* is 42 MP.")

    @commands.command()
    async def mp4woosh(self, ctx):
        await ctx.send("The MP cost for *Woosh* is 5 MP.")

    @commands.command()
    async def mp4swoosh(self, ctx):
        await ctx.send("The MP cost for *Swoosh* is 9 MP.")

    @commands.command()
    async def mp4kaswoosh(self, ctx):
        await ctx.send("The MP cost for *Kaswoosh* is 18 MP.")


async def setup(bot):
    await bot.add_cog(Heromana(bot))
    print("Heromana cog loaded")
