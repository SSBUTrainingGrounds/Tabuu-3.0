from utils.character import get_single_character_name, match_character


def test_match_character() -> None:
    # some basic matching
    assert match_character("mario") == ["<:Mario:929067419861913680>"]
    # more advanced
    assert match_character("incin, wii fit trainer, 4e") == [
        "<:Incineroar:929086965763145828>",
        "<:WiiFitTrainer:929086966115483748>",
        "<:DarkSamus:929068123020202004>",
    ]

    # matching one input to more than one char
    assert match_character("chroy, paisy") == [
        "<:Roy:929069540460097537>",
        "<:Chrom:929069556243238932>",
        "<:Peach:929068723829080105>",
        "<:Daisy:929068737317986324>",
    ]


def test_get_single_character_name() -> None:
    assert get_single_character_name("incin") == "incineroar"
    assert get_single_character_name("wii fit") == "wii fit trainer"
    assert get_single_character_name("4e") == "dark samus"
    assert get_single_character_name("mario") == "mario"
    assert get_single_character_name("chroy") == "roy"
    assert get_single_character_name("paisy") == "peach"
    assert get_single_character_name("squirtle") == "squirtle"
    assert get_single_character_name("ivysaur") == "ivysaur"
    assert get_single_character_name("charizard") == "charizard"
    assert get_single_character_name("pyra") == "pyra"
    assert get_single_character_name("mythra") == "mythra"
    assert get_single_character_name("11") == "captain falcon"
