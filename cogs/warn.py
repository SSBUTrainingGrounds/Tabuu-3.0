import discord
from discord.ext import commands, tasks
import json
import asyncio
import random
import time
from datetime import datetime, timedelta

#
#this file here contains the custom warning system
#

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self): #the pylint below is required, so that we dont get a false error
        self.warnloop.start() #pylint: disable=no-member



    async def add_mute(self, muted_users, user):
        if not f'{user.id}' in muted_users:
            muted_users[f'{user.id}'] = {}
            muted_users[f'{user.id}']['muted'] = True

    
    @commands.command()
    @commands.has_permissions(administrator=True) #checking permissions
    async def warn(self, ctx, user:discord.Member, *, args):

        if user.bot:
            await ctx.send("You can't warn bots, silly.") #just in case mods decide to be funny
            return

        reason = ''.join(args) #to get the full reason
        with open(r'/root/tabuu bot/json/warns.json', 'r') as f: #path where my .json file is stored, r is for read
            users = json.load(f) #loads .json file into memory

        warn_id = random.randint(100000, 999999) #warn id, so we can identify each warn, 6 digits is hopefully enough to avoid duplicates
        warndate = time.strftime("%A, %B %d %Y @ %H:%M:%S %p") #timestamp for the warning, in a nice format

        try: #if theres already at least 1 warning for a user, this gets executed
            user_data = users[str(user.id)]
            user_data[warn_id] = {"mod": ctx.author.id, "reason": reason, "timestamp": warndate}
        except: #if not, this gets executed, so a user key is made
            users[f'{user.id}'] = {}
            user_data = users[str(user.id)]
            user_data[warn_id] = {"mod": ctx.author.id, "reason": reason, "timestamp": warndate}

        warns = len(user_data) #total # of warnings

        author = ctx.author
        channel = self.bot.get_channel(785970832572678194) #ssbutg warn log channel: 785970832572678194
        embed = discord.Embed(title="⚠️New Warning⚠️", color = discord.Color.dark_red()) #test warn channel: 785974731273928714
        embed.add_field(name="Warned User", value=user.mention, inline=True)
        embed.add_field(name="Moderator", value=author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="ID", value=warn_id, inline=True)
        embed.timestamp = discord.utils.utcnow()


        await channel.send(embed=embed) #logs the warns in a nice format to the #infraction-logs channel

        await ctx.send(f"{user.mention} has been warned!")
        try:
            await user.send(f"You have been warned in the SSBU Training Grounds Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
        except:
            print("user has blocked me :(")
        if warns > 6: #auto ban for more than 7 warns
            try:
                await user.send(f"You have been automatically banned from the SSBU Training Grounds Server for reaching #***{warns}***.\nPlease contact Tabuu#0720 for an appeal.\nhttps://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/")
            except:
                print("user has blocked me :(")
            await ctx.send(f"{user.mention} has reached warning #{warns}. They have been automatically banned.")
            await user.ban(reason=f"Automatic ban for reaching {warns} warnings")
        if warns > 4 and warns < 7: #auto kick for more than 5 warns, stops at 7 so you dont get dumb errors
            try:
                await user.send(f"You have been automatically kicked from the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")
            await ctx.send(f"{user.mention} has reached warning #{warns}. They have been automatically kicked.")        
            await user.kick(reason=f"Automatic kick for reaching {warns} warnings")
        if warns > 2 and warns < 5: #auto mute if a user reaches 3 warns, stops at 5 so you dont get dumb errors
            role = discord.utils.get(ctx.guild.roles, id=739391329779581008) #muted role
            with open (r'/root/tabuu bot/json/muted.json', 'r') as fp: #the fp muted is for the mute database
                muted_users = json.load(fp)
            await user.add_roles(role)
            await self.add_mute(muted_users, user)
            with open(r'/root/tabuu bot/json/muted.json', 'w') as fp: #writes it to the file
                json.dump(muted_users, fp, sort_keys=True, ensure_ascii=False, indent=4) #dont need the sort_keys and ensure_ascii, works without
            await ctx.send(f"{user.mention} has reached warning #{warns}. They have been automatically muted.")
            try:
                await user.send(f"You have been automatically muted in the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
            except:
                print("user has blocked me :(")

        with open(r'/root/tabuu bot/json/warns.json', 'w') as f: #w is for write
            json.dump(users, f, indent=4) #writes data to .json file
        






    @commands.command(aliases=['warnings', 'infractions'])
    async def warns(self, ctx, user:discord.Member = None): #doesnt need an admin check imo
        if user is None:
            user = ctx.author

        try:
            with open(r'/root/tabuu bot/json/warns.json', 'r') as f:
                users = json.load(f) #loads .json file into memory

            user_data = users[str(user.id)]

            await ctx.send(f'{user.mention} has {len(user_data)} warning(s).') #just gets you the number
        except:
            await ctx.send(f"{user.mention} doesn't have any warnings (yet).")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, user:discord.Member):
        with open(r'/root/tabuu bot/json/warns.json', 'r') as f: #loads file as before
            users = json.load(f)

        if f'{user.id}' in users: #have to use this if else statement so the file doesnt get corrupted
            del users[f'{user.id}']
            await ctx.send(f"Cleared all warnings for {user.mention}.")
        else:
            await ctx.send(f"No warnings found for {user.mention}")

        with open(r'/root/tabuu bot/json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warndetails(self, ctx, user:discord.Member):
        try: #if the bot finds matching user in database
            with open(r'/root/tabuu bot/json/warns.json', 'r') as f:
                users = json.load(f) #loads .json file into memory


            user_data = users[str(user.id)]
            await ctx.send(f"Active warnings for {user.mention}: {len(user_data)}") #just the number
            warn_id = user_data.keys() #gets the warn id
            i = 1
            for warn_id in user_data.keys(): #gets all of the data, cycles through each warning
                mod = users[f'{user.id}'][warn_id]['mod']
                reason = users[f'{user.id}'][warn_id]['reason']
                timestamp = users[f'{user.id}'][warn_id]['timestamp']
                new_timestamp = datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")
                embed = discord.Embed(title=f"Warning #{i}", colour=discord.Colour.red())
                embed.add_field(name="Moderator: ", value=f"<@{mod}>")
                embed.add_field(name="Reason: ", value=f"{reason}")
                embed.add_field(name="ID:", value=f"{warn_id}")
                embed.add_field(name="Warning given out at:", value=discord.utils.format_dt(new_timestamp, style='F'))
                await ctx.send(embed=embed)
                i+=1
        except: #if not, generic error message
            await ctx.send(f"{user.mention} doesn't have any active warnings (yet).")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletewarn(self, ctx, user:discord.Member, warn_id):
        
        with open(r'/root/tabuu bot/json/warns.json', 'r') as f:
            users = json.load(f)

        user_data = users[str(user.id)]

        if warn_id in user_data: #have to use this if else statement so the file does not get corrupted
            del users[f'{user.id}'][warn_id]
            await ctx.send(f"Deleted warning {warn_id} for {user.mention}")
        else:
            await ctx.send(f"I couldnt find a warning with the ID {warn_id} for {user.mention}.")

        with open(r'/root/tabuu bot/json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)



    #error handling for the above
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
        with open(r'/root/tabuu bot/json/warns.json', 'r') as f:
            users = json.load(f)

        tbd_users = []
        tbd_ids = []

        for i in users: #checks every user
            warned_user = i
            warn_id = users[warned_user].keys()
            for warn_id in users[warned_user].keys(): #checks every warning for every user
                timestamp = users[warned_user][warn_id]['timestamp']
                timestamp = datetime.strptime(timestamp, "%A, %B %d %Y @ %H:%M:%S %p")
                timenow = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")
                timenow = str(timenow)
                timenow = datetime.strptime(timenow, "%A, %B %d %Y @ %H:%M:%S %p") #have to do this shit, otherwise it doesnt read the right value for whatever reason
                timediff = timenow - timestamp
                daydiff = timediff.days #gets the time difference in days, if its over 30, it appends it to the "to be deleted"-list
                if daydiff > 29:
                    tbd_users.append(warned_user)
                    tbd_ids.append(warn_id)
                    print(f"deleting warn_id #{warn_id} for user {warned_user} after 30 days")
                    

        i = 0
        for x in tbd_ids: #deletes every entry in the list determined above, have to do it seperately, otherwise the length of the for loop changes, and that throws an error
            warned_user = tbd_users[i]
            warn_id = tbd_ids[i]
            print(warned_user, x)
            del users[warned_user][warn_id]
            print(f"deleted warn#{warn_id}!")
            i += 1
        
        with open(r'/root/tabuu bot/json/warns.json', 'w') as f:
            json.dump(users, f, indent=4)







def setup(bot):
    bot.add_cog(Warn(bot))
    print("Warn cog loaded")