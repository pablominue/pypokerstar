from src.parsers.pokerstars import PokerStarsParser
from src.game.poker import Player
from src.tools.playerstats import PlayerStats
import os 


parser = PokerStarsParser("tests/pokerdata.txt")
hands = parser.parse()
player = Player(name="pipinoelbreve9")
stats = PlayerStats(player, hands)
range = stats.get_range()

range = {str(k): v for k, v in range.items()}
print(range)