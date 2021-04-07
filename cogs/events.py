import discord
from discord.ext import commands, tasks
import json
from itertools import cycle
from discord.utils import get

#
#this file here contains our event listeners, the welcome/booster messages, autorole and status updates
#

#status cycles through these, update these once in a while to keep it fresh
status = cycle(["type %help",
"Always watching 👀",
"Use the %modmail command in my DM's to privately contact the moderator team"])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self): #the pylint below is required, so that we dont get a false error
        self.change_status.start() #pylint: disable=no-member
        
    @tasks.loop(seconds=120) #the status loop, every 120 secs, could maybe increase it further
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(next(status)))

    
    
    #member join msg
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(739299507937738849) #ssbutg general: 739299507937738849
        rules = self.bot.get_channel(739299507937738843) #rules-and-info channel on ssbutg
        guild = self.bot.get_guild(739299507795132486) #ssbutg smash discord
        role = discord.utils.get(guild.roles, id=739391329779581008) #muted role
        cadet = discord.utils.get(guild.roles, id=739299507799326843) #cadet role

        try: #basically if the user id is in the muted.json this executes
            with open(r'/root/tabuu bot/json/muted.json', 'r') as f:
                muted_users = json.load(f)

            muted = muted_users[f'{member.id}']['muted'] #if a user is not muted, this here throws a keyerror, and then the except code kicks in

            if muted is True:
                await member.add_roles(role)
                await member.add_roles(cadet)
                await channel.send(f"Welcome back, {member.mention}! You are still muted, so maybe check back later.")



        except:
            await channel.send(f"{member.mention} has joined the ranks! What's shaking?\nPlease take a look at the {rules.mention} channel for information about server events/functions!")


    #if you join a voice channel, you get this role here
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_channel = 765625841861394442
        guild = self.bot.get_guild(739299507795132486)
        vc_role = discord.utils.get(guild.roles, id=824258210101198889)
        if before.channel is None or before.channel.id != voice_channel:
            if after.channel is not None and after.channel.id == voice_channel: #have to do the not None thing in both occasions, otherwise the console gets flooded with errors
                try:
                    await member.add_roles(vc_role)
                except:
                    pass

        #and if you leave, the role gets removed
        if after.channel is None or after.channel.id != voice_channel:
            if before.channel is not None and before.channel.id == voice_channel:
                try:
                    await member.remove_roles(vc_role)
                except:
                    pass




    #if a new booster boosts the server, checks role changes
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(739299507937738844) #ssbutg announcements channel: 739299507937738844 
        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles) #gets the new role

            if newRole.id == 739344833738571868: #checks if its the booster role
                await channel.send(f"{after.mention} has boosted the server!🥳🎉")


        if len(before.roles) > len(after.roles): #if you stop boosting, your color roles get removed
            color_roles = (774290821842862120, 774290823340359721, 774290825927458816, 774290826896605184, 774290829128105984, 774290831271002164, 794726232616206378, 794726234231013437, 794726235518795797)
            oldRole = next(role for role in before.roles if role not in after.roles) #gets the removed role

            if oldRole.id == 739344833738571868: #if its the booster role, all of the above color roles will get removed
                for role in color_roles:
                    try:
                        removerole = get(after.guild.roles, id=role)
                        await after.remove_roles(removerole)
                    except:
                        pass
        
        #this here gives out the cadet role on a successful member screening, on join was terrible because of shitty android app
        try:
            cadetrole = discord.utils.get(before.guild.roles, id=739299507799326843)
            member = self.bot.get_guild(before.guild.id).get_member(before.id)
            if before.bot or after.bot:
                return
            else:
                if before.pending == True:
                    if after.pending == False:
                        await member.add_roles(cadetrole)
        except AttributeError:
            pass


    #general error if the bot didnt find the command specified
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("I did not find this command. Type %help for all available commands.")
        raise error



def setup(bot):
    bot.add_cog(Events(bot))
    print("Events cog loaded")