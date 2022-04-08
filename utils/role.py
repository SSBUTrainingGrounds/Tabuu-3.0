from typing import Optional

import discord
from fuzzywuzzy import process


def search_role(guild: discord.Guild, input_role: str) -> Optional[discord.Role]:
    """
    Searches all of the guilds roles for the given input role.
    First we convert a possible role mention into the raw role ID.
    Then we look if the input matches the ID of any of the guilds roles.
    If that fails, we search the guilds roles for the closest match of the name using the fuzzywuzzy library.
    """
    # we get rid of the junk that comes with mentioning a role
    unwanted = ["<", "@", ">", "&"]
    for i in unwanted:
        input_role = input_role.replace(i, "")

    all_roles = [role.name for role in guild.roles]

    try:
        role = discord.utils.get(guild.roles, id=int(input_role))
    except ValueError:
        match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
        role = discord.utils.get(guild.roles, name=match)

    return role
