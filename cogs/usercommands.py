import discord
from discord.ext import commands, tasks
import random
import asyncio


#
#this file here mostly contains various commands who dont fit into the other categories
#

class Usercommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #modmail
    @commands.command()
    async def modmail(self, ctx, *, args):
        if str(ctx.channel.type) == 'private': #only works in dm's
            guild = self.bot.get_guild(739299507795132486) #ssbu tg server
            modmail_channel = self.bot.get_channel(806860630073409567) #modmail channel
            mod_role = discord.utils.get(guild.roles, id=739299507816366106)

            atm = ''
            if ctx.message.attachments:
                atm = " , ".join([i.url for i in ctx.message.attachments])

            complete_message = f"**✉️ New Modmail {mod_role.mention}! ✉️**\nFrom: {ctx.author} \nMessage:\n{args} \n{atm}"

            #with the message attachments combined with the normal message lengths, the message can reach over 4k characters, but we can only send 2k at a time.
            if len(complete_message[4000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:4000])
                await modmail_channel.send(complete_message[4000:])
                await ctx.send("Your message has been sent to the Moderator Team. They will get back to you shortly.")

            elif len(complete_message[2000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:])
                await ctx.send("Your message has been sent to the Moderator Team. They will get back to you shortly.")

            else:
                await modmail_channel.send(complete_message)
                await ctx.send("Your message has been sent to the Moderator Team. They will get back to you shortly.")


        else:
            await ctx.message.delete()
            await ctx.send("For the sake of privacy, please only use this command in my DM's. They are always open for you.")
    

    #just returns the avatar of a user
    @commands.command(aliases=['icon'])
    async def avatar(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.send(member.display_avatar.url)

    #returns their banner
    @commands.command()
    async def banner(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        user = await self.bot.fetch_user(member.id) #we have to fetch the user first for whatever reason
        try:
            await ctx.send(user.banner.url) #if the user does not have a banner, we get an error referencing it
        except:
            await ctx.send("This user does not have a banner.")

    #makes a basic poll
    @commands.command()
    async def poll(self, ctx, question, *options: str):
        if len(options) < 2:
            await ctx.send("You need at least 2 options to make a poll!") #obviously
            return
        if len(options) > 10:
            await ctx.send("You can only have 10 options at most!") #reaction emoji limit
            return
        try:
            await ctx.message.delete()
        except:
            pass

        reactions = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','0️⃣'] #in order
        description = []

        for x, option in enumerate(options):
            description += f'\n{reactions[x]}: {option}' #adds the emoji: option to the embed
        embed = discord.Embed(title=question, description=''.join(description), colour=discord.Colour.dark_purple())
        embed.set_footer(text=f'Poll by {ctx.author}')
        embed_message = await ctx.send(embed=embed) #sends the embed out
        for reaction in reactions[:len(options)]: #and then reacts with the correct number of emojis
            await embed_message.add_reaction(reaction)


    #classic ping
    @commands.command()
    async def ping(self, ctx):
        pingtime=self.bot.latency * 1000
        await ctx.send(f"Ping: {round(pingtime)}ms")

    #generic coin toss
    @commands.command()
    async def coin(self, ctx):
        coin = ['Coin toss: **Heads!**', 'Coin toss: **Tails!**']
        await ctx.send(random.choice(coin))

    @commands.command()
    async def stagelist(self, ctx):
        await ctx.send(file=discord.File(r"./files/stagelist.png"))

    #neat dice roll
    @commands.command(aliases=['r'])
    async def roll(self, ctx, dice:str):
        try:
            amount, sides = map(int, dice.split('d'))
        except:
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
            return
        results = []
        if amount > 100:
            await ctx.send("Too many dice!")
            return
        if sides > 1000:
            await ctx.send("Too many sides!")
            return
        for r in range(amount):
            x = random.randint(1, sides)
            results.append(x)
        if len(results) == 1:
            await ctx.send(f"Rolling **1**-**{sides}** \nResult: **{results}**")
        else:
            await ctx.send(f"Rolling **1**-**{sides}** **{r+1}** times \nResults: **{results}** \nTotal: **{sum(results)}**")

    #generic countdown
    @commands.command()
    async def countdown(self, ctx, count:int):
        if count > 50:
            await ctx.send("Please don't use numbers that big.")
            return
        if count < 1:
            await ctx.send("Invalid number!")
            return
        
        initial_count = count

        countdown_message = await ctx.send(f"Counting down from {initial_count}...\n{count}")

        while count > 1:
            count -= 1
            await asyncio.sleep(2) #sleeps 2 secs instead of 1
            await countdown_message.edit(content=f"Counting down from {initial_count}...\n{count}") #edits the message with the new count

        await asyncio.sleep(2) #sleeps again before sending the final message
        await countdown_message.edit(content=f"Counting down from {initial_count}...\nFinished!")


    #info about an emoji
    @commands.command(aliases=['emoji'])
    async def emote(self, ctx, emoji:discord.PartialEmoji):
        embed = discord.Embed(title="Emoji Info", colour=discord.Colour.orange(), description=f"\
**Url:** {emoji.url}\n\
**Name:** {emoji.name}\n\
**ID:** {emoji.id}\n\
**Created at:** {discord.utils.format_dt(emoji.created_at, style='F')}\n\
            ")
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)

    #same but for stickers
    @commands.command()
    async def sticker(self, ctx):
        sticker = await ctx.message.stickers[0].fetch()
        embed = discord.Embed(title="Sticker Info", colour=discord.Colour.orange(), description=f"\
**Url:** {sticker.url}\n\
**Name:** {sticker.name}\n\
**ID:** {sticker.id}\n\
**Created at:** {discord.utils.format_dt(sticker.created_at, style='F')}\n\
            ")
        embed.set_image(url=sticker.url)
        await ctx.send(embed=embed)


    #returns the spotify status
    @commands.command()
    async def spotify(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        if not ctx.guild:
            await ctx.send("This command does not work in my DM channel.")
            return

        listeningstatus = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)

        if listeningstatus is None:
            await ctx.send("This user is not listening to Spotify right now or their account is not connected.")
        else:
            await ctx.send(f"https://open.spotify.com/track/{listeningstatus.track_id}")




    #error handling for the above
    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @banner.error
    async def banner_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a question, and then at least 2 options!")
        else:
            raise error


    @modmail.error
    async def modmail_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a message to the moderators. It should look something like:\n```%modmail (your message here)```")
        else:
            raise error

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
        else:
            raise error

    @countdown.error
    async def countdown_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a number!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid number!")
        else:
            raise error

    @emote.error
    async def emote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify an emoji!")
        elif isinstance(error, commands.PartialEmojiConversionFailure):
            await ctx.send("I couldn't find information on this emoji! Make sure this is not a default emoji.")
        else:
            raise error

    @sticker.error
    async def sticker_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I could not find any information on this sticker!")
        else:
            raise error

    @spotify.error
    async def spotify_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error



def setup(bot):
    bot.add_cog(Usercommands(bot))
    print("Usercommands cog loaded")