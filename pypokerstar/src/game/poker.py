import datetime
import random
import typing as t

import polars as pl

from pypokerstar.src.types import Card, Deck

SEATS = {
    1: "button",
    2: "small blind",
    3: "big blind",
    4: "under the gun",
    5: "middle position",
    6: "cutoff",
}

ROUNDS = {
    "table": 0,
    "hole cards": 1,
    "flop": 2,
    "turn": 3,
    "river": 4,
    "show down": 5,
    "summary": 6,
}


class Bet:
    def __init__(
        self,
        player: "Player",
        bet_type: t.Literal[
            "bets",
            "calls",
            "raises",
            "folds",
            "checks",
            "small blind",
            "big blind",
            "uncalled",
            "collected",
        ],
        amount: float = 0.0,
    ) -> None:
        self.player = player
        self.amount = amount
        self.type = bet_type

    def __str__(self) -> str:
        return f"{self.player} {self.type} {self.amount.__str__()}"

    def __repr__(self):
        return self.__str__()


class Round:

    def __init__(
        self,
        name: str,
        bets: t.Iterable[Bet] = None,
        players: list["Player"] = [],
        pot: float = 0.0,
    ) -> None:
        if name.lower() not in [
            "hole cards",
            "flop",
            "turn",
            "river",
            "show down",
            "table",
            "summary",
        ]:
            raise ValueError(
                "Round name must be one of: 'hole cards', 'flop', 'turn', 'river', 'show down',  \n Given: "
                + name
            )
        self.name: str = name
        self.players = players
        self.bets: t.Iterable[Bet] = []
        self.pot: float = 0.0
        self.board: t.Iterable[Card] = []
        self.winner: t.Iterable[Player] = []
        self.game_type: t.Literal["cash", "tournament"] = "cash"

    def add_player(self, player: "Player") -> None:
        self.players.append(player)

    def add_bet(self, bet: Bet) -> None:
        self.bets.append(bet)
        self.pot += bet.amount

    def update_board(self, *cards: t.Iterable[Card]) -> None:
        for card in cards:
            if card not in self.board:
                self.board.append(card)

    def set_winner(self, player: "Player") -> None:
        self.winner.append(player)

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.name, tuple(self.bets), self.pot, tuple(self.board)))


class Player:
    def __init__(
        self,
        name: str = "",
        pot: float = 0,
        seat: int = 1,
        cards: t.Iterable[Card] = None,
    ) -> None:
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
    def __init__(
        self,
        players: t.Iterable[Player],
        rounds: t.Iterable[Round],
        hero: t.Optional[Player] = None,
        date: t.Optional[datetime.datetime] = None,
        pot: t.Optional[float] = 0.0,
        rake: t.Optional[float] = 0.0,
    ) -> None:
        self.players = players
        self.game_type: t.Literal["cash", "tournament"] = "cash"
        self.pot = pot
        self.rake = rake
        self.date: t.Optional[datetime.datetime] = date
        self.hero = hero
        self.board: t.Iterable[Card] = []
        self.winner: t.Iterable[Player] = []
        self.rounds: t.Iterable[Round] = rounds
        self.rounds = sorted(self.rounds, key=lambda x: ROUNDS[x.name.lower()])
        self.refresh()

    def refresh(self) -> None:
        for round in self.rounds:
            if round.game_type == "tournament":
                self.game_type = "tournament"
            for card in round.board:
                if card not in self.board:
                    self.board.append(card)
            if round.name.lower() == "table":
                self.table = round.bets
            if len(round.winner) > 0:
                for p in round.winner:
                    if p not in self.winner:
                        self.winner.append(p)

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
                    "ending_pot": round.pot + sum(bet.amount for bet in round.bets),
                }
                for round in self.rounds
            ],
        }

    def __str__(self) -> str:
        players = {", ".join([str(p) for p in self.players])}
        return f"Hand played by {players} with {len(self.rounds)} rounds. Total pot: {self.pot.__str__()} won by {self.winner.__str__()} . Final board: {' '.join([str(card) for card in self.board])}"


class History:
    def __init__(
        self, hands: t.Iterable[Hand] = [], hero: t.Optional[Player] = None
    ) -> None:
        self.hands: t.Iterable[Hand] = hands
        self.hero = hero
        if self.hero:
            self.hands = [
                hand
                for hand in self.hands
                if hand.hero == hero and hand.game_type == "cash"
            ]

    def add_hand(self, hand: Hand) -> None:
        self.hands.append(hand)

    def get_money_history(self) -> pl.DataFrame:
        if not self.hero:
            raise ValueError("Hero is not defined")
        data = []
        for hand in self.hands:
            hero_bets = hand.get_hero_bets()
            # Sum of actual invested amounts by hero within the hand.
            # Include blinds, bets, calls, raises, and subtract any returned uncalled amounts.
            total_bet = sum(
                bet.amount
                for bet in hero_bets
                if bet.type
                in [
                    "bets",
                    "calls",
                    "raises",
                    "small blind",
                    "big blind",
                    "uncalled",  # negative amounts reduce invested total
                ]
            )
            # Amounts explicitly collected by hero from the pot within the hand.
            won = sum(
                bet.amount
                for rnd in hand.rounds
                for bet in rnd.bets
                if bet.player == self.hero and bet.type == "collected"
            )
            data.append(
                {
                    "date": hand.date,
                    "total_bet": total_bet,
                    "won": won,
                    "net": won - total_bet,
                    "pot": hand.pot,
                    "rake": hand.rake,
                }
            )
        df = pl.DataFrame(data)
        df = df.sort("date")
        df = df.with_columns(
            [
                pl.col("net").cum_sum().alias("cumulative_net"),
                pl.col("total_bet").cum_sum().alias("cumulative_total_bet"),
                pl.col("won").cum_sum().alias("cumulative_won"),
                pl.col("pot").cum_sum().alias("cumulative_pot"),
                pl.col("rake").cum_sum().alias("cumulative_rake"),
            ]
        )
        return df

    def __str__(self) -> str:
        return f"History with {len(self.hands)} hands."
