from typing import Optional

import discord
from discord import app_commands
from stringmatch import Match


def search_role(guild: discord.Guild, input_role: str) -> Optional[discord.Role]:
    """Searches all of the guilds roles for the given input role.
    First we convert a possible role mention into the raw role ID.
    Then we look if the input matches the ID of any of the guilds roles.
    If that fails, we search the guilds roles for the closest match of the name using the stringmatch library.
    """
    # We get rid of the junk that comes with mentioning a role.
    unwanted = ["<", "@", ">", "&"]
    for i in unwanted:
        input_role = input_role.replace(i, "")

    all_roles = [role.name for role in guild.roles]

    match = Match(ignore_case=True, include_partial=True)

    try:
        role = discord.utils.get(guild.roles, id=int(input_role))

        # If the role is None we just search for it below.
        # This will happen if the input is an integer, but not a role ID.
        # Like when you would search for a role named "100".
        if not role:
            raise ValueError

    except ValueError:
        role_match = match.get_best_match(input_role, all_roles, score=55)
        role = discord.utils.get(guild.roles, name=role_match)

    return role


def autocomplete_choices(
    current: str, available_choices: list[str]
) -> list[app_commands.Choice]:
    """Returns a list of the first 25 autocomplete choices for the given current string
    and the choices supplied. Used primarily in autocompletion for slash commands.
    """
    match = Match(ignore_case=True, include_partial=True)

    matching_choices = []

    match_list = match.get_best_matches(
        current,
        available_choices,
        score=40,
        limit=25,
    )

    matching_choices.extend(
        app_commands.Choice(name=choice, value=choice) for choice in match_list
    )

    return matching_choices[:25]
