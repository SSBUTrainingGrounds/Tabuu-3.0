import discord
from discord.ext import commands, tasks
import json
from fuzzywuzzy import process
import asyncio
from discord.utils import get

#
#this file here contains most admin commands, they all need the @commands.has_permissions(administrator=True) decorator
#

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #clear
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount=1): #default amount for the clear is 1 message, so any channel doesnt get wiped by accident
        await ctx.channel.purge(limit=amount+1)

    #delete
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, *messages:discord.Message): #* so it detects multiple messages, works via message ID
        for message in messages: #deletes every one of them
            await message.delete()
        await ctx.message.delete() #deletes the original message aswell


    #ban command
    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def ban(self, ctx, id, *, args): #id is for the user ID, args for the ban reason
        unwanted = ['<','@','!','>'] #if someone does not use user ID,
        for i in unwanted: #it removes the junk from the mention and converts it into the raw ID string
            id = id.replace(i,'')
        
        guild = self.bot.get_guild(739299507795132486) #ID of SSBUTG discord server
        member = guild.get_member(int(id)) #int(id) to convert the id

        if member is None: #new ban command if the user isn't on the server
            user = await self.bot.fetch_user(int(id)) #have to use fetch if the user isn't on the server
            reason = ''.join(args)
            await ctx.guild.ban(user, reason=reason) #can't write users a dm, so skipped that step
            await ctx.send(f"{user.mention} has been banned!") #slightly different message gets sent, so i can know what command executed

        else: #just the regular ban command from before
            reason = ''.join(args)
            try:
                await member.send(f"You have been banned from the SSBU Training Grounds Server for the following reason: \n```{reason}```\nPlease contact Tabuu#0720 for an appeal.\nhttps://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/")
            except:
                print("user has blocked me :(")
            await member.ban(reason=reason) #logs the ban reason to the discord server
            await ctx.send(f"Banned {member.mention}!")
        

    #unban
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, id):
        unwanted = ['<','@','!','>'] #if someone does not use user ID,
        for i in unwanted: #it removes the junk from the mention and converts it into the raw ID string
            id = id.replace(i,'')
        user = await self.bot.fetch_user(int(id))
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned!")



    #kick command
    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def kick(self, ctx, member:discord.Member, *, args):
        reason = ''.join(args)
        try:
            await member.send(f"You have been kicked from the SSBU Training Grounds Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
        except:
            print("user has blocked me :(")
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}!")


    
    #role commands
    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def addrole(self, ctx, member:discord.Member, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role)) #this executes when you use the id, or mention the role
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0] #otherwise this executes, getting the closest match
            role = get(ctx.guild.roles, name=match)
        
        #the whole block above is searching for matching roles, its repeated in every role command below, does the same thing everytime

        await member.add_roles(role)
        await ctx.send(f"{member.mention} was given the {role} role")

    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def removerole(self, ctx, member:discord.Member, *,input_role):
        unwanted = ['<','@','>', '&']
        for i in unwanted:
            input_role = input_role.replace(i,'')
        all_roles = []

        for role in ctx.guild.roles:
            all_roles.append(role.name)
        try:
            role = get(ctx.guild.roles, id=int(input_role))
        except:
            match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
            role = get(ctx.guild.roles, name=match)

        await member.remove_roles(role) #same as above here
        await ctx.send(f"{member.mention} no longer has the {role} role")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def records(self, ctx):
        await ctx.send("https://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/") #google doc link to spreadsheet


    #renames the bot. thanks tabuu
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rename(self, ctx, member: discord.Member, *, name):
        await member.edit(nick=name)
        await ctx.send(f"Changed the display name of `{str(member)}` to `{name}`.")



    #error handling for the commands above, they all work in very similar ways
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument): #if the user fails to write a reason, also used as a failsafe
            await ctx.send("You need to specify a reason for the kick!")
        elif isinstance(error, commands.MemberNotFound): #if there is no valid user
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions): #if a non-admin uses this command
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a reason for the ban!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid ID, please make sure you got the right one, or just mention a member.")
        else:
            raise error

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member to unban.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I couldn't find a ban for this ID, make sure you have the right one.")
        else:
            raise error

    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a role!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        else:
            raise error

    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a role!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("You need to name a valid role!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I didn't find a good match for the role you provided. Please be more specific, or mention the role, or use the Role ID.")
        else:
            raise error

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send("Could not find a message with that ID! Make sure you are in the same channel as the message(s) you want to delete.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please supply one or more valid message IDs")
        else:
            raise error

    @records.error
    async def records_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @rename.error
    async def rename_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please enter a valid member and then a new nickname for them.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a nickname.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Something went wrong! Please try again.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Admin(bot))
    print("Admin cog loaded")