import unittest

from cogs.ranking import Ranking


class TestRanking(unittest.TestCase):
    def test_calculate_elo(self) -> None:
        self.assertEqual(Ranking.calculate_elo(self, 1000, 1000), (1016, 984, 16))
        self.assertEqual(Ranking.calculate_elo(self, 500, 1500), (532, 1468, 32))
        self.assertEqual(Ranking.calculate_elo(self, 500, 500), (516, 484, 16))
        self.assertEqual(Ranking.calculate_elo(self, 90, 2800), (122, 2768, 32))
        self.assertEqual(Ranking.calculate_elo(self, 1030, 1101), (1049, 1082, 19))
        self.assertEqual(Ranking.calculate_elo(self, 1132, 950), (1140, 942, 8))
