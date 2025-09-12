from pypokerstar.src.parsers.parser import Parser
from pypokerstar.src.parsers.pokerparser import PokerParser
import re
import typing as t
from pypokerstar.src.game.poker import Player, Hand, Round, Card, Bet
import os
from rich.progress import Progress


class PokerStarsParser(Parser):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.site = "PokerStars"
        self.failed = 0
        if self.file_extension.lower() != ".txt":
            raise ValueError("PokerStars parser only supports .txt files")

    @staticmethod
    def _get_hands(file_content: str) -> t.List[str]:
        return [f.strip() for f in file_content.split("\n\n")]

    def _parse_hand(self, hand: str) -> dict[t.Any, t.Any]:
        regex_section = re.compile(r"\*\*\* (.*?) \*\*\*")
        if hand == "":
            return {}
        sections = list(regex_section.finditer(hand))
        results = {}
        results["table"] = hand[0 : sections[0].start()].strip()
        for i, match in enumerate(sections):
            start = match.end()
            end = sections[i + 1].start() if i + 1 < len(sections) else len(hand)
            section_name = match.group(1).strip().upper()
            results[section_name] = hand[start:end].strip()

        return results

    def _parse_round(
        self, round_str: str, section: str, players: t.Iterable[Player]
    ) -> Round:
        round = Round(name=section)
        for row in round_str.split("\n"):
            if (
                re.match(pattern=r"^Dealt to \S+ \[.*\]$", string=row, flags=re.DOTALL)
                is not None
            ):
                pattern = re.compile(r"Dealt to (\S+) \[(.*)\]")
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    cards_str = match.group(2)
                    cards = [
                        Card.from_string(card_str) for card_str in cards_str.split(" ")
                    ]
                    for player in players:
                        if player.name == player_name:
                            player.cards = cards
            elif re.match(pattern=r"\[.*\]", string=row, flags=re.DOTALL) is not None:
                pattern = re.compile(r"\[(.*)\] \[(\S{2})\]?$")
                match = pattern.search(row)
                if match:
                    previous_cards = match.group(1)
                    round_cards = (
                        Card.from_string(match.group(2)) if match.group(2) else None
                    )
                    previous_cards = [
                        Card.from_string(previous_cards)
                        for previous_cards in previous_cards.split(" ")
                    ]
                    cards = (
                        previous_cards + [round_cards]
                        if round_cards
                        else previous_cards
                    )
                    round.update_board(*cards)
            elif (
                re.match(
                    pattern=r"^\S+: (bets|calls|raises|folds|checks)( .*)?$",
                    string=row,
                    flags=re.DOTALL,
                )
                is not None
            ):
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
                    for player in players:
                        if player.name == player_name:
                            bet = Bet(player=player, bet_type=action, amount=amount)
                            round.add_bet(bet)
            elif (
                re.match(pattern=r"\S+ posts \S+ blind", string=row, flags=re.DOTALL)
                is not None
            ):
                pattern = re.compile(r"(\S+) posts (.*) blind €(.*)?$")
                match = pattern.search(row)
                if match:
                    player = str(match.group(1))
                    blind = str(match.group(2).strip())
                    amount = float(match.group(3))
                    round.add_bet(
                        Bet(
                            player=Player(name=player),
                            bet_type=blind + " blind",
                            amount=amount,
                        )
                    )
            elif (
                re.match(
                    pattern=r"(\S+) \(.*\) collected \([$,€](\d{1,2}\.\d{1,2})\)",
                    string=row,
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                is not None
            ):
                ### POR QUE NUNCA PASA POR ESTE CONDICIONAL????
                pattern = re.compile(
                    r"(\S+) \(.*\) collected \([$,€](\d{1,2}\.\d{1,2})\)"
                )
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    amount = float(match.group(2))
                    for player in players:
                        if player.name == player_name:
                            round.pot = amount
                            print(f"{player.name} Won!")
                            round.set_winner(player)
                            break
        return round

    def _get_players(self, table: str) -> t.Generator[Player, None, None]:
        for row in table.split("\n"):
            if (
                re.match(pattern=r"Seat \d: \S+ \(.*\)", string=row, flags=re.DOTALL)
                is not None
            ):
                pattern = re.compile(r"Seat\s+(\d+):\s+([^(]+)\(€([\d\.]+)")
                match = pattern.search(row)
                if match:
                    seat = int(match.group(1))
                    name = match.group(2).strip()
                    currency = float(match.group(3))
                    player = Player(name=name, pot=currency, seat=seat)
                    yield player

    def parse(
        self,
        export: bool = False,
        filepath: t.Optional[str] = None,
        file_content: t.Optional[str] = None,
    ) -> t.Iterable[Hand]:
        if file_content:
            pass
        else:
            if filepath:
                self.file_path = filepath
            with open(self.file_path, "r") as file:
                file_content = file.read()

        hands = self._get_hands(file_content)
        results: list[Hand] = []
        for hand in hands:
            try:
                sections = self._parse_hand(hand)
                if sections == {}:
                    continue
                players = list(self._get_players(sections["table"]))
                sections = [
                    self._parse_round(round_str=v, section=k, players=players)
                    for k, v in sections.items()
                ]
                winner = [s.winner for s in sections if s.winner is not None]
                if len(winner) > 0:
                    winner: Player = winner[0]
                hand_obj = Hand(players=players, rounds=sections)
                hand_obj.set_winner(winner)
                hand_obj.refresh()
                results.append(hand_obj)
            except Exception as e:
                self.failed += 1
        if export and filepath is not None:
            parser = PokerParser(file_path=filepath)

        return results

    def parse_dir(
        self, directory: str, export: bool = False, *args, **kwargs
    ) -> t.Iterable[Hand]:
        import time
        paths = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                if f.endswith(".txt"):
                    full_path = os.path.join(dirpath, f)
                    paths.append(full_path)  # guardar rutas completas

        data = []
        items = len(paths)
        with Progress() as prog:
            task = prog.add_task("Loading...", total = items)
            for path in paths:
                prog.advance(task_id=task, advance=1)
                with open(path, encoding="utf-8") as f:
                    raw = f.read()
                    data.append(raw)

        hands = "\n\n".join(data)
        if export:
            with open("aggregated_hands.txt", "w+") as f:
                f.write(hands)
        return self.parse(file_content=hands, *args, **kwargs)
