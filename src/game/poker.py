from src.types import Card, Deck
import typing as t
import random
import polars as pl

SEATS = {
    1: "button",
    2: "small blind",
    3: "big blind",
    4: "under the gun",
    5: "middle position",
    6: "cutoff"
}

class Bet:
    def __init__(self, player: 'Player', bet_type: t.Literal["call", "raise", "fold", "check"],  amount: float = 0.0) -> None:
        self.player = player
        self.amount = amount
        self.type  = bet_type

class Round:

    def __init__(self, name: str, bets: t.Iterable[Bet], players: list['Player'] = [], pot: float = 0.0) -> None:
        self.name: str = name
        self.players = players
        self.bets: t.Iterable[Bet] = []
        self.pot: float = 0.0

    def add_player(self, player: 'Player') -> None:
        self.players.append(player)
        

class Player:
    def __init__(self, name: str = "", pot: float = 0, seat: int = 1, cards: t.Iterable[Card]=None) -> None:
        self.name: str = name
        self.seat: int = seat
        self.pot: float = pot
        self.cards: t.Iterable[Card] = cards

    def print_cards(self) -> None:
        for card in self.cards:
            print(card)


class Hand:
    def __init__(self, players: t.Iterable[Player], rounds: t.Iterable[Round]) -> None:
        self.players = players
        self.pot = 0
        self.table = []
        self.winner: t.Optional[Player] = None
        self.rounds: t.Iterable[Round] = rounds

    def to_polars(self) -> dict[str, t.Any]:
        return {
            "players": [player.__dict__ for player in self.players],
            "pot": self.pot,
            "table": [str(card) for card in self.table],
            "winner": self.winner.__dict__ if self.winner else None,
            "rounds": [
                {
                    "name": round.name,
                    "bets": [bet.__dict__ for bet in round.bets],
                    "pot": round.pot
                } for round in self.rounds
            ]
        }