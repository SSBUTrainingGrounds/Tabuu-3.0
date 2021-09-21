import discord
from discord.ext import commands, tasks
import json
import random
import time
from datetime import datetime, timedelta
from .mute import Mute

#
#this file here contains the custom warning system
#

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self): #the pylint below is required, so that we dont get a false error
        self.warnloop.start() #pylint: disable=no-member


    async def add_warn(self, author: discord.Member, member: discord.Member, reason):
        #this first part here logs the warning into the json file
        with open(r'./json/warns.json', 'r') as f:
            users = json.load(f)

        #assigning each warning a random 6 digit number, hope thats enough to not get duplicates
        warn_id = random.randint(100000, 999999)
        warndate = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")

        try:
            user_data = users[str(member.id)]
            user_data[warn_id] = {"mod": author.id, "reason": reason, "timestamp": warndate}
        except:
            users[f'{member.id}'] = {}
            user_data = users[str(member.id)]
            user_data[warn_id] = {"mod": author.id, "reason": reason, "timestamp": warndate}

        with open(r'./json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)


        #and this second part here logs the warn into the warning log discord channel
        channel = self.bot.get_channel(785970832572678194)
        embed = discord.Embed(title="⚠️New Warning⚠️", color = discord.Color.dark_red())
        embed.add_field(name="Warned User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="ID", value=warn_id, inline=True)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)



    #this function here checks the warn count on each user and if it reaches a threshold it will mute/kick/ban the user
    async def check_warn_count(self, guild: discord.Guild, channel: discord.TextChannel, member: discord.Member):
        with open(r'./json/warns.json', 'r') as f:
            users = json.load(f)

        user_data = users[str(member.id)]
        warns = len(user_data)

        if warns > 6:
            try:
                await member.send(f"You have been automatically banned from the SSBU Training Grounds Server for reaching #***{warns}***.\nPlease contact Tabuu#0720 for an appeal.\nhttps://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/")
            except:
                print("user has blocked me :(")

            await channel.send(f"{member.mention} has reached warning #{warns}. They have been automatically banned.")
            await member.ban(reason=f"Automatic ban for reaching {warns} warnings")
        elif warns > 4:
            try:
                await member.send(f"You have been automatically kicked from the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")

            await channel.send(f"{member.mention} has reached warning #{warns}. They have been automatically kicked.")        
            await member.kick(reason=f"Automatic kick for reaching {warns} warnings")
        elif warns > 2:
            await Mute.add_mute(self, guild, member)
            await channel.send(f"{member.mention} has reached warning #{warns}. They have been automatically muted.")

            try:
                await member.send(f"You have been automatically muted in the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")
            


    #the actual commands, first the basic warn command
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member:discord.Member, *, reason):
        if member.bot:
            await ctx.send("You can't warn bots, silly.")
            return

        #adds the warning
        await self.add_warn(ctx.author, member, reason)

        #tries to dm user
        try:
            await member.send(f"You have been warned in the SSBU Training Grounds Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
        except:
            print("user has blocked me :(")
        await ctx.send(f"{member.mention} has been warned!")

        #checks warn count for further actions
        await self.check_warn_count(ctx.guild, ctx.channel, member)


    #checking how many warnings a user has, no need for permissions
    @commands.command(aliases=['warnings', 'infractions'])
    async def warns(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            with open(r'./json/warns.json', 'r') as f:
                users = json.load(f) #loads .json file into memory

            user_data = users[str(member.id)]

            await ctx.send(f'{member.mention} has {len(user_data)} warning(s).') #just gets you the number
        except:
            await ctx.send(f"{member.mention} doesn't have any warnings (yet).")


    #deletes the whole user entry
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member:discord.Member):
        with open(r'./json/warns.json', 'r') as f: #loads file as before
            users = json.load(f)

        if f'{member.id}' in users: #have to use this if else statement so the file doesnt get corrupted
            del users[f'{member.id}']
            await ctx.send(f"Cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"No warnings found for {member.mention}")

        with open(r'./json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)


    #gets you a detailed overview of the warnings of a user
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warndetails(self, ctx, member:discord.Member):
        try: #if the bot finds matching user in database
            with open(r'./json/warns.json', 'r') as f:
                users = json.load(f) #loads .json file into memory


            user_data = users[str(member.id)]
            await ctx.send(f"Active warnings for {member.mention}: {len(user_data)}") #just the number
            i = 1
            for warn_id in user_data.keys(): #gets all of the data, cycles through each warning
                mod = users[f'{member.id}'][warn_id]['mod']
                reason = users[f'{member.id}'][warn_id]['reason']
                timestamp = users[f'{member.id}'][warn_id]['timestamp']
                new_timestamp = datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")
                embed = discord.Embed(title=f"Warning #{i}", colour=discord.Colour.red())
                embed.add_field(name="Moderator: ", value=f"<@{mod}>")
                embed.add_field(name="Reason: ", value=f"{reason}")
                embed.add_field(name="ID:", value=f"{warn_id}")
                embed.add_field(name="Warning given out at:", value=discord.utils.format_dt(new_timestamp, style='F'))
                await ctx.send(embed=embed)
                i+=1
        except: #if not, generic error message
            await ctx.send(f"{member.mention} doesn't have any active warnings (yet).")


    #deletes a specific warning
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletewarn(self, ctx, member:discord.Member, warn_id):
        try:
            with open(r'./json/warns.json', 'r') as f:
                users = json.load(f)

            user_data = users[str(member.id)]

            if warn_id in user_data: #have to use this if else statement so the file does not get corrupted
                del users[f'{member.id}'][warn_id]
                await ctx.send(f"Deleted warning {warn_id} for {member.mention}")
            else:
                await ctx.send(f"I couldnt find a warning with the ID {warn_id} for {member.mention}.")

            with open(r'./json/warns.json', 'w') as f:
                json.dump(users, f, indent=4)
        except:
            await ctx.send("This user does not have any active warnings.")



    #basic error handling for the above
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a reason!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @clearwarns.error
    async def clearwarns_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @deletewarn.error
    async def deletewarn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member and specify a warn_id.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warndetails.error
    async def warndetails_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error





    #this here checks if a warning is older than 30 days and has expired, then deletes the expired warnings
    #gets called once on bot startup and then every 24 hours
    @tasks.loop(hours=24)
    async def warnloop(self):
        with open(r'./json/warns.json', 'r') as f:
            users = json.load(f)

        tbd_warnings = []

        #checks every warning for every user
        #we first need to append the warnings to a separate list and then we can delete them
        for warned_user in users:
            for warn_id in users[warned_user].keys():
                timestamp = users[warned_user][warn_id]['timestamp']
                #this here compares the stored CEST timezone of the warning to the current GMT timezone
                #its off by 1 hour (or 2 in summer) but thats close enough when we count in differences of 30 days
                timediff = datetime.utcnow() - datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")
                daydiff = timediff.days
                #so if its been longer than 30 days since the warning was handed out, we will hand the warning over to the loop below which will delete it
                if daydiff > 29:
                    tbd_warnings.append((warned_user, warn_id))
                    print(f"deleting warn_id #{warn_id} for user {warned_user} after 30 days")

        #deletes the warnings
        for i in tbd_warnings:
            #i00 is the user id, i01 is the warn id
            del users[[i][0][0]][[i][0][1]]
            print(f"deleted warn #{[i][0][1]}!")
        
        with open(r'./json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)





def setup(bot):
    bot.add_cog(Warn(bot))
    print("Warn cog loaded")