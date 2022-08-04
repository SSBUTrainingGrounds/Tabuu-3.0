from discord.ext import commands

from cogs.ranking import Ranking


def test_calculate_elo() -> None:
    assert Ranking(commands.Bot).calculate_elo(1000, 1000) == (1016, 984, 16)
    assert Ranking(commands.Bot).calculate_elo(500, 1500) == (532, 1468, 32)
    assert Ranking(commands.Bot).calculate_elo(500, 500) == (516, 484, 16)
    assert Ranking(commands.Bot).calculate_elo(90, 2800) == (122, 2768, 32)
    assert Ranking(commands.Bot).calculate_elo(1030, 1101) == (1049, 1082, 19)
    assert Ranking(commands.Bot).calculate_elo(1132, 950) == (1140, 942, 8)
