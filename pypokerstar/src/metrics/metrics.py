import typing as t
from abc import ABC, abstractmethod

from pypokerstar.src.game.poker import Bet, Hand, Player, History
from rich.progress import Progress

class Metric(ABC):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player):
        if isinstance(hands, History):
            self.history = hands
        else:
            self.history = History(hands = [hand for hand in hands if hand.hero == hero], hero=hero)
            self.history.get_main_stats()
        self.hero = hero
        self._value: t.Union[int, float, None] = None

    @abstractmethod
    def get(self) -> t.Union[int, float]:
        pass

    @abstractmethod
    @property
    def value(self) -> t.Union[int, float]:
        if self._value is None:
            self._value = self.get()
        return self._value

    @value.setter
    def value(self) -> None:
        raise AttributeError("Can't set value directly, use get() method.")

class StatsMetric(Metric):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player, stat: str) -> None:
        super().__init__(hands, hero)
        if stat not in self.history.get_main_stats(hero=self.hero).columns:
            raise ValueError(f"Stat {stat} not found in main stats DataFrame.")
        self.stat = stat

    def get(self) -> float:
        df = self.history.get_main_stats(hero=self.hero)
        return df[self.stat].mean()

class VPIP(StatsMetric):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player) -> None:
        super().__init__(hands, hero, stat="vpip")

class WTSD(Metric):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player) -> None:
        super().__init__(hands, hero, stat="wtsd")

class WSD(Metric):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player) -> None:
        super().__init__(hands, hero, stat="w$sd")

class PFR(StatsMetric):
    def __init__(self, hands: t.Union[History, t.Iterable[Hand]], hero: Player) -> None:
        super().__init__(hands, hero, stat="pfr")
