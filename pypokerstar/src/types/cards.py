"""
Poker card and deck implementations.

This module provides classes for representing playing cards, card pairs and a full deck
of cards. Includes utilities for card comparisons and standard poker hand notation.

Classes:
    Card: Single playing card with suit and number
    Pair: Two-card poker hand combination
    Deck: Standard 52-card poker deck
"""


import itertools
import random
import typing as t

from pydantic import BaseModel

SPADES = "♠️"
CLUBS = "♣️"
HEARTS = "♥️"
DIAMONDS = "♦️"

SUITS = {"s": SPADES, "c": CLUBS, "h": HEARTS, "d": DIAMONDS}
REVERSE_SUITS = {v: k for k, v in SUITS.items()}

class Card:
    """
    Represents a single playing card.
    
    Attributes:
        number (int): Card number/rank (1-13, where 1=Ace)
        suit (str): Card suit symbol (♠️, ♣️, ♥️, ♦️)
        
    Methods:
        from_string: Creates card from standard notation (e.g. "As" for Ace of spades)
        pocket_pair: Checks if forms pair with another card
        suited: Checks if same suit as another card
        connector: Checks if sequential with another card
        stringify: Returns unicode string representation
        standard_string: Returns standard notation string
    """
    def __init__(self, number, suit) -> None:
        if suit not in SUITS.values():
            available = ", ".join(SUITS)
            raise TypeError(f"Suit must be in {available}. Given: {suit}")
        self.number = number
        self.suit = suit

    def _parse_number(string: str) -> int:
        if string == "A":
            return 1
        elif string == "T":
            return 10
        elif string == "J":
            return 11
        elif string == "Q":
            return 12
        elif string == "K":
            return 13
        else:
            try:
                number = int(string)
                if number < 2 or number > 10:
                    raise ValueError("Card number must be between 2 and 9")
                return number
            except ValueError:
                raise ValueError("Card number must be between 2 and 9 or A, J, Q, K, T")

    @staticmethod
    def from_string(string: str) -> "Card":
        string = string.strip()
        string = string.replace("[", "").replace("]", "")
        if len(string) != 2:
            raise ValueError("Card string must be of length 2. Given: " + string)
        number_str = string[0]
        suit_str = SUITS.get(string[1])
        return Card(number=Card._parse_number(number_str), suit=suit_str)

    def pocket_pair(self, other: "Card") -> bool:
        return self.number == other.number

    def suited(self, other: "Card") -> bool:
        return self.suit == other.suit

    def connector(self, other: "Card") -> bool:
        return bool(abs(self.number - other.number) == 1)

    def suited_connector(self, other: "Card") -> bool:
        return self.suited(other) and self.connector(other)

    def stringify(self) -> str:
        number = ""
        if self.number == 1:
            number = "A"
        elif self.number == 10:
            number = "T"
        elif self.number == 11:
            number = "J"
        elif self.number == 12:
            number = "Q"
        elif self.number == 13:
            number = "K"
        else:
            number = str(self.number)

        return number + self.suit
    
    def standard_string(self) -> str:
        number = ""
        if self.number == 1:
            number = "A"
        elif self.number == 10:
            number = "T"
        elif self.number == 11:
            number = "J"
        elif self.number == 12:
            number = "Q"
        elif self.number == 13:
            number = "K"
        else:
            number = str(self.number)

        return number + REVERSE_SUITS[self.suit]

    def __str__(self) -> str:
        return self.stringify()

    def __repr__(self):
        return self.stringify()

    def __eq__(self, other: "Card") -> bool:
        return self.number == other.number and self.suit == other.suit


class Pair:
    """
    Represents a two-card poker hand combination.
    
    Attributes:
        cards (list[Card]): The two cards in sorted order
        card1 (Card): First/lower card
        card2 (Card): Second/higher card
        suited (bool): Whether cards are same suit
        pocket_pair (bool): Whether cards are same number
        hand (str): Standard hand notation (e.g. "AKs" for suited Ace-King)
    """
    def __init__(self, card1: Card, card2: Card) -> None:
        self.cards = sorted([card1, card2], key=lambda x: x.number)
        self.card1 = self.cards[0]
        self.card2 = self.cards[1]
        self.suited: bool = False
        self.pocket_pair = False
        self.hand = ""
        if card1.number == card2.number:
            self.hand = str(card1.number) + str(card2.number)
            self.pocket_pair = True

        if self.card1.suited(self.card2):
            self.hand = str(self.card1)[0] + str(self.card2)[0] + "s"
            self.suited = True

        else:
            self.hand = str(self.card1)[0] + str(self.card2)[0] + "o"

    def __eq__(self, other: "Pair") -> bool:
        return self.hand == other.hand

    def __hash__(self):
        return (
            self.cards[0].number * 100
            + self.cards[1].number * 10
            + (1 if self.cards[0].suited(self.cards[1]) else 0)
        )

    def __str__(self) -> str:
        return str(self.hand)


class Deck:
    """
    Implementation of standard 52-card poker deck.
    
    Attributes:
        cards (list[Card]): Remaining cards in the deck
        
    Methods:
        draw: Removes and returns top card(s) from deck
    """
    def __init__(self) -> None:
        self.cards = [
            [Card(number=n, suit=suit) for n in range(1, 13, 1)] for suit in SUITS.values()
        ]
        self.cards = list(itertools.chain.from_iterable(self.cards))
        random.shuffle(self.cards)

    def draw(self, cards: int = 1) -> Card:
        return self.cards.pop(0)
    
    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def remove_cards(self, *cards: t.Iterable[Card]) -> None:
        self.cards = [c for c in self.cards if c not in cards]


class Range:
    pass