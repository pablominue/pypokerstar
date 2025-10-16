from pypokerstar.src.types import Card, Deck
import typing as t
import random
import polars as pl
import uuid
import os


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

    def __str__(self) -> str:
        return f"{self.player} {self.type} {self.amount.__str__()}"
    
    def __repr__(self):
        return self.__str__()

class Round:

    def __init__(self, name: str, bets: t.Iterable[Bet] = None, players: list['Player'] = [], pot: float = 0.0) -> None:
        if name.lower() not in ["hole cards", "flop", "turn", "river", "show down",  "table", "summary"]:
            raise ValueError("Round name must be one of: 'hole cards', 'flop', 'turn', 'river', 'show down',  \n Given: " + name)
        self.name: str = name
        self.players = players
        self.bets: t.Iterable[Bet] = []
        self.pot: float = 0.0
        self.board: t.Iterable[Card] = []
        self.winner: t.Optional[Player] = None

    def add_player(self, player: 'Player') -> None:
        self.players.append(player)

    def add_bet(self, bet: Bet) -> None:
        self.bets.append(bet)
        self.pot += bet.amount
        
    def update_board(self, *cards: t.Iterable[Card]) -> None:
        for card in cards:
            if card not in self.board:
                self.board.append(card)

    def set_winner(self, player: 'Player') -> None:
        self.winner = player

    def __str__(self) -> str:
        return f"Round {self.name} with {len(self.bets)} bets and pot {self.pot.__str__()} . Board: {' '.join([str(card) for card in self.board])}"
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash((self.name, tuple(self.bets), self.pot, tuple(self.board)))

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

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self):
        return self.__str__()

class Hand:
    def __init__(self, players: t.Iterable[Player], rounds: t.Iterable[Round], hero: t.Optional[Player] = None) -> None:
        self.players = players
        self.pot = 0
        self.hero = hero
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
    
    def set_winner(self, player: 'Player') -> None:
        self.winner = player

    def get_player(self, name: str) -> t.Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return None

    def get_hero_bets(self) -> t.Iterable[Bet]:
        if not self.hero:
            return []
        hero_bets = []
        for round in self.rounds:
            for bet in round.bets:
                if bet.player == self.hero:
                    hero_bets.append(bet)
        return hero_bets
    
    def get_hero_rounds(self) -> t.Iterable[Round]:
        if not self.hero:
            return []
        hero_rounds = []
        for round in self.rounds:
            for bet in round.bets:
                if bet.player == self.hero:
                    hero_rounds.append(round)
                    break
        return hero_rounds
    
    def get_hero_finished_rounds(self) -> t.Iterable[Round]:
        if not self.hero:
            return []
        hero_rounds = []
        for round in self.rounds:
            for bet in round.bets:
                if bet.player == self.hero and bet.type == "folds":
                    break
                else:
                    continue
            hero_rounds.append(round)
        return hero_rounds

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
        players = {", ".join([str(p) for p in self.players])}
        return f"Hand played by {players} with {len(self.rounds)} rounds. Total pot: {self.pot.__str__()} won by {self.winner.__str__()} . Final board: {' '.join([str(card) for card in self.board])}"
    

def export_hands(hands: t.Iterable[Hand], directory: str) -> None:
    data = pl.DataFrame()
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i, hand in enumerate(hands):
        for round in hand.rounds:
            round_dict = {
            "players": [player.__dict__ for player in round.players],
            "pot": round.pot,
            "table": [str(card) for card in hand.table],
            "winner": round.winner.__dict__ if round.winner else None,
            "round": round.name,
            "bets": [bet.__dict__ for bet in round.bets],
            "pot": round.pot,
            "ending_pot": round.pot + sum(bet.amount for bet in round.bets)
            }
            data = pl.concat([data, pl.DataFrame(round_dict, strict=False)], how="vertical")
            print(data)
    print(data)
    data.write_json(os.path.join(directory, "hands.json"))

def read_hands(directory: str) -> t.List[Hand]:
    hands = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            data = pl.read_json(os.path.join(directory, filename))
            for row in data.iter_rows(named=True):
                players = [Player(**player) for player in row["players"]]
                rounds = []
                for round_data in row["rounds"]:
                    round_players = players
                    round_bets = []
                    for bet_data in round_data["bets"]:
                        bet_player = next((p for p in players if p.name == bet_data["player"]["name"]), None)
                        if bet_player:
                            round_bets.append(Bet(player=bet_player, bet_type=bet_data["type"], amount=bet_data["amount"]))
                    round = Round(name=round_data["name"], bets=round_bets, players=round_players, pot=round_data["pot"])
                    rounds.append(round)
                winner = next((p for p in players if p.name == row["winner"]["name"]), None) if row["winner"] else None
                hand = Hand(players=players, rounds=rounds, hero=None)
                hand.pot = row["pot"]
                hand.winner = winner
                hands.append(hand)
    return hands