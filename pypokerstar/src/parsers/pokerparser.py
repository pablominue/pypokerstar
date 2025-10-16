import os
import typing as t

from pypokerstar.src.game.poker import Bet, Hand, Player, Round
from pypokerstar.src.types import Card


class PokerParser:
    def __init__(self) -> None:
        self.hands: t.List[dict[t.Any, t.Any]] = []

    def add_hands(self, hands: t.Iterable[Hand]) -> None:
        for hand in hands:
            self.hands.append(hand)

    def export(self, directory: str) -> None:
        if not os.path.exists(directory):
            os.makedirs(directory)
