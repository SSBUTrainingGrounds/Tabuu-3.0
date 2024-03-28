# type: ignore

from discord.app_commands import Choice
from discord.ext import commands

from cogs.profile import Profile


def test_character_autocomplete() -> None:
    incin_query = [
        Choice(name="Incineroar", value="Incineroar"),
        Choice(name="Inkling", value="Inkling"),
        Choice(name="Min Min", value="Min Min"),
        Choice(name="Lucina", value="Lucina"),
        Choice(name="Greninja", value="Greninja"),
        Choice(name="Corrin", value="Corrin"),
        Choice(name="Toon Link", value="Toon Link"),
        Choice(name="Link", value="Link"),
        Choice(name="Captain Falcon", value="Captain Falcon"),
        Choice(name="Luigi", value="Luigi"),
        Choice(name="Pichu", value="Pichu"),
        Choice(name="Sonic", value="Sonic"),
        Choice(name="Robin", value="Robin"),
        Choice(name="Simon", value="Simon"),
        Choice(name="Young Link", value="Young Link"),
        Choice(name="Mii Gunner", value="Mii Gunner"),
    ]

    w_query = [
        Choice(name="Wolf", value="Wolf"),
        Choice(name="Wario", value="Wario"),
        Choice(name="Wii Fit Trainer", value="Wii Fit Trainer"),
    ]

    gnw_query = [
        Choice(name="Mr. Game & Watch", value="Mr. Game & Watch"),
        Choice(name="Mega Man", value="Mega Man"),
        Choice(name="Peach", value="Peach"),
        Choice(name="Pac Man", value="Pac Man"),
    ]

    dr_query = [
        Choice(name="Mario, Dr. Mario", value="Mario, Dr. Mario"),
        Choice(name="Mario, Dark Samus", value="Mario, Dark Samus"),
        Choice(name="Mario, Dark Pit", value="Mario, Dark Pit"),
        Choice(name="Mario, King K. Rool", value="Mario, King K. Rool"),
    ]

    e_query = [
        Choice(name="what, Ike", value="what, Ike"),
        Choice(name="what, Ken", value="what, Ken"),
    ]

    assert Profile(commands.Bot).character_autocomplete("Incin") == incin_query
    assert Profile(commands.Bot).character_autocomplete("w") == w_query
    assert (
        Profile(commands.Bot).character_autocomplete("mr. game and watch") == gnw_query
    )

    assert Profile(commands.Bot).character_autocomplete("Mario, Dr. M") == dr_query
    assert Profile(commands.Bot).character_autocomplete("what, e") == e_query
