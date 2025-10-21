"""
Core poker game models and logic.

This module implements the core classes needed to model poker hands, players, rounds,
bets and game history. It provides functionality for tracking game state, player actions,
and computing results.

Classes:
    Bet: Represents a betting action by a player
    Round: Models a single round/street of poker 
    Player: Represents a player in the game
    Hand: Models a complete poker hand from start to finish
    History: Maintains history of multiple poker hands
"""

import datetime
import random
import typing as t
import phevaluator
import copy

import polars as pl
import uuid
import os


from pypokerstar.src.types import Card, Deck, Range

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

class Player:
    """
    Represents a player in the poker game.
    
    Attributes:
        name (str): Player's name/identifier
        pot (float): Player's stack/chip amount
        seat (int): Player's seat position at table
        cards (list[Card]): Player's hole cards
    """
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
    
    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.__str__()

class Bet:
    """
    Represents a betting action made by a player.
    
    Attributes:
        player (Player): The player making the bet
        amount (float): The bet amount
        type (str): Type of bet (bets/calls/raises/folds/checks/blinds/uncalled/collected)
    """
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
    """
    Models a single round/street of poker (preflop, flop, turn, river).
    
    Attributes:
        name (str): Name of the round (hole cards/flop/turn/river/show down)
        players (list[Player]): Players active in the round
        bets (list[Bet]): Betting actions made during the round
        pot (float): Total amount in the pot for this round
        board (list[Card]): Community cards shown in this round
        winner (list[Player]): Players who won this round
        game_type (str): Game type - cash or tournament
    """
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

    def active_players(self) -> t.Iterable[Player]:
        plys = set()
        for bet in self.bets:
            plys.add(bet.player)
        return list(plys)

    def set_winner(self, player: "Player") -> None:
        self.winner.append(player)

    def get_hero_equity(self, hero: Player, iterations: int) -> float:
        deck = Deck()
        for card in hero.cards + list(self.board):
            deck.remove_cards(card)
        wins = 0
        for _ in range(iterations):
            deck.shuffle()
            sim_deck = copy.deepcopy(deck)
            sim_board = list(self.board)
            while len(sim_board) < 5:
                sim_board.append(sim_deck.draw())
            hero_hand = hero.cards + sim_board
            hero_score = phevaluator.evaluate_cards(
                *[card.standard_string() for card in hero_hand]
            )
            is_winner = True
            for player in self.active_players():
                if player == hero:
                    continue
                opp_cards = [sim_deck.draw() for _ in range(2)]
                opp_hand = opp_cards + sim_board
                opp_score = phevaluator.evaluate_cards(
                    *[card.standard_string() for card in opp_hand]
                )
                if opp_score < hero_score:
                    is_winner = False
                    break
            if is_winner:
                wins += 1
        return wins / iterations

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.name, tuple(self.bets), self.pot, tuple(self.board)))





