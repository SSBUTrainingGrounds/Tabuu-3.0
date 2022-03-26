import unittest

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


if __name__ == "__main__":
    unittest.main()
