import discord
from discord.ext import commands, tasks
import asyncio
from utils.ids import GuildNames, GuildIDs
from utils.role import search_role

#
#this file here contains general purpose admin commands, they all need the @commands.has_permissions(administrator=True) decorator
#

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #clear
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount=1): #default amount for the clear is 1 message
        if amount < 1:
            await ctx.send("Please input a valid number!")
            return

        deleted = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"Successfully deleted `{len(deleted)}` messages, {ctx.author.mention}")


    #delete
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, *messages:discord.Message): #* so it detects multiple messages, works via message ID
        for message in messages: #deletes every one of them
            await message.delete()
        await ctx.message.delete() #deletes the original message aswell


    #ban command
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, user: discord.User, *, reason):
        #since the mod team cannot stop playing with the ban command for fun, i had to add a check to verify
        def check(m):
            return m.content.lower() in ("y", "n") and m.author == ctx.author and m.channel == ctx.channel

        #if the reason provided is too long for the embed, we'll just cut it off
        if len(reason[2000:]) > 0:
            reason = reason[:2000]

        embed = discord.Embed(title=f"{str(user)} ({user.id})", description = f"**Reason:** {reason}", colour=discord.Colour.dark_red())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(f"{ctx.author.mention}, are you sure you want to ban this user? **Type y to verify** or **Type n to cancel**.", embed=embed)
        
        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"Ban for {user.mention} timed out, try again.")
            return
        else:
            if msg.content.lower() == "y":
                #tries to dm them first, need a try/except block cause you can ban ppl not on your server, or ppl can block your bot
                try:
                    await user.send(f"You have been banned from the {ctx.guild.name} Server for the following reason: \n```{reason}```\nPlease contact Tabuu#0720 for an appeal.\nhttps://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/")
                except:
                    print("user has blocked me :(")

                await ctx.guild.ban(user, reason=reason)
                await ctx.send(f"{user.mention} has been banned!")
            elif msg.content.lower() == "n":
                await ctx.send(f"Ban for {user.mention} cancelled.")
                return
        

    #unban
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user: discord.User):
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned!")


    #automatically bans the users on bg that are on our ban list over at tg
    @commands.command(aliases=['syncbans'])
    @commands.has_permissions(administrator=True)
    async def syncbanlist(self, ctx):
        if ctx.guild.id != GuildIDs.BATTLEGROUNDS:
            await ctx.send(f"This command is only available on the {GuildNames.BATTLEGROUNDS} server!")
            return

        tg_guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)

        bans = await tg_guild.bans()

        await ctx.send("Syncing ban list... Please wait a few seconds.")

        i = 0

        for u in bans:
            try:
                await ctx.guild.fetch_ban(u.user)
            except discord.NotFound:
                await ctx.guild.ban(u.user, reason=f"Automatic ban because user was banned on the {GuildNames.TG} server.")
                await ctx.send(f"Banned {str(u.user)}!")
                i += 1
            
        await ctx.send(f"Ban list was successfully synced. Banned {i} users.")



    #kick command
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member:discord.Member, *, reason):
        #same as the ban command, there would be an easier fix involving the mod team not to fuck around with that but here we are
        def check(m):
            return m.content.lower() in ("y", "n") and m.author == ctx.author and m.channel == ctx.channel

        if len(reason[2000:]) > 0:
            reason = reason[:2000]

        embed = discord.Embed(title=f"{str(member)} ({member.id})", description = f"**Reason:** {reason}", colour=discord.Colour.dark_orange())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(f"{ctx.author.mention}, are you sure you want to kick this user? **Type y to verify** or **Type n to cancel**.", embed=embed)

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"Kick for {member.mention} timed out, try again.")
            return
        else:
            if msg.content.lower() == "y":
                try:
                    await member.send(f"You have been kicked from the {ctx.guild.name} Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
                except:
                    print("user has blocked me :(")
                await member.kick(reason=reason)
                await ctx.send(f"Kicked {member}!")
            elif msg.content.lower() == "n":
                await ctx.send(f"Kick for {member.mention} cancelled.")
                return


    
    #role commands
    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def addrole(self, ctx, member:discord.Member, *, input_role):
        #searches the closest matching role
        role = search_role(ctx.guild, input_role)

        await member.add_roles(role)
        await ctx.send(f"{member.mention} was given the {role} role.")


    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def removerole(self, ctx, member:discord.Member, *,input_role):
        role = search_role(ctx.guild, input_role)

        await member.remove_roles(role) #same as above here
        await ctx.send(f"{member.mention} no longer has the {role} role.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def records(self, ctx):
        await ctx.send("https://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/") #google doc link to spreadsheet


    #renames the bot. thanks tabuu
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rename(self, ctx, member: discord.Member, *, name = None):
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
        elif isinstance(error, commands.UserNotFound):
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
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("I could not find this user!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I couldn't find a ban for this ID, make sure you have the right one.")
        else:
            raise error

    @syncbanlist.error
    async def syncbanlist_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
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
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please input a valid number!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I could not delete one or more of these messages! Make sure they were not send too long ago or try a different amount.")
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
            await ctx.send("Please enter a valid member.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a member.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Something went wrong! Please try again.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Admin(bot))
    print("Admin cog loaded")