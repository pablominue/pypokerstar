import datetime
import os
import re
import typing as t

from rich.progress import Progress

from pypokerstar.src.game.poker import Bet, Card, Hand, Player, Round
from pypokerstar.src.parsers.parser import Parser
from pypokerstar.src.parsers.pokerparser import PokerParser

SPANISH_MAP = {
    "CARTAS DE MANO": "hole cards",
    "RESUMEN": "summary",
}


class PokerStarsParser:
    def __init__(self, file_path: str = "") -> None:
        self.file_path = file_path
        self.site = "PokerStars"
        self.failed = 0

    @staticmethod
    def _get_hands(file_content: str) -> t.List[str]:
        return [f.strip() for f in file_content.split("\n\n")]

    def _parse_hand(self, hand: str) -> dict[t.Any, t.Any]:
        regex_section = re.compile(r"\*\*\* (.*?) \*\*\*")
        if hand == "":
            return {}
        date_pattern = re.compile(r"\d+\/\d+\/\d+ \d{2}:\d{2}:\d{2}")
        match = date_pattern.search(hand)
        if match:
            date_str = match.group(0)
        else:
            return {}

        sections = list(regex_section.finditer(hand))
        results = {}
        if (
            re.search(
                pattern=r"Total pot [$,€](\d+\.\d+)",
                flags=re.DOTALL | re.IGNORECASE,
                string=hand,
            )
            is not None
        ):
            pattern = re.compile(
                r"Total pot [$,€](\d+\.\d+)", flags=re.DOTALL | re.IGNORECASE
            )
            match = pattern.search(hand)
            if match:
                results["pot"] = float(match.group(1))

        if (
            re.search(
                pattern=r"Rake [$,€](\d+\.\d+)",
                flags=re.DOTALL | re.IGNORECASE,
                string=hand,
            )
            is not None
        ):
            pattern = re.compile(
                r"Rake [$,€](\d+\.\d+)", flags=re.DOTALL | re.IGNORECASE
            )
            match = pattern.search(hand)
            if match:
                results["rake"] = float(match.group(1))

        if date_str is not None:
            results["date"] = datetime.datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
        results["table"] = hand[0 : sections[0].start()].strip()
        for i, match in enumerate(sections):
            start = match.end()
            end = sections[i + 1].start() if i + 1 < len(sections) else len(hand)
            section_name = match.group(1).strip().upper()
            section_name = SPANISH_MAP.get(section_name, section_name.lower())
            results[section_name] = hand[start:end].strip()

        return results

    def _parse_round(
        self, round_str: str, section: str, players: t.Iterable[Player]
    ) -> t.Optional[Round]:
        try:
            round = Round(name=section)
        except ValueError:
            return None
        for row in round_str.split("\n"):
            if (
                re.search(
                    pattern=r"Dealt to (.+?)(?:\(.*\) )? \[(.*)\]$",
                    string=row,
                    flags=re.DOTALL,
                )
                is not None
            ):
                pattern = re.compile(r"Dealt to (.+?)(?:\(.*\) )? \[(.*)\]$")
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
                    pattern=r"(.+?)(?:\(.*\) )?\: (bets|calls|raises|folds|checks)( .*)?$",
                    string=row,
                    flags=re.DOTALL,
                )
                is not None
            ):
                pattern = re.compile(
                    r"(.+?)(?:\(.*\) )?\: (bets|calls|raises|folds|checks)( .*)?$"
                )
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    action = match.group(2)
                    amount_str = match.group(3).strip() if match.group(3) else ""
                    amount = 0.0
                    if amount_str:
                        if action == "raises":
                            to_match = re.search(r"to\s+[€,$]?([\d\.]+)", amount_str)
                            if to_match:
                                amount = float(to_match.group(1))
                            else:
                                euros = re.findall(r"[€,$]([\d\.]+)", amount_str)
                                if euros:
                                    amount = float(euros[-1])
                        else:
                            amount_pattern = re.compile(r"[€,$]([\d\.]+)")
                            amount_match = amount_pattern.search(amount_str)
                            if amount_match:
                                amount = float(amount_match.group(1))
                    for player in players:
                        if player.name == player_name:
                            bet = Bet(player=player, bet_type=action, amount=amount)
                            round.add_bet(bet)
            elif (
                re.match(
                    pattern=r"(.+?)(?:\(.*\) )?\: posts \S+ blind (?:[€,$])?(\d+(?:\.\d+)?)$",
                    string=row,
                    flags=re.DOTALL | re.IGNORECASE,
                )
                is not None
            ):
                pattern = re.compile(
                    r"(.+?)(?:\(.*\) )?\: posts (.*) blind (?:[€,$])?(\d+(?:\.\d+)?)$",
                    flags=re.DOTALL | re.IGNORECASE,
                )
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
                re.search(
                    pattern=r"Uncalled bet \((?:[$,€])?(\d+\.\d+|\d+)\) returned to (.+)",
                    string=row,
                    flags=re.DOTALL | re.IGNORECASE,
                )
                is not None
            ):
                # Track uncalled bet returns as negative amount for the player
                pattern = re.compile(
                    r"Uncalled bet \((?:[$,€])?(\d+\.\d+|\d+)\) returned to (.+)",
                    flags=re.DOTALL | re.IGNORECASE,
                )
                match = pattern.search(row)
                if match:
                    amount = float(match.group(1))
                    player_name = match.group(2)
                    for player in players:
                        if player.name == player_name:
                            round.add_bet(
                                Bet(
                                    player=player,
                                    bet_type="uncalled",
                                    amount=-amount,
                                )
                            )
            elif (
                re.search(
                    pattern=r"(?:Seat \d\: )?(.+?) (?:\(.*\) )?collected \((?:[$,€])?(\d{1,2}\.\d{1,2}|\d+)\)",
                    string=row,
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                is not None
            ):
                pattern = re.compile(
                    r"(?:Seat \d\: )?(.+?) (?:\(.*\) )?collected \((?:[$,€])?(\d{1,2}\.\d{1,2}|\d+)\)",
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                match = pattern.search(row)
                if match:
                    player_name = match.group(1)
                    amount = float(match.group(2))
                    for player in players:
                        if player.name == player_name:
                            round.pot = amount
                            round.set_winner(player)
                            # Add an explicit collected payout event for per-player accounting
                            round.add_bet(
                                Bet(
                                    player=player,
                                    bet_type="collected",
                                    amount=amount,
                                )
                            )
                    if "€" in row or "$" in row:
                        round.game_type = "cash"
                    else:
                        round.game_type = "tournament"

            elif (
                re.search(
                    pattern=r"(?:Seat \d\: )?(.+?) (?:\(.*\) )?showed \[.*\] and won \((?:[$,€])?(\d+\.\d+|\d|\d+)\)",
                    string=row,
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                is not None
            ):
                pattern = re.compile(
                    pattern=r"(?:Seat \d\: )?(.+?) (?:\(.*\) )?showed \[.*\] and won \((?:[$,€])?(\d+\.\d+|\d|\d+)\)",
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                match = pattern.search(row)
                if match:
                    if "€" in row or "$" in row:
                        round.game_type = "cash"
                    else:
                        round.game_type = "tournament"
                    player_name = match.group(1)
                    amount = float(match.group(2))
                    for player in players:
                        if player.name == player_name:
                            round.pot = amount
                            round.set_winner(player)
                            # Add an explicit collected payout event for per-player accounting
                            round.add_bet(
                                Bet(
                                    player=player,
                                    bet_type="collected",
                                    amount=amount,
                                )
                            )

        return round

    def _get_players(self, table: str) -> t.Generator[Player, None, None]:
        for row in table.split("\n"):
            if (
                re.match(pattern=r"Seat \d\: .* \(.*\)", string=row, flags=re.DOTALL)
                is not None
            ):
                pattern = re.compile(
                    r"Seat (\d+)\: (.+?) \((?:[€,$])?(\d+\.\d+|\d+).+\)"
                )
                match = pattern.search(row)
                if match:
                    seat = int(match.group(1))
                    name = match.group(2).strip()
                    currency = float(match.group(3))
                    player = Player(name=name, pot=currency, seat=seat)
                    yield player
                else:
                    print("No match for player in row:", row)

    def parse(
        self,
        export: bool = False,
        filepath: t.Optional[str] = None,
        file_content: t.Optional[str] = None,
        hero: t.Optional[Player] = None,
        skip_tournaments: bool = True,
        progress: bool = True,
    ) -> t.Iterable[Hand]:
        if file_content:
            pass
        else:
            if filepath:
                self.file_path = filepath
            with open(self.file_path, "r") as file:
                file_content = file.read()

        hands = self._get_hands(file_content)
        hands = [hand for hand in hands if hand.strip() != ""]
        results: list[Hand] = []
        with Progress() as prog:
            if progress:
                task = prog.add_task("Parsing file...", total=len(hands), color="blue")
            for hand in hands:
                try:
                    id_pattern = re.compile(r"Hand \#(\d*)\:")
                    match = id_pattern.search(hand)
                    if not match:
                        print("No hand ID found, skipping hand.")
                        print(f"This error comes from {self.file_path}")
                        print(hand)
                        self.failed += 1
                        continue
                    hand_id = match.group(1)
                    
                    if skip_tournaments:
                        if re.search(
                            pattern=r"Tournament",
                            flags=re.DOTALL | re.IGNORECASE,
                            string=hand,
                        ):
                            if progress:
                                prog.advance(task_id=task, advance=2)
                            continue
                    
                    sections = self._parse_hand(hand)
                    if sections == {}:
                        continue
                    players = list(self._get_players(sections["table"]))
                    date = sections.get("date", None)
                    pot = sections.get("pot", 0.0)
                    rake = sections.get("rake", 0.0)
                    sections = [
                        self._parse_round(round_str=v, section=k, players=players)
                        for k, v in sections.items()
                        if k not in ("table", "date", "pot", "rake")
                    ]
                    sections = [s for s in sections if s is not None]
                    winner = [s.winner for s in sections if s.winner is not None]
                    if len(winner) > 0:
                        winner: Player = winner[0]
                    try:
                        hand_obj = Hand(
                            id=hand_id,
                            raw_text=hand,
                            players=players,
                            rounds=sections,
                            hero=hero,
                            date=date,
                            pot=pot,
                            rake=rake,
                        )
                    except ValueError as e:
                        self.failed += 1
                        continue
                    # Infer game type at hand level from any round signal
                    try:
                        if any(
                            getattr(r, "game_type", "cash") == "cash" for r in sections
                        ):
                            hand_obj.game_type = "cash"
                        elif any(
                            getattr(r, "game_type", "cash") == "tournament"
                            for r in sections
                        ):
                            hand_obj.game_type = "tournament"
                    except Exception:
                        pass
                    hand_obj.refresh()
                    results.append(hand_obj)

                    if len(hand_obj.winner) == 0:
                        print("No winner found in hand:")
                        print(hand)
                        break
                except Exception as e:
                    print(e)
                    self.failed += 1
                    continue
                if progress:
                    prog.advance(task_id=task, advance=2)
        if self.failed > 0:
            print("Failed to parse hands:", self.failed)
        return results

    def parse_dir(
        self,
        directory: str,
        export: bool = False,
        hero: t.Optional[Player] = None,
        *args,
        **kwargs,
    ) -> t.Iterable[Hand]:

        paths = []
        if os.path.exists(directory) is False:
            raise ValueError(f"Directory {directory} does not exist")
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                if f.endswith(".txt"):
                    full_path = os.path.join(dirpath, f)
                    paths.append(full_path)  # guardar rutas completas

        data: t.Iterable[Hand] = []
        with Progress() as prog:
            task = prog.add_task(f"Parsing Directory...", total=len(paths), color="red")
            for path in paths:
                hand = self.parse(filepath=path, hero=hero, progress=False, *args, **kwargs)
                data.extend(hand)
                prog.advance(task_id=task, advance=1)
        return data
