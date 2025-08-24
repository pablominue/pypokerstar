from src.parsers.parser import Parser
import re
import typing as t
from src.game.poker import Player, Hand, Round, Hand, Card

class PokerStarsParser(Parser):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.site = "PokerStars"
        if self.file_extension.lower() != ".txt":
            raise ValueError("PokerStars parser only supports .txt files")
        
    @staticmethod
    def _get_hands(file_content: str) -> t.List[str]:
        return [
            f.strip() for f in file_content.split("\n\n")
        ]
    
    def _parse_hand(self, hand: str) -> dict[t.Any, t.Any]:
        regex_section = re.compile(r"\*\*\* (.*?) \*\*\*")
        sections = list(regex_section.finditer(hand))
        results = {}
        results["table"] = hand[0:sections[0].start()].strip()
        for i, match in enumerate(sections):
            start = match.end()
            end = sections[i+1].start() if i+1 < len(sections) else len(hand)
            section_name = match.group(1).strip().upper().replace(" ", "_")
            results[section_name] = hand[start:end].strip()

        return results
    
    def _parse_round(self, round_str: str, section: str) -> None:
        round = Round(name=section)
        for row in round_str.split("\n"):
            if re.match(pattern=r"^Dealt to \S+ \[.*\]$", string=row, flags = re.DOTALL) is not None:
                pattern = re.compile(r"Dealt to (\S+) \[(.*)\]")
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    cards_str = match.group(2)
                    cards = [Card.from_string(card_str) for card_str in cards_str.split(" ")]
                    # Find the player and assign the cards
                    # for player in players:
                    #     if player.name == player_name:
                    #         player.cards = cards
            elif re.match(pattern=r"^\S+: (bets|calls|raises|folds|checks)( .*)?$", string=row, flags = re.DOTALL) is not None:
                pattern = re.compile(r"^(\S+): (bets|calls|raises|folds|checks)( .*)?$")
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    action = match.group(2)
                    amount_str = match.group(3).strip() if match.group(3) else ""
                    amount = 0.0
                    if amount_str:
                        amount_pattern = re.compile(r"€([\d\.]+)")
                        amount_match = amount_pattern.search(amount_str)
                        if amount_match:
                            amount = float(amount_match.group(1))
                    # Find the player
                    # for player in players:
                    #     if player.name == player_name:
                    #         bet = Bet(player=player, bet_type=action, amount=amount)
                    #         round.bets.append(bet)

    def _get_players(self, table: str) -> t.Generator[Player, None, None]:
        for row in table.split("\n"):
            if re.match(pattern=r"Seat \d: \S+ \(.*\)", string=row, flags = re.DOTALL) is not None:
                pattern = re.compile(r"Seat\s+(\d+):\s+([^(]+)\(€([\d\.]+)")
                match = pattern.search(row)
                if match:
                    seat = int(match.group(1))
                    name = match.group(2).strip()
                    currency = float(match.group(3))
                    player = Player(name=name, pot=currency, seat=seat)
                    yield player

        
    def parse(self) -> None:
        with open(self.file_path, 'r') as file:
            file_content = file.read()
        
        hands = self._get_hands(file_content)
        for hand in hands:
            sections = self._parse_hand(file_content)

        players = list(self._get_players(sections["table"]))
        for player in players:
            print(f"Player {player.seat}: {player.name} with pot {player.pot}")