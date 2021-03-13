import discord
from discord.ext import commands, tasks
import random
import difflib
from discord.utils import get

#
#this file here contains most useful commands that don't need special permissions
#

class Usercommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command() #some basic info about a role
    async def roleinfo(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role))
        except:
            closest_role = difflib.get_close_matches(input_role, all_roles)
            role1 = closest_role[0]
            role = get(ctx.guild.roles, name=role1)

        #the above block searches all roles for the closest match, as seen in the admin cog

        creationdate = role.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p")
        embed = discord.Embed(color = discord.Color.light_gray())
        embed.add_field(name="Role Name:", value=role.mention, inline=True)
        embed.add_field(name="Role ID:", value=role.id, inline=True)
        embed.add_field(name="Users with role:", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable:", value=role.mentionable, inline=True)
        embed.add_field(name="Displayed Seperately:", value=role.hoist, inline=True)
        embed.add_field(name="Color:", value=role.color, inline=True)
        embed.set_footer(text=f"Role created at: {creationdate}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['listroles']) #lists every member in the role if there arent more than 60 members, to prevent spam
    async def listrole(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role))
        except:
            closest_role = difflib.get_close_matches(input_role, all_roles)
            role1 = closest_role[0]
            role = get(ctx.guild.roles, name=role1)

        members = role.members
        memberlist = []

        if len(members) > 60:
            await ctx.send("Too many members to list")
            return
        if len(members) == 0:
            await ctx.send(f"No user currently has the {role} role!")
            return
        else:
            for member in members:
                memberlist.append(f"{member.name}#{member.discriminator}")
            all_members = ', '.join(memberlist)
            await ctx.send(f"Users with the {role} role:\n{all_members}")


    #modmail
    @commands.command()
    async def modmail(self, ctx, *, args):
        if str(ctx.channel.type) == 'private': #only works in dm's
            guild = self.bot.get_guild(739299507795132486) #ssbu tg server
            modmail_channel = self.bot.get_channel(806860630073409567) #modmail channel
            mod_role = discord.utils.get(guild.roles, name="「Grounds Warrior」")
            await modmail_channel.send(f"**✉️ New Modmail {mod_role.mention}! ✉️**\nFrom: {ctx.author} \nMessage:\n{args}")
            await ctx.send("Your message has been sent to the Moderator Team. They will get back to you shortly.")


        else:
            await ctx.message.delete()
            await ctx.send("For the sake of privacy, please only use this command in my DM's. They are always open for you.")
    

    #serverinfo, gives out basic info about the server
    @commands.command(aliases=['serverinfo'])
    async def server(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title=f"{server.name}({server.id})", color=discord.Color.green())
        embed.add_field(name="Created at:", value=server.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p CET"), inline=True) #same as above
        embed.add_field(name="Owner:", value=server.owner.mention, inline=True)
        embed.add_field(name="Channels:", value=len(server.channels), inline=True)
        embed.add_field(name="Members:", value=f"{sum(not member.bot for member in server.members)} (Bots: {sum(member.bot for member in server.members)})")
        embed.add_field(name="Emojis:", value=len(server.emojis))
        embed.add_field(name="Roles:", value=len(server.roles))
        embed.set_thumbnail(url=server.icon_url)
        await ctx.send(embed=embed)

    #userinfo
    @commands.command(aliases=['user'])
    async def userinfo(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        embed=discord.Embed()
        embed = discord.Embed(title="Userinfo of {}".format(member.name), color=discord.Color.dark_gold())
        embed.add_field(name="Name:", value=member.name, inline=True)
        embed.add_field(name="ID:", value=member.id, inline=True)
        embed.add_field(name="Number of Roles:", value=len(member.roles), inline=True) #gives the number of roles to prevent listing like 35 roles
        embed.add_field(name="Top Role:", value=member.top_role.mention, inline=True) #instead only gives out the important role
        embed.add_field(name="Joined Server at:", value=member.joined_at.strftime("%A, %B %d %Y @ %H:%M:%S %p"), inline=True) #the strftime and so on are for nice formatting
        embed.add_field(name="Joined Discord at:", value=member.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p"), inline=True) #would look ugly otherwise
        embed.add_field(name="Online Status:", value=member.status, inline=True)
        embed.add_field(name="Activity Status", value=member.activity, inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)


    @commands.command(aliases=['icon'])
    async def avatar(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.send(member.avatar_url)


    #pic with our stagelist on it, change file when it changes
    @commands.command()
    async def stagelist(self, ctx):
        await ctx.send(file=discord.File(r"/root/tabuu bot/files/stagelist.png")) 

    #classic ping
    @commands.command()
    async def ping(self, ctx):
        pingtime=self.bot.latency * 1000
        await ctx.send(f"Ping: {round(pingtime)}ms")

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

    #generic coin toss
    @commands.command()
    async def coin(self, ctx):
        coin = ['Coin toss: **Heads!**', 'Coin toss: **Tails!**']
        await ctx.send(random.choice(coin))

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



    #error handling for the above
    @listrole.error
    async def listrole_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        raise error

    @roleinfo.error
    async def roleinfo_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        raise error
        

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        raise error

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        raise error


    @modmail.error
    async def modmail_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a message to the moderators. It should look something like:\n```%modmail (your message here)```")
        raise error

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Wrong format!\nTry something like: %roll 1d100")
        raise error




def setup(bot):
    bot.add_cog(Usercommands(bot))
    print("Usercommands cog loaded")