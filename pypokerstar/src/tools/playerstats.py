from pypokerstar.src.game.poker import Hand, Player
from pypokerstar.src.types import Card, Pair
import typing as t


class PlayerStats:
    def __init__(self, player: Player, hands: t.Iterable[Hand]) -> None:
        self.hands = hands
        self.player = player

        self.hands = self._filter_hands()

    def _filter_hands(self) -> t.Iterable[Hand]:
        return [hand for hand in self.hands if self.player in hand.players]

    def get_range(self) -> dict[int, t.Iterable[Card]]:
        range = {}
        """Returns a dictionary with the range the player playis in each position"""
        for hand in self.hands:
            cards = hand.get_player(self.player.name).cards
            round = hand.get_round("hole cards")
            for bet in round.bets:
                if (bet.player == self.player) and (bet.type in ["raises", "calls"]):
                    if range.get(Pair(*cards), None) is None:
                        range[Pair(*cards)] = 1
                    else:
                        range[Pair(*cards)] += 1
        return range
