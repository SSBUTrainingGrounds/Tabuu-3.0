import discord
from discord.ext import commands, tasks
import json
import asyncio
import random
import time

#
#this file here contains our custom mute system
#

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_mute(self, muted_users, user):
        if not f'{user.id}' in muted_users:
            muted_users[f'{user.id}'] = {}
            muted_users[f'{user.id}']['muted'] = True

    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def mute(self, ctx, member:discord.Member, *, args):
        role = discord.utils.get(ctx.guild.roles, name="Muted") #specific name for the role, needs changing when the role name changes
        reason = ''.join(args)
        with open (r'/root/tabuu bot/json/muted.json', 'r') as f:
            muted_users = json.load(f)
        await member.add_roles(role)
        await self.add_mute(muted_users, member) #adds the mute to muted.json
        await ctx.send(f"{member.mention} was muted!")
        try:
            await member.send(f"You have been muted in the SSBU Training Grounds Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Karma!#6636 or Maddy#1833")
        except:
            print("user has blocked me :(")
        
        with open(r'/root/tabuu bot/json/muted.json', 'w') as f: #writes it to the file
            json.dump(muted_users, f, sort_keys=True, ensure_ascii=False, indent=4) #dont really need either, but sort_keys is for sorting the users by id, and ensure_ascii is kinda useless here, because there are no non-ascii chars passed here anyways


    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def unmute(self, ctx, member:discord.Member): #just the reverse mute command
        role = discord.utils.get(ctx.guild.roles, name="Muted") #specific name for the role, needs changing when the role name changes
        await member.remove_roles(role)
        with open(r'/root/tabuu bot/json/muted.json', 'r') as f:
            muted_users = json.load(f)

        if f'{member.id}' in muted_users: #have to check if the user is muted in the json file, otherwise the delete function would corrupt the file
            del muted_users[f'{member.id}']['muted']
            del muted_users[f'{member.id}']
            await ctx.send(f"{member.mention} was unmuted!")
            try:
                await member.send("You have been unmuted in the SSBU Training Grounds Server! Don't break the rules again")
            except:
                print("user has blocked me :(")
        else:
            await ctx.send(f"{member.mention} was not muted.")
        with open(r'/root/tabuu bot/json/muted.json', 'w') as f:
            json.dump(muted_users, f, indent=4)

        
        

    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def tempmute(self, ctx, member:discord.Member, mute_time, *, args): #this is pretty much just the mute command, then a x min waiting period and then the unmute command
        reason = ''.join(args)
        #this block here gets the time
        if mute_time.lower().endswith("d"):
            seconds = int(mute_time[:-1]) * 60 * 60 * 24
            time_muted = f"{seconds // 60 // 60 // 24} day(s)"
        elif mute_time.lower().endswith("h"):
            seconds = int(mute_time[:-1]) * 60 * 60
            time_muted = f"{seconds // 60 // 60} hour(s)"
        elif mute_time.lower().endswith("m"):
            seconds = int(mute_time[:-1]) * 60
            time_muted = f"{seconds // 60} minute(s)"
        elif mute_time.lower().endswith("s"):
            seconds = int(mute_time[:-1])
            time_muted = f"{seconds} seconds"
        else:
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.")
            return

        if seconds < 30: #makes sure there are no negative values
            await ctx.send("Invalid time format! Minimum value is 30 seconds.")
            return
        if seconds > 86401: #1 day + 1 sec
            await ctx.send("Invalid time format! Maximum value is 1 day.")
            return
  
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        with open (r'/root/tabuu bot/json/muted.json', 'r') as f:
            muted_users = json.load(f)
        await self.add_mute(muted_users, member)
        await member.add_roles(role)
        with open(r'/root/tabuu bot/json/muted.json', 'w') as f:
            json.dump(muted_users, f, sort_keys=True, ensure_ascii=False, indent=4) #dont need the sort_keys and ensure_ascii, works without

        await ctx.send(f"{member.mention} has been muted for {time_muted}!") #now we need to change that back just for the message
        try:
            await member.send(f"You have been muted in the SSBU Training Grounds Server for ***{time_muted}*** for the following reason: \n```{reason}``` \nIf you would like to discuss your punishment, please contact Tabuu#0720, Karma!#6636 or Maddy#1833")
        except:
            print("user has blocked me :(")

        await asyncio.sleep(seconds) #waits the specified amount of time
        await member.remove_roles(role) #reverses the action above, could move it into the if statement, doesnt really matter tho if you remove a role thats not there
        with open(r'/root/tabuu bot/json/muted.json', 'r') as f:
            muted_users = json.load(f)
        if f'{member.id}' in muted_users: #checks if they already have been unmuted, so the muted file doesnt break
            del muted_users[f'{member.id}']['muted']
            del muted_users[f'{member.id}']
            await ctx.send(f"{member.mention} has been automatically unmuted!")
            try:
                await member.send(f"You have been unmuted in the SSBU Training Grounds Server! Don't break the rules again")
            except:
                print("user has blocked me :(")
        else:
            await ctx.send(f"I tried to unmute {member.mention}, but they were already unmuted.")
        with open(r'/root/tabuu bot/json/muted.json', 'w') as f:
            json.dump(muted_users, f, indent=4)



    #error handling for the mute commands
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a reason for the mute!")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        raise error

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument): #bit different than the rest cause you dont need a reason for unmute
            await ctx.send("You need to mention a member!")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        raise error

    @tempmute.error
    async def tempmute_error(self, ctx,error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member, an amount of time, and a reason!")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.")
        raise error

def setup(bot):
    bot.add_cog(Mute(bot))
    print("Mute cog loaded")