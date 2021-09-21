import discord
from discord.ext import commands, tasks
import json
import asyncio

#
#this file here contains our custom mute system
#

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #adds the mute to the json file and gives out the role
    async def add_mute(self, guild: discord.Guild, member: discord.Member):
        with open (r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)
        
        role = discord.utils.get(guild.roles, id=739391329779581008)
        #need to use quite a few of these try/except blocks for adding/removing roles and dm'ing people unfortunately
        try:
            await member.add_roles(role)
        except:
            print("tried to add muted role to but it failed")

        #checking if the user is already muted.
        #we dont need that for the mute command but for the automatic mute this is useful as to not write someone 2x into the json file
        if not f'{member.id}' in muted_users:
            muted_users[f'{member.id}'] = {}
            muted_users[f'{member.id}']['muted'] = True

            with open(r'./json/muted.json', 'w') as f:
                json.dump(muted_users, f, indent=4)

    #basically reverses the action of the function above
    async def remove_mute(self, guild: discord.Guild, member: discord.Member):
        with open(r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)

        role = discord.utils.get(guild.roles, id=739391329779581008)
        try:
            await member.remove_roles(role)
        except:
            print("tried to remove muted role from user but it failed")

        if f'{member.id}' in muted_users:
            del muted_users[f'{member.id}']

            with open(r'./json/muted.json', 'w') as f:
                json.dump(muted_users, f, indent=4)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member:discord.Member, *, reason):
        #we check again if the user is muted here because i dont want the user to get dm'd again if he already is muted
        #didn't wanna put a separate dm function as well because the dm's change depending on what command calls it
        #thats why we kind of check twice here, the check in the function itself is still needed for automatic mutes
        with open (r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)
        
        if not f'{member.id}' in muted_users:
            await self.add_mute(ctx.guild, member)
            await ctx.send(f"{member.mention} was muted!")
            try:
                await member.send(f"You have been muted in the SSBU Training Grounds Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")

        else:
            await ctx.send("This user was already muted!")



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member:discord.Member):
        with open (r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)

        if f'{member.id}' in muted_users:
            await self.remove_mute(ctx.guild, member)
            await ctx.send(f"{member.mention} was unmuted!")
            try:
                await member.send("You have been unmuted in the SSBU Training Grounds Server! Don't break the rules again")
            except:
                print("user has blocked me :(")
        else:
            await ctx.send("This user was not muted!")


        
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def tempmute(self, ctx, member:discord.Member, mute_time, *, reason):
        #this block gets the time from a human readable input, so that the user does not have to convert hours to minutes or whatever
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

        if seconds < 30:
            await ctx.send("Invalid time format! Minimum value is 30 seconds.")
            return
        if seconds > 86401:
            await ctx.send("Invalid time format! Maximum value is 1 day.")
            return


        #now this is basically just "%mute, wait specified time, %unmute" but automated into one command
        with open (r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)
        
        #the mute block from %mute, with the inclusion of time_muted
        if not f'{member.id}' in muted_users:
            await self.add_mute(ctx.guild, member)
            await ctx.send(f"{member.mention} was muted for *{time_muted}*!")
            try:
                await member.send(f"You have been muted in the SSBU Training Grounds Server for ***{time_muted}*** for the following reason: \n```{reason}``` \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")

        else:
            await ctx.send("This user is already muted!")
            return

        #waits the specified time
        await asyncio.sleep(seconds)

        #need to refresh the json file
        with open (r'./json/muted.json', 'r') as f:
            muted_users = json.load(f)

        #the unmute block from %unmute, without the else statement, no need for another unmute confirmation if the user was unmuted before manually
        if f'{member.id}' in muted_users:
            await self.remove_mute(ctx.guild, member)
            await ctx.send(f"{member.mention} was automatically unmuted!")
            try:
                await member.send("You have been automatically unmuted in the SSBU Training Grounds Server! Don't break the rules again")
            except:
                print("user has blocked me :(")

        
        



    #error handling for the mute commands
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a reason for the mute!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @tempmute.error
    async def tempmute_error(self, ctx,error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member, an amount of time, and a reason!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.")
        else:
            raise error



def setup(bot):
    bot.add_cog(Mute(bot))
    print("Mute cog loaded")