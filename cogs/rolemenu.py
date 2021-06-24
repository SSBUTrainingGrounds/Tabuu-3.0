import discord
from discord.ext import commands, tasks
import json

#
#this file here contains the role menus and the listeners to add the roles
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
            await ctx.send("Either the message ID is invalid or I don't have access to this emoji. Also make sure the message is in the same channel as this one.")
            return


        if f'{message}' in data.keys():
            data[f'{message}'].append([{"emoji":emoji, "role":role.id}])
        else:
            data[f'{message}'] = [[]] #double list for proper indentation
            data[f'{message}'] = [{"exclusive":False, "rolereq":None}] #default values for the special properties, only once per message
            data[f'{message}'] += ([[{"emoji":emoji, "role": role.id}]])

        with open(r'/root/tabuu bot/json/reactrole.json', 'w') as f: #writes it to the file
            json.dump(data, f, indent=4)

        await ctx.send(f"Added an entry for Message ID #{message}, Emoji {emoji}, and Role {role.name}")

    #modifies the special values
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modifyrolemenu(self, ctx, message:int, exclusive:bool = False, rolereq:discord.Role = None):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        if not f'{message}' in data.keys(): #quick check if the message is in there
            await ctx.send("I didn't find an entry for this message.")
            return
        
        data[f'{message}'][0]['rolereq'] =  rolereq.id if rolereq is not None else rolereq  #if the rolereq is a role we need to set it to the role.id if it is not a role and simply a "None"
        data[f'{message}'][0]['exclusive'] = exclusive                                      #rolereq will not have an attribute id, and thus we need to set it to just rolereq


        with open(r'/root/tabuu bot/json/reactrole.json', 'w') as f: #writes it to the file
            json.dump(data, f, indent=4)
        try:
            await ctx.send(f"I have set the Role requirement to {rolereq.name} and the Exclusive requirement to {exclusive} for the Role menu message ID {message}.")
        except: #if rolereq is none it throws an error, quick fix around
            await ctx.send(f"I have set the Role requirement to {rolereq} and the Exclusive requirement to {exclusive} for the Role menu message ID {message}.")


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

        message = []

        for x in data: #gets every message entry
            entrys = data[f'{x}']
            list = []
            for i in entrys: #for each value in each message entry
                try:
                    list.append(f"{i[0]['emoji']} = <@&{i[0]['role']}>") #either gets the role/emoji combo
                except: #or gets the special values
                    rolereq = i['rolereq']
                    exclusive = i['exclusive']
                sent_list = '\n'.join(list) #then combines the entry for one message
            if rolereq is not None:
                rolereq = f"<@&{rolereq}>"
            message.append(f"**{x}:**\nExclusive: {exclusive} | Role required: {rolereq}\n{sent_list}\n\n") #then combines the entry for every message
        all_messages = ''.join(message) #to put it in the embed in a nice format

        if len(sent_list) == 0:
            sent_list = "No entry found."

        try:
            embed = discord.Embed(title="Every role menu saved", description=all_messages, colour=discord.Color.dark_blue())

            await ctx.send(embed=embed)
        except:
            await ctx.send("Too many to list in a single message.")




    #listeners to actually add/remove the roles
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        if not payload.guild_id: #reactions outside of the server would throw an error otherwise
            return
        
        if payload.member.bot:
            return

        if f'{payload.message_id}' in data.keys():
            if data[f'{payload.message_id}'][0]['rolereq'] is not None: #if the rolereq is set, this executes
                role_required = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=data[f'{payload.message_id}'][0]['rolereq'])
                if role_required not in payload.member.roles: #otherwise it will just return
                    return
            if data[f'{payload.message_id}'][0]['exclusive'] == True: #if the exclusive value is set to true it will fist remove every role you already have that is in that role menu ID
                entrys = data[f'{payload.message_id}']
                for x in entrys[1:]: #gets every entry except the first one, which is the role/exclusive thing itself so it needs to skip that
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[0]['role'])
                    if role in payload.member.roles:
                        await payload.member.remove_roles(role)
            entrys = data[f'{payload.message_id}']
            for x in entrys[1:]: #gets every entry except the first one, which is the role/exclusive thing itself so it needs to skip that
                if str(payload.emoji) == x[0]['emoji']:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[0]['role'])
                    await payload.member.add_roles(role)

    #pretty much the same as above, only to remove the role again, no need for any checks though
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        with open(r'/root/tabuu bot/json/reactrole.json', 'r') as f:
            data = json.load(f)

        if f'{payload.message_id}' in data.keys():
            entrys = data[f'{payload.message_id}']
            for x in entrys:
                if str(payload.emoji)[-20:] == x[0]['emoji'][-20:]: #the last 20 digits are the emoji ID, if it is custom. I have to do this because of animated emojis
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[0]['role']) #and this event here doesnt recognise them properly. discord is stupid basically
                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role) #also i have to get the member like this because this event listener is bs



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

    @modifyrolemenu.error
    async def modifyrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.BadBoolArgument):
            await ctx.send("You need to input a boolean value for both arguments, True or False.")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Invalid role! Please input a valid Role.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a valid message ID.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("You need to input a valid message ID.")
        raise error
    
    @geteveryrolemenu.error
    async def geteveryrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        raise error


def setup(bot):
    bot.add_cog(Rolemenu(bot))
    print("Rolemenu cog loaded")