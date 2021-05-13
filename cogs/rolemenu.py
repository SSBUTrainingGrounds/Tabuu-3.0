import discord
from discord.ext import commands, tasks
import json

#
#this file here will maybe contain the role menus
#

class Rolemenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #first the commands to add/remove entrys from our json file, this here to add. admin only obv
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newrolemenu(self, ctx, message:int, emoji, role:discord.Role):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        try: #makes sure the message and emoji are valid
            reactionmessage = await ctx.fetch_message(message)
            await reactionmessage.add_reaction(emoji)

        except:
            await ctx.send("Either the message ID is invalid or I don't have access to this emoji.")
            return


        if f'{message}' in data.keys():
            data[f'{message}'].append([{"emoji":emoji, "role":role.id}])
        else:
            data[f'{message}'] = [[]] #double list for proper indentation
            data[f'{message}'] = ([[{"emoji":emoji, "role": role.id}]])

        with open(r'/root/tabuu bot/json/reactrole.json', 'w') as f: #writes it to the file
            json.dump(data, f, indent=4)

        await ctx.send(f"Added an entry for Message ID #{message}, Emoji {emoji}, and Role {role.name}")

    #deletes an entry from the json file
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleterolemenu(self, ctx, message:int):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)
        
        if f'{message}' in data.keys():
            del data[f'{message}']
            await ctx.send(f"Deleted every entry for Message ID #{message}")
        else:
            await ctx.send("This message was not used for role menus.")
        
        with open(r'/root/tabuu bot/json/reactrole.json', 'w') as f: #writes it to the file
            json.dump(data, f, indent=4)

    #gets you every role menu, just if you forget to delete something or whatever. thought this might be nicer than to manually look them up each time
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def geteveryrolemenu(self, ctx):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        list = []

        for x in data:
            entrys = data[f'{x}']
            for i in entrys:
                list.append(f"{x}, {i[0]['emoji']}, <@&{i[0]['role']}>")
        sent_list = '\n'.join(list)

        if len(sent_list) == 0:
            sent_list = "No entry found."

        try:
            embed = discord.Embed(title="Every role menu saved", description=sent_list, colour=discord.Color.dark_blue())

            await ctx.send(embed=embed)
        except:
            await ctx.send("Too many to list in a single message.")




    #listeners to actually add/remove the roles
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)
        
        if payload.member.bot:
            return

        if f'{payload.message_id}' in data.keys():
            entrys = data[f'{payload.message_id}']
            for x in entrys:
                if str(payload.emoji) == x[0]['emoji']:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[0]['role'])
                    await payload.member.add_roles(role)

    #pretty much the same as above, only to remove the role again
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        if f'{payload.message_id}' in data.keys():
            entrys = data[f'{payload.message_id}']
            for x in entrys:
                if str(payload.emoji) == x[0]['emoji']:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[0]['role'])
                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role) #have to get the member like this because when removing a reaction it only gets the id for whatever reason?



    #generic error handling
    @newrolemenu.error
    async def newrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something was not recognized properly. The syntax for this command is: \n`%newrolemenu <message_id> <emoji> <role>`")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Something was not recognized properly. The syntax for this command is: \n`%newrolemenu <message_id> <emoji> <role>`")
        raise error

    @deleterolemenu.error
    async def deleterolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a message ID.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("You need to input a message ID.")
        raise error
    
    @geteveryrolemenu.error
    async def geteeveryrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        raise error


def setup(bot):
    bot.add_cog(Rolemenu(bot))
    print("Rolemenu cog loaded")