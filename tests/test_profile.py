import unittest

from discord.app_commands import Choice

from cogs.profile import Profile


class TestTime(unittest.TestCase):
    def test_match_character(self):
        # some basic matching
        self.assertEqual(
            Profile.match_character(self, "mario"), ["<:Mario:929067419861913680>"]
        )
        # more advanced
        self.assertEqual(
            Profile.match_character(self, "incin, wii fit trainer, 4e"),
            [
                "<:Incineroar:929086965763145828>",
                "<:WiiFitTrainer:929086966115483748>",
                "<:DarkSamus:929068123020202004>",
            ],
        )
        # matching one input to more than one char
        self.assertEqual(
            Profile.match_character(self, "chroy, paisy"),
            [
                "<:Roy:929069540460097537>",
                "<:Chrom:929069556243238932>",
                "<:Peach:929068723829080105>",
                "<:Daisy:929068737317986324>",
            ],
        )

    def test_character_autocomplete(self):
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

        self.assertEqual(Profile.character_autocomplete(self, "Incin"), incin_query)
        self.assertEqual(Profile.character_autocomplete(self, "w"), w_query)
        self.assertEqual(
            Profile.character_autocomplete(self, "mr. game and watch"), gnw_query
        )
        self.assertEqual(Profile.character_autocomplete(self, "Mario, Dr. M"), dr_query)
        self.assertEqual(Profile.character_autocomplete(self, "what, e"), e_query)


if __name__ == "__main__":
    unittest.main()
