import typing as t
from pypokerstar.src.game.poker import Hand, Bet, Player
from abc import abstractmethod, ABC


class Metric(ABC):
    def __init__(self, hands: t.Iterable[Hand], hero: Player):
        self.hands = hands
        self.hero = hero

    @abstractmethod
    def get(self) -> t.Union[int, float]:
        pass


class VPIP(Metric):
    def __init__(self, hands: t.Iterable[Hand], hero: Player) -> None:
        super().__init__(hands, hero)

    def get(self) -> float:
        vpip_raw = 0
        for hand in self.hands:
            preflop = hand.get_round("hole cards")
            if preflop:
                if any(
                    [
                        bet.player.name == self.hero.name
                        and bet.type
                        in [
                            "calls",
                            "raises",
                        ]
                        for bet in preflop.bets
                    ]
                ):
                    vpip_raw += 1

        return 100 * vpip_raw / len(self.hands)


class WTSD(Metric):
    def __init__(self, hands: t.Iterable[Hand], hero: Player) -> None:
        super().__init__(hands, hero)

    def get(self) -> float:
        pass
