from pydantic import BaseModel
import typing as t
import random
import itertools

SPADES = "♠️"
CLUBS = "♣️"
HEARTS = "♥️"
DIAMONDS = "♦️"

SUITS = {"s": SPADES, "c": CLUBS, "h": HEARTS, "d": DIAMONDS}


class Card:
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

    def __str__(self) -> str:
        return self.stringify()

    def __repr__(self):
        return self.stringify()

    def __eq__(self, other: "Card") -> bool:
        return self.number == other.number and self.suit == other.suit


class Pair:
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
    def __init__(self) -> None:
        self.cards = [
            [Card(number=n, suit=suit) for n in range(1, 13, 1)] for suit in SUITS
        ]
        self.cards = list(itertools.chain.from_iterable(self.cards))
        random.shuffle(self.cards)

    def draw(self, cards: int = 1) -> Card:
        return self.cards.pop(0)
