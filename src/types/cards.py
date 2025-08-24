from pydantic import BaseModel
import typing as t
import random
import itertools

SPADES = "♠️"
CLUBS = "♣️"
HEARTS = "♥️"
DIAMONDS = "♦️"

SUITS = [
    SPADES, CLUBS, HEARTS, DIAMONDS
]

class Card:

    def __init__(self, number, suit) -> None:
        if suit not in SUITS:
            available = ", ".join(SUITS)
            raise TypeError(f"Suit must be in {available}")
        self.number = number
        self.suit = suit

    def from_string(string: str) -> 'Card':
        pass


    def pocket_pair(self, other: 'Card') -> bool:
        return self.number == other.number
    
    def suited(self, other: 'Card') -> bool:
        return self.suit == other.suit
    
    def connector(self, other: 'Card') -> bool:
        return bool(abs(self.number - other.number)==1)

    def suited_connector(self, other: 'Card') -> bool:
        return self.suited(other) and self.connector(other)
    
    def stringify(self) -> str:
        number = ""
        if self.number == 1:
            number = "A"
        elif self.number == 11:
            number = "J"
        elif self.number == 12:
            number = "Q"
        elif self.number == 13:
            number = "K"
        else:
            number = str(self.number)

        return number + self.suit
    
    def __str__(self) -> str:
        return self.stringify()


class Deck:
    def __init__(self) -> None:
        self.cards = [[Card(number=n, suit=suit) for n in range(1, 13, 1)] for suit in SUITS]
        self.cards = list(itertools.chain.from_iterable(self.cards))
        random.shuffle(self.cards)


    def draw(self, cards: int = 1) -> Card:
        return self.cards.pop(0)
    
