import discord
from fuzzywuzzy import process

#this here searches a matching role from your input, works with role mention, role ID, or closest name match
def search_role(guild: discord.Guild, input_role):
    #we get rid of the junk that comes with mentioning a role
    unwanted = ['<','@','>', '&']
    for i in unwanted:
        input_role = input_role.replace(i,'')

    all_roles = []
    for role in guild.roles:
        all_roles.append(role.name)

    #first we try to get the role straight from the ID
    try:
        role = discord.utils.get(guild.roles, id=int(input_role))
    #if that fails, we search for the closest matching name
    except:
        match = process.extractOne(input_role, all_roles, score_cutoff=30)[0]
        role = discord.utils.get(guild.roles, name=match)

    return role