class Hand:
    # ...existing code...
    def __init__(
        self,
        id: str,
        raw_text: str,
        players: t.Iterable[Player],
        rounds: t.Iterable[Round],
        hero: t.Optional[Player] = None,
        date: t.Optional[datetime.datetime] = None,
        pot: t.Optional[float] = 0.0,
        rake: t.Optional[float] = 0.0,
    ) -> None:
        self.id = id
        self.raw_text: str = raw_text
        self.players = list(players)

        self.players_map: dict[str, Player] = {p.name: p for p in self.players}
        self.game_type: t.Literal["cash", "tournament"] = "cash"
        self.pot = pot
        self.rake = rake
        self.date: t.Optional[datetime.datetime] = date
        self.hero = hero

        self.board: list[Card] = []
        self._board_set: set[Card] = set()
        self.winner: list[Player] = []
        self.rounds: list[Round] = list(rounds)
        self.rounds = sorted(self.rounds, key=lambda x: ROUNDS[x.name.lower()])

        self.rounds_map: dict[str, Round] = {r.name.lower(): r for r in self.rounds}
        self.main_rounds = ["hole cards", "flop", "turn", "river", "show down"]
        self._result: dict[Player, float] = {}

        self._player_bets_cache: dict[str, list[Bet]] = {}
        self.refresh()
    def refresh(self) -> None:
        # ensure hero references canonical Player object if present
        if self.hero:
            canonical = self.players_map.get(self.hero.name)
            if canonical:
                self.hero = canonical

        sd = self.get_round("show down")
        if sd:
            # for each player object in show down, if it contains card info, map to canonical
            for p in sd.players:
                if getattr(p, "cards", None) and len(p.cards) == 2:
                    canonical = self.players_map.get(p.name)
                    if canonical and canonical is not p:
                        # copy cards into canonical object rather than remove/append in list
                        canonical.cards = p.cards

        # update board and winner lists using sets for fast membership
        for round in self.rounds:
            if round.game_type == "tournament":
                self.game_type = "tournament"
            for card in round.board:
                if card not in self._board_set:
                    self._board_set.add(card)
                    self.board.append(card)
            if round.name.lower() == "table":
                self.table = round.bets
            if round.winner:
                for p in round.winner:
                    if p.name not in {w.name for w in self.winner}:
                        # prefer canonical player object
                        canonical = self.players_map.get(p.name, p)
                        self.winner.append(canonical)

    def get_round(self, name: str) -> t.Optional[Round]:
        return self.rounds_map.get(name.lower())

    def get_player(self, name: str) -> t.Optional[Player]:
        return self.players_map.get(name)

    def __get_player_bets(self, player: Player) -> t.Iterable[Bet]:
        # cache per player by name to avoid re-iterating rounds repeatedly
        if player.name in self._player_bets_cache:
            return self._player_bets_cache[player.name]
        player_bets: list[Bet] = []
        for round in self.rounds:
            # iterate bets once
            for bet in round.bets:
                if bet.player.name == player.name:
                    player_bets.append(bet)
        self._player_bets_cache[player.name] = player_bets
        return player_bets

    @property
    def result(self) -> dict[Player, float]:
        if not self._result:
            self.refresh()
            # use names as keys internally then map back to canonical Player objects
            tmp: dict[str, float] = {}
            for player in self.players:
                total_bet = sum(
                    b.amount for b in self.__get_player_bets(player) if b.type != "collected"
                )
                tmp[player.name] = -total_bet

            summary = self.get_round("summary")
            if summary:
                for bet in summary.bets:
                    if bet.type == "collected":
                        name = bet.player.name
                        tmp[name] = tmp.get(name, 0.0) + bet.amount

            # convert to dict[Player, float] using players_map
            for name, val in tmp.items():
                player_obj = self.players_map.get(name)
                if player_obj:
                    self._result[player_obj] = val
        return self._result

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
    
    def __get_player_bets(self, player: Player) -> t.Iterable[Bet]:
        player_bets = []
        for round in self.rounds:
            for bet in round.bets:
                if bet.player == player:
                    player_bets.append(bet)
        return player_bets
    

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
    """
    Maintains history of multiple poker hands.
    
    Provides analysis and statistics across multiple hands.
    
    Attributes:
        hands (list[Hand]): Collection of poker hands
        hero (Player): Player perspective for analysis
        
    Methods:
        get_money_history: Returns DataFrame with financial results over time
    """
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
            # Compute hero's invested total by street without double counting raises
            total_bet = 0.0
            for rnd in hand.rounds:
                per_round = 0.0
                for bet in rnd.bets:
                    if bet.player != self.hero:
                        continue
                    if bet.type in ("small blind", "big blind", "bets", "calls"):
                        per_round += bet.amount
                    elif bet.type == "raises":
                        # Treat raises as committing to the final amount of the street
                        per_round = max(per_round, bet.amount)
                    elif bet.type == "uncalled":
                        per_round += bet.amount  # negative when returned
                total_bet += per_round

            # Prefer explicit collected amounts (handles splits/side pots)
            won = sum(
                bet.amount
                for rnd in hand.rounds
                for bet in rnd.bets
                if bet.player == self.hero and bet.type == "collected"
            )
            # Fallback: equal split among winners if no explicit collected entry
            if won == 0.0 and hand.winner and self.hero in hand.winner:
                won = (hand.pot - hand.rake) / max(len(hand.winner), 1)
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
    
    # def get_ranges(self) -> Range:
    #     for hand in self.hands:
    #         preflop = hand.get_round("hole cards")
    #         for bet in preflop.bets:


    def __str__(self) -> str:
        return f"History with {len(self.hands)} hands."
