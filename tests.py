from pypokerstar.src.parsers.pokerstars import PokerStarsParser
from pypokerstar.src.game.poker import Player
from pypokerstar.src.tools.playerstats import PlayerStats
import os
from pypokerstar.src.metrics.metrics import VPIP


parser = PokerStarsParser("tests/pokerdata.txt")
player = Player(name="pipinoelbreve9")
hands = parser.parse_dir(
    "/Users/pablominue/Library/CloudStorage/GoogleDrive-pablominue97@gmail.com/Mi unidad/HM3",
)
example = hands[1]

print(example)
