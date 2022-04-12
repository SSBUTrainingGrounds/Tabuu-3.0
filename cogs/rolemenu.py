import aiosqlite
import discord
from discord.ext import commands

import utils.check
from utils.ids import TGChannelIDs


class Rolemenu(commands.Cog):
    """
    Contains the commands used to make or modify role menus.
    As well as the listeners to add/remove these roles accordingly.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @utils.check.is_moderator()
    async def newrolemenu(self, ctx, message: int, emoji: str, role: discord.Role):
        """
        Creates a brand new role menu.
        """
        # makes sure the message and emoji are valid
        try:
            reactionmessage = await ctx.fetch_message(message)
            await reactionmessage.add_reaction(emoji)

        except discord.HTTPException:
            await ctx.send(
                "Either the message ID is invalid or I don't have access to this emoji. "
                "Also make sure the message is in the same channel as this one."
            )
            return

        async with aiosqlite.connect("./db/database.db") as db:
            rolemenu_message = await db.execute_fetchall(
                """SELECT exclusive, rolereq FROM reactrole WHERE message_id = :message_id""",
                {"message_id": message},
            )

            # if a message already exists in the database,
            # it will use these values for exclusivity and rolereq
            # otherwise we'll use the default values
            if len(rolemenu_message) == 0:
                exclusive = False
                rolereq = None
            else:
                exclusive = rolemenu_message[0][0]
                rolereq = rolemenu_message[0][1]

            await db.execute(
                """INSERT INTO reactrole VALUES (:message_id, :exclusive, :rolereq, :emoji, :role)""",
                {
                    "message_id": message,
                    "exclusive": exclusive,
                    "rolereq": rolereq,
                    "emoji": emoji,
                    "role": role.id,
                },
            )

            await db.commit()

        await ctx.send(
            f"Added an entry for Message ID #{message}, Emoji {emoji}, and Role {role.name}"
        )

    @commands.command()
    @utils.check.is_moderator()
    async def modifyrolemenu(
        self,
        ctx,
        message: int,
        exclusive: bool = False,
        rolereqs: commands.Greedy[discord.Role] = None,
    ):
        """
        Modifies a role menu with either a role requirement, or makes it "exclusive".
        Which means that a user can only have 1 of those roles at once.
        """

        # if there are rolereqs supplied, gets every role in there
        if rolereqs is not None:
            rolereq_ids = []
            rolereq_names = []

            # saves the role ids and names
            for role in rolereqs:
                rolereq_ids.append(str(role.id))
                rolereq_names.append(role.name)

            rolereq_id_store = " ".join(rolereq_ids)
            rolereq_name_store = ", ".join(rolereq_names)
        else:
            rolereq_id_store = None
            # this is just for the confirmation message
            rolereq_name_store = "None"

        async with aiosqlite.connect("./db/database.db") as db:
            rolemenu_entries = await db.execute_fetchall(
                """SELECT * FROM reactrole WHERE message_id = :message_id""",
                {"message_id": message},
            )

            if len(rolemenu_entries) == 0:
                await ctx.send("I didn't find an entry for this message.")
                return

            await db.execute(
                """UPDATE reactrole SET exclusive = :exclusive, rolereq = :rolereq WHERE message_id = :message_id""",
                {
                    "exclusive": exclusive,
                    "rolereq": rolereq_id_store,
                    "message_id": message,
                },
            )

            await db.commit()

        await ctx.send(
            f"I have set the Role requirement to {rolereq_name_store} "
            f"and the Exclusive requirement to {exclusive} for the Role menu message ID {message}."
        )

    @commands.command()
    @utils.check.is_moderator()
    async def deleterolemenu(self, ctx, message: int):
        """
        Completely deletes a role menu entry from the database.
        """

        async with aiosqlite.connect("./db/database.db") as db:
            rolemenu_entries = await db.execute_fetchall(
                """SELECT * FROM reactrole WHERE message_id = :message_id""",
                {"message_id": message},
            )

            if len(rolemenu_entries) == 0:
                await ctx.send("This message was not used for role menus.")
                return

            await db.execute(
                """DELETE FROM reactrole WHERE message_id = :message_id""",
                {"message_id": message},
            )

            await db.commit()

        await ctx.send(f"Deleted every entry for Message ID #{message}.")

    @commands.command()
    @utils.check.is_moderator()
    async def geteveryrolemenu(self, ctx):
        """
        Lists every currently active role menu.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            rolemenu_entries = await db.execute_fetchall(
                """SELECT * FROM reactrole ORDER BY message_id ASC"""
            )

        unique_messages = []
        embed_description = []

        for entry in rolemenu_entries:
            (message_id, exclusive, rolereq, emoji, role) = entry
            # to make it more readable
            exclusive = "False" if exclusive == 0 else "True"

            # converts the role reqs saved into mentions, if they exist
            if rolereq is not None:
                role_mentions_list = [
                    f"<@&{unique_role}>" for unique_role in rolereq.split()
                ]

                role_mentions_list = " ".join(role_mentions_list)

                rolereq = role_mentions_list

            # if its the first message in the list, it creates the "header" too
            if message_id not in unique_messages:
                unique_messages.append(message_id)
                embed_description.append(
                    f"\n**{message_id}:**\nExclusive: {exclusive} | Role(s) required: {rolereq}\n{emoji} = <@&{role}>"
                )

            # else it will just append
            else:
                embed_description.append(f"{emoji} = <@&{role}>")

        embed_description = "\n".join(embed_description)

        if not embed_description:
            embed_description = "No entries found."

        try:
            embed = discord.Embed(
                title="Every role menu saved",
                description=embed_description,
                colour=discord.Colour.dark_blue(),
            )
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error! Too many entries to list!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # The listener to actually add the correct role on a raw reaction event
        # Also does the checking for the special properties

        # reactions outside of the server would throw an error otherwise
        if not payload.guild_id:
            return

        if payload.member.bot:
            return

        async with aiosqlite.connect("./db/database.db") as db:
            matching_entries = await db.execute_fetchall(
                """SELECT * FROM reactrole WHERE message_id = :message_id""",
                {"message_id": payload.message_id},
            )

        # if the message is not saved, returns
        if len(matching_entries) == 0:
            return

        # these values *should* be the same for every entry of a message
        exclusive = matching_entries[0][1]
        rolereq = matching_entries[0][2]

        if rolereq is not None:
            # you can have more than one required role,
            # you dont need every though, only one of them will be enough.
            roles_required = [
                discord.utils.get(
                    self.bot.get_guild(payload.guild_id).roles,
                    id=int(role_required),
                )
                for role_required in rolereq.split()
            ]

            if all(role not in payload.member.roles for role in roles_required):
                # checks if the user does not have the required roles
                for entry in matching_entries:
                    (_, _, _, emoji, role) = entry
                    # we only send a message if the entry matches
                    if str(payload.emoji) == emoji:
                        wanted_role = discord.utils.get(
                            self.bot.get_guild(payload.guild_id).roles, id=role
                        )

                        # sends a message telling them what roles they need
                        await payload.member.send(
                            f"The role {wanted_role.name} was not added to you "
                            "due to not having one or more of the following roles:"
                            f"{', '.join([missing_role.name for missing_role in roles_required])}.\n\n"
                            f"Check <#{TGChannelIDs.RULES_CHANNEL}> for information "
                            f"or inquire in <#{TGChannelIDs.HELP_CHANNEL}> if you cannot find the details on the required roles.",
                        )
                return

        if exclusive == 1:
            for entry in matching_entries:
                (_, _, _, _, role) = entry
                role_tbd = discord.utils.get(
                    self.bot.get_guild(payload.guild_id).roles, id=role
                )
                if role_tbd in payload.member.roles:
                    await payload.member.remove_roles(role_tbd)

        for entry in matching_entries:
            (_, _, _, emoji, role) = entry
            if str(payload.emoji) == emoji:
                role_tbd = discord.utils.get(
                    self.bot.get_guild(payload.guild_id).roles, id=role
                )
                await payload.member.add_roles(role_tbd)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # The listener to remove the correct role on a raw reaction remove event
        # Does not need any additional checking
        async with aiosqlite.connect("./db/database.db") as db:
            matching_entries = await db.execute_fetchall(
                """SELECT * FROM reactrole WHERE message_id = :message_id""",
                {"message_id": payload.message_id},
            )

        if len(matching_entries) == 0:
            return

        for entry in matching_entries:
            (_, _, _, emoji, role) = entry
            # The last 20 digits are the emoji ID, if it is custom.
            # I have to do this because of animated emojis.
            # And this event here doesnt recognise them properly.
            # It doesnt send any information on whether or not the emoji is animated or not.
            if str(payload.emoji)[-20:] == emoji[-20:]:
                role_tbd = discord.utils.get(
                    self.bot.get_guild(payload.guild_id).roles, id=role
                )
                # Also i have to get the member like this because this event listener is bs
                await self.bot.get_guild(payload.guild_id).get_member(
                    payload.user_id
                ).remove_roles(role_tbd)

    # generic error handling
    @newrolemenu.error
    async def newrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.BadArgument, commands.MissingRequiredArgument)
        ):
            await ctx.send(
                "Something was not recognized properly. The syntax for this command is: \n"
                "`%newrolemenu <message_id> <emoji> <role>`"
            )
        else:
            raise error

    @deleterolemenu.error
    async def deleterolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.BadArgument)
        ):
            await ctx.send("You need to input a valid message ID.")
        else:
            raise error

    @modifyrolemenu.error
    async def modifyrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                "I could not find one or more of these roles! Make sure you got the right ones."
            )
        elif isinstance(error, commands.BadBoolArgument):
            await ctx.send(
                "You need to input a boolean value for both arguments, True or False."
            )
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.BadArgument)
        ):
            await ctx.send("You need to input a valid message ID.")
        else:
            raise error

    @geteveryrolemenu.error
    async def geteveryrolemenu_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Rolemenu(bot))
    print("Rolemenu cog loaded")
