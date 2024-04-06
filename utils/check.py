import discord
from discord.ext import commands

from utils.ids import BGRoleIDs, GuildIDs, TGRoleIDs


def is_moderator():
    """Custom check if the user can invoke the Admin Commands.

    Returns True if the author:
        -Is the Server Owner,
        -Has Administrator Rights,
        -Has the Moderator Role (Grounds Warrior)

    If neither of these things are true, we raise the MissingPermissions Error.
    """

    def predicate(ctx: commands.Context):
        # If the command is invoked in dm's we return the error immediately.
        if ctx.guild is None:
            raise commands.MissingPermissions(["Moderator"])

        if ctx.guild.id not in [x.id for x in GuildIDs.ADMIN_GUILDS]:
            raise commands.MissingPermissions(
                ["This guild is not allowed to do Moderation actions."]
            )

        # First we check if the author is the guild owner.
        if ctx.guild.owner and ctx.guild.owner.id == ctx.author.id:
            return True

        if isinstance(ctx.author, discord.Member):
            # Then we check for admin privileges, which i guess the owner also has.
            if ctx.author.guild_permissions.administrator is True:
                return True

            # And lastly we check if the author has any of the moderator roles.
            author_role_ids = [role.id for role in ctx.author.roles]
            mod_role_ids = [TGRoleIDs.MOD_ROLE, BGRoleIDs.MOD_ROLE]

            if any(role in author_role_ids for role in mod_role_ids):
                return True

        # And if not we raise the error again.
        raise commands.MissingPermissions(["Moderator"])

    return commands.check(predicate)
