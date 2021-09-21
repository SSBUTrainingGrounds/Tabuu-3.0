import discord
from discord.ext import commands, tasks
import re
import string
from .warn import Warn

#
#this file here contains our message filters, both the link filter and the bad word filter
#

with open(r'./files/badwords.txt') as file:
    file = file.read().split()


class On_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user: #dont want any recursive stuff to happen, so any messages from tabuu 3.0 wont get checked, just in case
            return

        if not message.guild: #wont check dm's
            return


        #searches for invite links, no need for regex as there are a million ways to disguise invite links anyways. 
        #this is just a basic filter which is not designed to stop 100% of invite links coming in
        if "discord.gg" in message.content or "discordapp.com/invite" in message.content:
            guild = self.bot.get_guild(739299507795132486)
            mod_role = discord.utils.get(guild.roles, id=739299507816366106)
            promoter_role = discord.utils.get(guild.roles, id=739299507799326847)
            allowed_channels = (739299509670248502, 739299508902559811, 739299508403437623, 739299508197917060, 739299509670248505)
            if mod_role not in message.author.roles and promoter_role not in message.author.roles and message.channel.id not in allowed_channels:
                await message.delete()
                await message.channel.send(f"Please don't send invite links here {message.author.mention}")


        #searches for bad words using regex
        separators = ()#string.digits+string.whitespace+string.punctuation , add all these for very strict ruling, might end up with false positives
        excluded = string.ascii_letters+string.digits #add/remove these depending on strictness, do +'/'+'-' and so on for urls in the future maybe

        for word in file: #checks if a message contains one of the words in the badwords.txt file
            formatted_word = f"[{separators}]*".join(list(word))
            regex_true = re.compile(fr"{formatted_word}", re.IGNORECASE)
            regex_false = re.compile(fr"([{excluded}]+{word})|({word}[{excluded}]+)", re.IGNORECASE)


            #checks if a word matches, and then double checks again
            if regex_true.search(message.content) is not None and regex_false.search(message.content) is None:

                #adds the warning
                reason = "Automatic warning for using a blacklisted word"
                await Warn.add_warn(self, message.guild.me, message.author, reason)
                await message.channel.send(f"{message.author.mention} has been automatically warned for using a blacklisted word!")
            
                try:
                    await message.author.send(f"You have been automatically warned in the SSBU Training Grounds Server for sending a message containing a blacklisted word.\nIf you would like to discuss your punishment, please contact Tabuu#0720, Phxenix#1104 or Parz#5811")
                except:
                    print("user has blocked me :(")

                #this function here checks the warn count on each user and if it reaches a threshold it will mute/kick/ban the user
                await Warn.check_warn_count(self, message.guild, message.channel, message.author)

                break




def setup(bot):
    bot.add_cog(On_message(bot))
    print("On_message cog loaded")