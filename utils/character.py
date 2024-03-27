import json

from typing import Optional


def get_single_character_name(input_character: str) -> Optional[str]:
    """Returns the name of the character based on the input.
    Works with names, commonly used nicknames or Fighters ID Number.
    Example:
        Input: incin
        Output: "incineroar"
    """
    with open(r"./files/characters.json", "r", encoding="utf-8") as f:
        characters = json.load(f)

    if input_character is None:
        return None

    input_character = input_character.lower()

    # Characters that you can't really "main", so I didn't account for them when creating that json file.
    # But, they are still valid inputs here.
    # Luckily, they don't really need nicknames.
    special_characters = ["squirtle", "ivysaur", "charizard", "pyra", "mythra"]

    if input_character in special_characters:
        return input_character

    for match_char in characters["Characters"]:
        if (
            input_character == match_char["name"]
            or input_character in match_char["id"]
            or input_character in match_char["aliases"]
        ):
            return match_char["name"]

    return None


def match_character(profile_input: str) -> list[str]:
    """Matches the input to one or multiple characters and returns the corresponding emoji.
    Separates the input by commas.
    Works with names, commonly used nicknames or Fighters ID Number.
    Example:
        Input: incin, wii fit trainer, 4e
        Output: [
            <:Incineroar:929086965763145828>,
            <:WiiFitTrainer:929086966115483748>,
            <:DarkSamus:929068123020202004>,
        ]
    """
    with open(r"./files/characters.json", "r", encoding="utf-8") as f:
        characters = json.load(f)

    output_characters = []

    if profile_input is None:
        return output_characters

    profile_input = profile_input.lower()
    input_characters = profile_input.split(",")

    for i_char in input_characters:
        # This strips leading and trailing whitespaces.
        i_char = i_char.strip()

        for match_char in characters["Characters"]:
            # 2 characters (pt, aegis) have more than 1 id, so the ids need to be in a list.
            if (
                i_char == match_char["name"]
                or i_char in match_char["id"]
                or i_char in match_char["aliases"]
            ) and match_char["emoji"] not in output_characters:
                output_characters.append(match_char["emoji"])

    return output_characters
