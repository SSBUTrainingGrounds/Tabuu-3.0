from discord.ext import commands

from utils.ids import BGRoleIDs, TGRoleIDs


def is_moderator():
    """
    Custom check if the user can invoke the Admin Commands.
    Returns True if the author:
        -Is the Server Owner,
        -Has Administrator Rights,
        -Has the Moderator Role (Grounds Warrior),
    in that order.
    If neither of these things are true, we raise the MissingPermissions Error.
    """

    def predicate(ctx: commands.Context):
        # if the command is invoked in dm's we return the error immediately.
        if ctx.guild is None:
            raise commands.MissingPermissions(["Moderator"])

        # first we check if the author is the guild owner.
        if ctx.guild.owner.id == ctx.author.id:
            return True

        # then we check for admin privileges, which i guess the owner also has
        if ctx.author.guild_permissions.administrator is True:
            return True

        # and lastly we check if the author has any of the two moderator roles
        author_role_ids = [role.id for role in ctx.author.roles]
        mod_role_ids = [TGRoleIDs.MOD_ROLE, BGRoleIDs.MOD_ROLE]

        if any(role in author_role_ids for role in mod_role_ids):
            return True

        # and if not we raise the error again.
        raise commands.MissingPermissions(["Moderator"])

    return commands.check(predicate)
