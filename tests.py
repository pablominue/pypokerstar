import os
import collections
import typing as t
from collections import defaultdict, Counter


import polars as pl

from pypokerstar.src.game.poker import History, Player, Hand
from pypokerstar.src.parsers.pokerstars import PokerStarsParser

from rich.progress import Progress

player = Player(name="pipinoelbreve9")
hands = PokerStarsParser("").parse_dir("PokerStars/", hero=player)
history = History(hands=hands, hero=player)

df = history.get_main_stats(hero=player)

print(df)