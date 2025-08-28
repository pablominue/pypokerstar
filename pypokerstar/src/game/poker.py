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

ROUNDS = {
    "table": 0,
    "hole cards": 1,
    "flop": 2,
    "turn": 3,
    "river": 4,
    "show down": 5,
    "summary": 6
}   

class Bet:
    def __init__(self, player: 'Player', bet_type: t.Literal["calls", "raises", "folds", "checks", "small blind", "big blind"],  amount: float = 0.0) -> None:
        self.player = player
        self.amount = amount
        self.type  = bet_type

class Round:

    def __init__(self, name: str, bets: t.Iterable[Bet] = None, players: list['Player'] = [], pot: float = 0.0) -> None:
        if name.lower() not in ["hole cards", "flop", "turn", "river", "show down",  "table", "summary"]:
            raise ValueError("Round name must be one of: 'hole cards', 'flop', 'turn', 'river', 'show down',  \n Given: " + name)
        self.name: str = name
        self.players = players
        self.bets: t.Iterable[Bet] = []
        self.pot: float = 0.0
        self.board: t.Iterable[Card] = []

    def add_player(self, player: 'Player') -> None:
        self.players.append(player)

    def add_bet(self, bet: Bet) -> None:
        self.bets.append(bet)
        self.pot += bet.amount
        
    def update_board(self, *cards: t.Iterable[Card]) -> None:
        for card in cards:
            if card not in self.board:
                self.board.append(card)

class Player:
    def __init__(self, name: str = "", pot: float = 0, seat: int = 1, cards: t.Iterable[Card]=None) -> None:
        self.name: str = name
        self.seat: int = seat
        self.pot: float = pot
        self.cards: t.Iterable[Card] = cards

    def print_cards(self) -> None:
        for card in self.cards:
            print(card)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return self.name == other.name


class Hand:
    def __init__(self, players: t.Iterable[Player], rounds: t.Iterable[Round]) -> None:
        self.players = players
        self.pot = 0
        self.board: t.Iterable[Card] = []
        self.winner: t.Optional[Player] = None
        self.rounds: t.Iterable[Round] = rounds
        self.rounds = sorted(self.rounds, key=lambda x: ROUNDS[x.name.lower()])
        self.refresh()

    def refresh(self) -> None:
        for round in self.rounds:
            self.pot += round.pot
            round.pot = self.pot - round.pot
            for card in round.board:
                if card not in self.board:
                    self.board.append(card)

            if round.name.lower() == "table":
                self.table = round.bets

    def get_round(self, name: str) -> t.Optional[Round]:
        for round in self.rounds:
            if round.name.lower() == name.lower():
                return round
        return None
    

    def get_player(self, name: str) -> t.Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return None


    def to_polars(self) -> dict[str, t.Any]:
        self.refresh()
        return {
            "players": [player.__dict__ for player in self.players],
            "pot": self.pot,
            "table": [str(card) for card in self.table],
            "winner": self.winner.__dict__ if self.winner else None,
            "rounds": [
                {
                    "name": round.name,
                    "bets": [bet.__dict__ for bet in round.bets],
                    "pot": round.pot,
                    "ending_pot": round.pot + sum(bet.amount for bet in round.bets)
                } for round in self.rounds
            ]
        }
    
    def __str__(self) -> str:
        return f"Hand with {len(self.players)} players and {len(self.rounds)} rounds. Total pot: {self.pot}. Final board: {' '.join([str(card) for card in self.board])}"