import os

import polars as pl

from pypokerstar.src.game.poker import History, Player, Hand
from pypokerstar.src.metrics.metrics import VPIP
from pypokerstar.src.parsers.pokerstars import PokerStarsParser
from pypokerstar.src.tools.playerstats import PlayerStats

import phevaluator
from phevaluator.evaluator import evaluate_cards


player = Player(name="pipinoelbreve9")
hands = PokerStarsParser("").parse_dir("PokerStars/", hero=player)
history = History(hands=hands, hero=player)

for hand in history.hands:
    print(hand)
    for round in hand.rounds:
        print(round.get_hero_equity(hero=hand.hero, iterations=1000))


# df = history.get_money_history()

# with pl.Config() as cfg:
#     cfg.set_tbl_cols(10)

# df = df.to_pandas()
# print(
#     df.sort_values(by="net", ascending=True)[["date", "pot", "net", "won", "total_bet"]]
# )