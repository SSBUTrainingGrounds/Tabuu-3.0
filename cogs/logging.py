import discord
from discord.ext import commands, tasks
import datetime

#
#this file here contains the logs, it logs every little user/message update into our logs channel
#

logchannel = 739299509670248504 #logchannel id

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #if a user updates their profile
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        #username change
        if before.name != after.name:
            embed = discord.Embed(title="**✏️ Username changed ✏️**", description=f"Before: {before.name}\nAfter: {after.name}", colour=discord.Colour.orange())
            embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            logs = self.bot.get_channel(logchannel)
            await logs.send(embed=embed)
        
        #discriminator change
        if before.discriminator != after.discriminator:
            embed = discord.Embed(title="**✏️ Discriminator changed ✏️**", description=f"Before: {before.discriminator}\nAfter: {after.discriminator}", colour=discord.Colour.orange())
            embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            logs = self.bot.get_channel(logchannel)
            await logs.send(embed=embed)

        #avatar change
        if before.avatar.url != after.avatar.url:
            embed = discord.Embed(title=f"**📷 Avatar changed 📷**", description=f"New avatar below:", colour=discord.Colour.dark_gray())
            embed.set_thumbnail(url=before.avatar.url)
            embed.set_image(url=after.avatar.url)
            embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            logs = self.bot.get_channel(logchannel)
            await logs.send(embed=embed)

    #if a member changes something on the server
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        #if someone changes their nickname on this server
        if before.display_name != after.display_name:
            embed = discord.Embed(title="**✏️ Nickname changed ✏️**", description=f"Before: {before.display_name}\nAfter: {after.display_name}", colour=discord.Colour.orange())
            embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            logs = self.bot.get_channel(logchannel)
            await logs.send(embed=embed)
        
        #roles change
        if before.roles != after.roles:
            #user gains a role
            if len(before.roles) < len(after.roles):
                newRole = next(role for role in after.roles if role not in before.roles) #gets the new role
                embed = discord.Embed(title="**📈 User gained role 📈**", description=f"Role gained: {newRole.mention}", colour=discord.Colour.green())
                embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                logs = self.bot.get_channel(logchannel)
                await logs.send(embed=embed)

            #user loses a role
            if len(before.roles) > len(after.roles):
                oldRole = next(role for role in before.roles if role not in after.roles) #gets the old role
                embed = discord.Embed(title="**📉 User lost role 📉**", description=f"Role lost: {oldRole.mention}", colour=discord.Colour.dark_red())
                embed.set_author(name=f"{str(after)} ({after.id})", icon_url=after.avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                logs = self.bot.get_channel(logchannel)
                await logs.send(embed=embed)

    
    #someone joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title="**🎆 New member joined 🎆**", description=f"{member.mention} has joined the server!\n\n**Account created:**\n{discord.utils.format_dt(member.created_at, style='R')}", colour=discord.Colour.green())
        embed.set_author(name=f"{str(member)} ({member.id})", icon_url=member.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)

    #someone leaves the server
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        everyonerole = discord.utils.get(member.guild.roles, name="@everyone")
        roles = [role.mention for role in member.roles if role is not everyonerole] #we dont want the everyone role to be included there
        role_description = f"{' '.join(roles)}" if len(roles) != 0 else "No roles" #if the member has no roles, we dont want the field to be empty
        embed = discord.Embed(title=f"** 🚶 Member left the server 🚶**", description=f"{member.mention} has left the server. \n**Lost roles:** \n{role_description}", colour=discord.Colour.dark_red())
        embed.set_author(name=f"{str(member)} ({member.id})", icon_url=member.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)


    #someone edits their message
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild: #dont want dms to be included, same in the below listeners
            return

        if after.author.bot: #also dont care about bot message edits
            return

        if before.content == after.content:
            return

        if len(after.content[2000:]) > 0: #discord released an update where they allow nitro users to send messages with up to 4000 chars in them, but an embed can only have 6000 chars in them
            after.content = "Content is too large to fit in a single embed."
        if len(before.content[2000:]) > 0: #so we need to add in a check to not get dumb errors. 2000 chars is still the limit for non-nitro users so it should be fine.
            before.content = "Content is too large to fit in a single embed."
        
        embed = discord.Embed(title=f"**✍️ Edited Message in {after.channel.name}! ✍️**", description=f"**New Content:**\n{after.content}", colour=discord.Colour.orange())
        embed.set_author(name=f"{str(after.author)} ({after.author.id})", icon_url=after.author.avatar.url)
        embed.add_field(name=f"**Old Content:**", value=f"{before.content[:1000]}", inline=False)
        if len(before.content[1000:]) > 0: #if a message is too long, it gets split into two embed fields, 1000 chars is the limit for embed values, 2000 is the max discord message.
            embed.add_field(name="(Continued from above)", value=before.content[1000:], inline=False) #descriptions can be 2048 chars long, so it just fits barely there
        embed.add_field(name="Message ID:", value=f"{after.id}\n{after.jump_url}")
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)

    #someone deletes their message
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return
        
        if message.author.bot:
            return

        if len(message.content[2000:]) > 0: #same as above with the message length
            message.content = "Content is too large to fit in a single embed."
        
        embed = discord.Embed(title=f"**❌ Deleted Message in {message.channel.name}! ❌**", description=f"**Content:**\n{message.content}", colour=discord.Colour.dark_red())
        embed.set_author(name=f"{str(message.author)} ({message.author.id})", icon_url=message.author.avatar.url)
        if message.attachments: #if a message has an attachment with it, it also gets logged. i dont really care for that on the on message edit though
            if len(message.attachments) == 1: #for one attachment, this is enough
                if message.attachments[0].url.endswith(('.jpg', '.png', '.jpeg', '.gif')): #if its an image it will be the embed image
                    new_url = message.attachments[0].url.replace('cdn.discordapp.com', 'media.discordapp.net') #trying this out to log images more consistently
                    embed.set_image(url=new_url)
                else: #else it will just log the url
                    embed.add_field(name="Attachment", value=message.attachments[0].url)
            else: #for multiple, putting it all into one embed value might result in too many characters, so this is needed. only mobile users can send multiple attachments anyway right now
                i = 1
                for x in message.attachments:
                    embed.add_field(name=f"Attachment ({i}/{len(message.attachments)})", value=x.url, inline=False)
                    i += 1
        embed.add_field(name="Message ID:", value=message.id)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)

    #someone deletes a lot of messages
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        embed = discord.Embed(title=f"**❌ Bulk message deletion in {messages[0].channel.name}! ❌**", description=f"{len(messages)} messages were deleted!", colour=discord.Colour.dark_red())
        embed.set_author(name=f"{str(self.bot.user)} ({self.bot.user.id})", icon_url=self.bot.user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)
        

    #someone gets banned
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(title="**🚫 New ban! 🚫**", description=f"{user.mention} has been banned from this server!", colour=discord.Colour.dark_red())
        embed.set_author(name=f"{str(user)} ({user.id})", icon_url=user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)

    #someone gets unbanned
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(title="**🔓 New unban! 🔓**", description=f"{user.mention} has been unbanned from this server!", colour=discord.Colour.green())
        embed.set_author(name=f"{str(user)} ({user.id})", icon_url=user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        logs = self.bot.get_channel(logchannel)
        await logs.send(embed=embed)




def setup(bot):
    bot.add_cog(Logging(bot))
    print("Logging cog loaded")