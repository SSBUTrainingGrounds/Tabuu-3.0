import discord
from discord.ext import commands, tasks
import re
import string
import time
import random
import json
from discord.utils import get

#
#this file here contains our message filters, both the link filter and the bad word filter
#

with open(r'/root/tabuu bot/files/badwords.txt') as file:
    file = file.read().split()


class On_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    async def add_mute(self, muted_users, user):
        if not f'{user.id}' in muted_users:
            muted_users[f'{user.id}'] = {}
            muted_users[f'{user.id}']['muted'] = True


    @commands.Cog.listener()
    async def on_message(self, message):


        if message.author == self.bot.user: #dont want any recursive stuff to happen, so any messages from tabuu 3.0 wont get checked, just in case
            return

        if not message.guild: #wont check dm's
            return

        separators = ()#string.digits+string.whitespace+string.punctuation , add all these for very strict ruling, might end up with false positives
        excluded = string.ascii_letters+string.digits #add/remove these depending on strictness, do +'/'+'-' and so on for urls in the future maybe

        guild = self.bot.get_guild(739299507795132486) #our guild
        mod_role = discord.utils.get(guild.roles, id=739299507816366106) #mod role, and promoter role
        promoter_role = discord.utils.get(guild.roles, id=739299507799326847)
        allowed_channels = (739299509670248502, 739299508902559811, 739299508403437623, 739299508197917060, 739299509670248505) #excepted channels
        if "discord.gg" in message.content or "discordapp.com/invite" in message.content: #ugly 4-nested if statements, havent found a more elegant way
            if mod_role not in message.author.roles: #also the above are the 2-most common invite links and are only used for invites, shouldnt get any false positives
                if promoter_role not in message.author.roles:
                    if message.channel.id not in allowed_channels:
                        await message.delete()
                        await message.channel.send(f"Please don't send invite links here {message.author.mention}")


        for word in file: #checks if a message contains one of the words in the badwords.txt file
            formatted_word = f"[{separators}]*".join(list(word))
            regex_true = re.compile(fr"{formatted_word}", re.IGNORECASE)
            regex_false = re.compile(fr"([{excluded}]+{word})|({word}[{excluded}]+)", re.IGNORECASE)

            #profane = False
            if regex_true.search(message.content) is not None\
                and regex_false.search(message.content) is None: #checks if a word matches, and then double checks again
                channel = self.bot.get_channel(785970832572678194) #just the infraction logs
                tabuu3 = self.bot.get_user(785303736582012969) #the bot itself
                server = self.bot.get_guild(739299507795132486) #the tg server, to get the muted role
                warn_id = random.randint(100000, 999999) #assigns the warning an ID for reference later
                warndate = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")
                embed = discord.Embed(title="⚠️New Warning⚠️", color = discord.Color.dark_red())
                embed.add_field(name="Warned User", value=message.author.mention, inline=True)
                embed.add_field(name="Moderator", value=tabuu3.mention, inline=True)
                embed.add_field(name="Reason", value=f"Automatic warning for using a blacklisted word", inline=True)
                embed.add_field(name="ID", value=warn_id, inline=True)
                embed.set_footer(text=f"{warndate} CET") 
                await channel.send(embed=embed) #logs the message to the channel
                try:
                    await message.delete() #deletes the message, below is the warn command
                except: #if another bot is also scanning for blacklisted words, it might delete the message first which would throw an error
                    pass
                with open(r'/root/tabuu bot/json/warns.json', 'r') as f: #path where my .json file is stored, r is for read
                    users = json.load(f) #loads .json file into memory


                warn_reason = (f"Automatic warning for using a blacklisted word")
                
                try: #most of this is just copied/adapted from the warn command
                    user_data = users[str(message.author.id)]
                    user_data[warn_id] = {"mod": tabuu3.id, "reason": warn_reason, "timestamp": warndate}
                except:
                    users[f'{message.author.id}'] = {}
                    user_data = users[str(message.author.id)]
                    user_data[warn_id] = {"mod": tabuu3.id, "reason": warn_reason, "timestamp": warndate}

                warns = len(user_data)


                await message.channel.send(f"{message.author.mention} has been automatically warned for using a blacklisted word!")
                try:
                    await message.author.send(f"You have been automatically warned in the SSBU Training Grounds Server for sending a message containing a blacklisted word.\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Maddy#1833")
                except:
                    print("user has blocked me :(")
                if warns > 6: #auto ban for more than 7 warns
                    try:
                        await message.author.send(f"You have been automatically banned from the SSBU Training Grounds Server for reaching #***{warns}***.\nPlease contact Tabuu#0720 for an appeal.\nhttps://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/")
                    except:
                        print("user has blocked me :(")
                    await message.author.ban(reason=f"Automatic ban for reaching {warns} warnings")
                    await message.channel.send(f"{message.author.mention} has reached warning #{warns}. They have been automatically banned.")
                if warns > 4 and warns < 7: #auto kick for more than 5 warns, stops at 7 so you dont get dumb errors
                    try:
                        await message.author.send(f"You have been automatically kicked from the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Maddy#1833")
                    except:
                        print("user has blocked me :(")
                    await message.author.kick(reason=f"Automatic kick for reaching {warns} warnings")
                    await message.channel.send(f"{message.author.mention} has reached warning #{warns}. They have been automatically kicked.")
                if warns > 2 and warns < 5: #auto mute if a user reaches 3 warns, stops at 5 so you dont get dumb errors
                    role = discord.utils.get(server.roles, id=739391329779581008) #muted role
                    await message.author.add_roles(role)
                    with open (r'/root/tabuu bot/json/muted.json', 'r') as fp:
                        muted_users = json.load(fp)
                    await self.add_mute(muted_users, message.author)
                    await message.channel.send(f"{message.author.mention} has reached warning #{warns}. They have been automatically muted.")
                    try:
                        await message.author.send(f"You have been automatically muted in the SSBU Training Grounds Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Maddy#1833")
                    except:
                        print("user has blocked me :(")
                    with open(r'/root/tabuu bot/json/muted.json', 'w') as fp: #writes it to the file
                        json.dump(muted_users, fp, sort_keys=True, ensure_ascii=False, indent=4) #dont need the sort_keys and ensure_ascii, works without

                with open(r'/root/tabuu bot/json/warns.json', 'w') as f: #w is for write
                    json.dump(users, f, indent=4) #writes data to .json file

                #profane = True

        #if not profane:
        #    await self.bot.process_commands(message)
        #
        #i needed the profane thingy above when not using cogs, if i use it now every command gets executed twice for whatever reason



def setup(bot):
    bot.add_cog(On_message(bot))
    print("On_message cog loaded")