import discord
from discord.ext import commands, tasks
import platform
import psutil
import time
import datetime
import os
from fuzzywuzzy import process


#
#this here is home to the various stats commands about users, roles or the bot
#


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #some basic info about a role
    @commands.command()
    async def roleinfo(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(input_role))
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
            role = discord.utils.get(ctx.guild.roles, name=match)

        #the above block searches all roles for the closest match, as seen in the admin cog

        embed = discord.Embed(title=f"Roleinfo of {role.name} ({role.id})", color = role.colour)
        embed.add_field(name="Role Name:", value=role.mention, inline=True)
        embed.add_field(name="Users with role:", value=len(role.members), inline=True)
        embed.add_field(name="Created at:", value=discord.utils.format_dt(role.created_at, style='F'))
        embed.add_field(name="Mentionable:", value=role.mentionable, inline=True)
        embed.add_field(name="Displayed Seperately:", value=role.hoist, inline=True)
        embed.add_field(name="Color:", value=role.color, inline=True)
        await ctx.send(embed=embed)

    #lists every member in the role if there arent more than 60 members, to prevent spam
    @commands.command(aliases=['listroles']) 
    async def listrole(self, ctx, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(input_role))
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
            role = discord.utils.get(ctx.guild.roles, name=match)

        members = role.members
        memberlist = []

        if len(members) > 60:
            await ctx.send(f"Users with the {role} role ({len(role.members)}):\n`Too many users to list!`")
            return
        if len(members) == 0:
            await ctx.send(f"No user currently has the {role} role!")
            return
        else:
            for member in members:
                memberlist.append(f"{member.name}#{member.discriminator}")
            all_members = ', '.join(memberlist)
            await ctx.send(f"Users with the {role} role ({len(role.members)}):\n`{all_members}`")



    #serverinfo, gives out basic info about the server
    @commands.command(aliases=['serverinfo'])
    async def server(self, ctx):
        if not ctx.guild:
            await ctx.send("This command is only available on servers.")
            return

        invites = await ctx.guild.invites()

        embed = discord.Embed(title=f"{ctx.guild.name} ({ctx.guild.id})", color=discord.Color.green())
        embed.add_field(name="Created on:", value=discord.utils.format_dt(ctx.guild.created_at, style='F'), inline=True)
        embed.add_field(name="Owner:", value=ctx.guild.owner.mention, inline=True)
        embed.add_field(name="Server Region:", value=ctx.guild.region, inline=True)

        embed.add_field(name="Members:", value=f"{len(ctx.guild.members)} (Bots: {sum(member.bot for member in ctx.guild.members)})", inline=True)
        embed.add_field(name="Boosts:", value=f"{ctx.guild.premium_subscription_count} (Boosters: {len(ctx.guild.premium_subscribers)})", inline=True)
        embed.add_field(name="Active Invites:", value=len(invites), inline=True)

        embed.add_field(name="Roles:", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Emojis:", value=f"{len(ctx.guild.emojis)}", inline=True)
        embed.add_field(name="Stickers:", value=f"{len(ctx.guild.stickers)}", inline=True)

        embed.add_field(name="Text Channels:", value=len(ctx.guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels:", value=len(ctx.guild.voice_channels), inline=True)
        embed.add_field(name="Active Threads:", value=len(ctx.guild.threads), inline=True)

        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)


    #userinfo
    @commands.command(aliases=['user'])
    async def userinfo(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            activity = member.activity.name
        except:
            activity = "None"

        if not ctx.guild:
            await ctx.send("This command can only be used in the SSBU TG Discord Server.")
            return

        sorted_members = sorted(ctx.guild.members, key=lambda x:x.joined_at)
        index = sorted_members.index(member)


        embed = discord.Embed(title=f"Userinfo of {member.name}#{member.discriminator} ({member.id})", color=member.top_role.color)
        embed.add_field(name="Name:", value=member.mention, inline=True)
        embed.add_field(name="Top Role:", value=member.top_role.mention, inline=True)
        embed.add_field(name="Number of Roles:", value=f"{(len(member.roles)-1)}", inline=True) #gives the number of roles to prevent listing like 35 roles, -1 for the @everyone role
        embed.add_field(name="Joined Server on:", value=discord.utils.format_dt(member.joined_at, style='F'), inline=True) #timezone aware datetime object, F is long formatting
        embed.add_field(name="Join Rank:", value=f"{(index+1)}/{len(ctx.guild.members)}", inline=True)
        embed.add_field(name="Joined Discord on:",  value=discord.utils.format_dt(member.created_at, style='F'), inline=True)
        embed.add_field(name="Online Status:", value=member.status, inline=True)
        embed.add_field(name="Activity Status:", value=activity, inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)


    #some bot stats
    @commands.command(aliases=['stats'])
    async def botstats(self, ctx):
        proc = psutil.Process(os.getpid())
        uptimeSeconds = time.time() - proc.create_time()

        embed = discord.Embed(title="Tabuu 3.0 Stats", color=0x007377, url="https://github.com/phxenix-w/Tabuu-3.0-Bot")
        embed.add_field(name="Name:", value=f"{self.bot.user.mention}", inline=True)
        embed.add_field(name="Servers:", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Total Users:", value=len(set(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Bot Version:", value=self.bot.version_number, inline=True)
        embed.add_field(name="Python Version:", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py Version:", value=discord.__version__, inline=True)
        embed.add_field(name="CPU Usage:", value=f"{psutil.cpu_percent(interval=None)}%", inline=True)
        embed.add_field(name="RAM Usage:", value=f"{round(psutil.virtual_memory()[3]/(1024*1024*1024), 2)}GB/{round(psutil.virtual_memory()[0]/(1024*1024*1024), 2)}GB ({round((psutil.virtual_memory()[3]/psutil.virtual_memory()[0]) * 100, 1)}%)", inline=True)
        embed.add_field(name="Uptime:", value=str(datetime.timedelta(seconds=uptimeSeconds)).split(".")[0], inline=True)
        embed.set_footer(text="Creator: Phxenix#1104, hosted on: Raspberry Pi 3B+")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)



    #error handling for the above
    @listrole.error
    async def listrole_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        else:
            raise error

    @roleinfo.error
    async def roleinfo_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        else:
            raise error
        

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Stats(bot))
    print("Stats cog loaded")