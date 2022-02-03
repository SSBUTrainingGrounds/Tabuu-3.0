import discord
from discord.ext import commands
import json


class Rolemenu(commands.Cog):
    """
    Contains the commands used to make or modify role menus.
    As well as the listeners to add/remove these roles accordingly.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newrolemenu(self, ctx, message: int, emoji, role: discord.Role):
        """
        Creates a brand new role menu.
        """
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        # makes sure the message and emoji are valid
        try:
            reactionmessage = await ctx.fetch_message(message)
            await reactionmessage.add_reaction(emoji)

        except:
            await ctx.send(
                "Either the message ID is invalid or I don't have access to this emoji. Also make sure the message is in the same channel as this one."
            )
            return

        if f"{message}" in data.keys():
            data[f"{message}"].append([{"emoji": emoji, "role": role.id}])
        else:
            data[f"{message}"] = [[]]  # double list for proper indentation
            data[f"{message}"] = [
                {"exclusive": False, "rolereq": None}
            ]  # default values for the special properties, only once per message
            data[f"{message}"] += [[{"emoji": emoji, "role": role.id}]]

        with open(r".\json\reactrole.json", "w") as f:  # writes it to the file
            json.dump(data, f, indent=4)

        await ctx.send(
            f"Added an entry for Message ID #{message}, Emoji {emoji}, and Role {role.name}"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modifyrolemenu(
        self, ctx, message: int, exclusive: bool = False, rolereq: discord.Role = None
    ):
        """
        Modifies a role menu with either a role requirement, or makes it "exclusive".
        Which means that a user can only have 1 of those roles at once.
        """
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        if not f"{message}" in data.keys():  # quick check if the message is in there
            await ctx.send("I didn't find an entry for this message.")
            return

        # if the rolereq is a role we need to set it to the role.id if it is not a role and simply a "None"
        # rolereq will not have an attribute id, and thus we need to set it to just rolereq
        data[f"{message}"][0]["rolereq"] = (
            rolereq.id if rolereq is not None else rolereq
        )
        data[f"{message}"][0]["exclusive"] = exclusive

        with open(r".\json\reactrole.json", "w") as f:  # writes it to the file
            json.dump(data, f, indent=4)
        try:
            await ctx.send(
                f"I have set the Role requirement to {rolereq.name} and the Exclusive requirement to {exclusive} for the Role menu message ID {message}."
            )
        # if rolereq is none we cant reference it by name
        except:
            await ctx.send(
                f"I have set the Role requirement to {rolereq} and the Exclusive requirement to {exclusive} for the Role menu message ID {message}."
            )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleterolemenu(self, ctx, message: int):
        """
        Completely deletes a role menu entry from the json file.
        """
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        if f"{message}" in data.keys():  # quick check if the message is in there
            del data[f"{message}"]
            await ctx.send(f"Deleted every entry for Message ID #{message}.")
        else:
            await ctx.send("This message was not used for role menus.")

        with open(r".\json\reactrole.json", "w") as f:  # writes it to the file
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def geteveryrolemenu(self, ctx):
        """
        Lists every currently active role menu.
        """
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        message = []

        for x in data:
            entrys = data[f"{x}"]
            list = []
            for i in entrys:
                # either gets the role/emoji combo, or the special properties set
                try:
                    list.append(f"{i[0]['emoji']} = <@&{i[0]['role']}>")
                except:
                    rolereq = i["rolereq"]
                    exclusive = i["exclusive"]
                sent_list = "\n".join(list)
            if rolereq is not None:
                rolereq = f"<@&{rolereq}>"
            message.append(
                f"**{x}:**\nExclusive: {exclusive} | Role required: {rolereq}\n{sent_list}\n\n"
            )
        all_messages = "".join(message)

        if len(all_messages) == 0:
            all_messages = "No entry found."

        try:
            embed = discord.Embed(
                title="Every role menu saved",
                description=all_messages,
                colour=discord.Color.dark_blue(),
            )

            await ctx.send(embed=embed)
        except:
            await ctx.send("Too many to list in a single message.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # The listener to actually add the correct role on a raw reaction event
        # Also does the checking for the special properties
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        # reactions outside of the server would throw an error otherwise
        if not payload.guild_id:
            return

        if payload.member.bot:
            return

        if f"{payload.message_id}" in data.keys():
            if data[f"{payload.message_id}"][0]["rolereq"] is not None:
                role_required = discord.utils.get(
                    self.bot.get_guild(payload.guild_id).roles,
                    id=data[f"{payload.message_id}"][0]["rolereq"],
                )
                if role_required not in payload.member.roles:
                    return
            # if the exclusive value is set to true it will fist remove every role you already have that is in that role menu ID
            if data[f"{payload.message_id}"][0]["exclusive"] == True:
                entrys = data[f"{payload.message_id}"]
                # gets every entry except the first one, which is the role/exclusive thing itself so it needs to skip that
                for x in entrys[1:]:
                    role = discord.utils.get(
                        self.bot.get_guild(payload.guild_id).roles, id=x[0]["role"]
                    )
                    if role in payload.member.roles:
                        await payload.member.remove_roles(role)
            entrys = data[f"{payload.message_id}"]
            for x in entrys[1:]:
                if str(payload.emoji) == x[0]["emoji"]:
                    role = discord.utils.get(
                        self.bot.get_guild(payload.guild_id).roles, id=x[0]["role"]
                    )
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # The listener to remove the correct role on a raw reaction remove event
        # Does not need any additional checking
        with open(r".\json\reactrole.json", "r") as f:
            data = json.load(f)

        if f"{payload.message_id}" in data.keys():
            entrys = data[f"{payload.message_id}"]
            for x in entrys[1:]:
                # The last 20 digits are the emoji ID, if it is custom.
                # I have to do this because of animated emojis.
                # And this event here doesnt recognise them properly.
                # It doesnt send any information on whether or not the emoji is animated or not.
                if str(payload.emoji)[-20:] == x[0]["emoji"][-20:]:
                    role = discord.utils.get(
                        self.bot.get_guild(payload.guild_id).roles, id=x[0]["role"]
                    )
                    # Also i have to get the member like this because this event listener is bs
                    await self.bot.get_guild(payload.guild_id).get_member(
                        payload.user_id
                    ).remove_roles(role)

    # generic error handling
    @newrolemenu.error
    async def newrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                "Something was not recognized properly. The syntax for this command is: \n`%newrolemenu <message_id> <emoji> <role>`"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Something was not recognized properly. The syntax for this command is: \n`%newrolemenu <message_id> <emoji> <role>`"
            )
        else:
            raise error

    @deleterolemenu.error
    async def deleterolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to input a valid message ID.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("You need to input a valid message ID.")
        else:
            raise error

    @modifyrolemenu.error
    async def modifyrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.BadBoolArgument):
            await ctx.send(
                "You need to input a boolean value for both arguments, True or False."
            )
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
        else:
            raise error


def setup(bot):
    bot.add_cog(Rolemenu(bot))
    print("Rolemenu cog loaded")
