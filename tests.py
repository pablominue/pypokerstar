import os

import polars as pl

from pypokerstar.src.game.poker import History, Player
from pypokerstar.src.metrics.metrics import VPIP
from pypokerstar.src.parsers.pokerstars import PokerStarsParser
from pypokerstar.src.tools.playerstats import PlayerStats

parser = PokerStarsParser("tests/pokerdata.txt")
player = Player(name="pipinoelbreve9")
hands = parser.parse_dir("/home/pablo/Documents/HM3", hero=player)

history = History(hands=hands, hero=player)
df = history.get_money_history()

with pl.Config() as cfg:
    cfg.set_tbl_cols(10)
    print(df)
    print(df.get_column("rake").max())

df = df.to_pandas()

import matplotlib.pyplot as plt
df.set_index("date")[["net"]].cumsum().plot()
plt.savefig("out.png")