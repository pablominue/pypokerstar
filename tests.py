import os

import polars as pl

from pypokerstar.src.game.poker import History, Player, Hand
from pypokerstar.src.metrics.metrics import VPIP
from pypokerstar.src.parsers.pokerstars import PokerStarsParser
from pypokerstar.src.tools.playerstats import PlayerStats


player = Player(name="pipinoelbreve9")
hands = PokerStarsParser("").parse_dir("PokerStars/", hero=player)
history = History(hands=hands, hero=player)



df = history.get_money_history()

with pl.Config() as cfg:
    cfg.set_tbl_cols(10)

df = df.to_pandas()
print(
    df.sort_values(by="net", ascending=True)[["date", "pot", "net", "won", "total_bet"]]
)

import matplotlib.pyplot as plt
df.set_index("date")[["net"]].cumsum().plot()
plt.savefig("out2.png")
