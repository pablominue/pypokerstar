import os
import collections
import typing as t
from collections import defaultdict, Counter


import polars as pl

from pypokerstar.src.game.poker import History, Player, Hand
from pypokerstar.src.parsers.pokerstars import PokerStarsParser

from rich.progress import Progress

player = Player(name="pipinoelbreve9")
hands = PokerStarsParser("").parse_dir("PokerStars/", hero=player)
history = History(hands=hands, hero=player)

villain = Player("Ivangennaro")


# Helpers
RANK_MAP = {1: "A", 10: "T", 11: "J", 12: "Q", 13: "K"}


def rank_str(n: int) -> str:
    return RANK_MAP.get(n, str(n))


def pair_notation(c1, c2) -> str:
    # produce canonical two-card notation like "AKs", "76o", "TT"
    if c1 is None or c2 is None:
        return None
    # ensure ordering high to low by number
    a, b = (c1, c2) if c1.number >= c2.number else (c2, c1)
    if a.number == b.number:
        return f"{rank_str(a.number)}{rank_str(b.number)}"
    suited = "s" if a.suit == b.suit else "o"
    return f"{rank_str(a.number)}{rank_str(b.number)}{suited}"


def get_player_bets_for(hand: Hand, player: Player) -> list:
    bets = []
    for rnd in hand.rounds:
        for b in rnd.bets:
            if b.player == player:
                bets.append((rnd.name.lower(), b))
    return bets


# Accumulators
per_hand_rows = []
pos_range: dict[t.Any, dict[str, collections.Counter]] = {}
vpip_count = 0
pfr_count = 0
total_hands_with_villain = 0
hands_seen_for_range = 0

def build_player_bets_map(hand: Hand) -> dict[str, list[tuple[str, "Bet"]]]:
    """Return mapping player_name -> list of (round_name, bet) in chronological order."""
    bets_map: dict[str, list[tuple[str, "Bet"]]] = defaultdict(list)
    for rnd in hand.rounds:
        rnd_name = rnd.name.lower()
        for bet in rnd.bets:
            # use canonical player name
            name = getattr(bet.player, "name", None)
            if name:
                bets_map[name].append((rnd_name, bet))
    return bets_map

# per-player accumulators
per_player_stats: dict[str, dict] = defaultdict(lambda: {
    "hands": 0,
    "vpip": 0,
    "pfr": 0,
    "3bet": 0,
    "invested": 0.0,
    "collected": 0.0,
    "showdown_seen": 0,
    "pos_ranges": defaultdict(lambda: {"openers": Counter(), "callers": Counter(), "3bet": Counter(), "total_seen": 0}),
})
per_hand_rows = []


def get_dataframe() -> pl.DataFrame:
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing hands...", total=len(history.hands))
        for hand in history.hands:
            hand.refresh()
            bets_map = build_player_bets_map(hand)

            # iterate canonical players present in the hand
            for player_obj in hand.players:
                if player_obj is None:
                    continue
                name = player_obj.name
                stats = per_player_stats[name]
                stats["hands"] += 1

                # preflop bets for this player
                player_bets = [b for (rnd, b) in bets_map.get(name, []) if rnd == "hole cards"]

                # VPIP: voluntarily put money in pot preflop (calls/bets/raises) excluding forced posts
                did_vpip = any(b.type in ("calls", "bets", "raises") for b in player_bets)
                if did_vpip:
                    stats["vpip"] += 1

                # PFR: raised preflop
                did_pfr = any(b.type == "raises" for b in player_bets)
                if did_pfr:
                    stats["pfr"] += 1

                # detect 3bet: player raised and there was any earlier raise by another player in same preflop
                is_3bet = False
                preflop_bets = [b for (rnd, b) in bets_map.get(name, []) if rnd == "hole cards"]
                # build chronological list of all preflop bets
                all_preflop = [b for (rnd, b) in (x for x in [(r.name.lower(), bet) for r in hand.rounds for bet in r.bets] ) if b is not None]  # fallback, but we'll build below

                # safer: construct chronological preflop bets from hole round if present
                hole_round = hand.get_round("hole cards")
                all_preflop = hole_round.bets if hole_round else []
                for idx, b in enumerate(all_preflop):
                    if b.player == player_obj and b.type == "raises":
                        earlier_raises = any(
                            all_preflop[i].type == "raises" and all_preflop[i].player != player_obj
                            for i in range(0, idx)
                        )
                        if earlier_raises:
                            is_3bet = True
                        break
                if is_3bet:
                    stats["3bet"] += 1

                # invested / collected (sum across rounds using bets_map)
                invested = sum(b.amount for lst in bets_map.get(name, []) for (_, b) in [(None, lst[1])] if b.type != "collected")  # simplified below

                # simpler correct calculation:
                invested = 0.0
                collected = 0.0
                for (_, b) in bets_map.get(name, []):
                    if b.type == "collected":
                        collected += b.amount
                    else:
                        invested += b.amount

                stats["invested"] += invested
                stats["collected"] += collected

                # showdown cards if available
                showdown_cards = None
                c = getattr(player_obj, "cards", None)
                if isinstance(c, (list, tuple)) and len(c) >= 2:
                    showdown_cards = pair_notation(c[0], c[1])

                # position: prefer seat attribute, normalize to string key
                pos = getattr(player_obj, "seat", None)
                if pos is None:
                    try:
                        pos = next(i + 1 for i, p in enumerate(hand.players) if p.name == name)
                    except StopIteration:
                        pos = "unknown"
                pos_key = pos

                # record per-position showdown range usage
                if showdown_cards:
                    stats["showdown_seen"] += 1
                    pr = stats["pos_ranges"][pos_key]
                    pr["total_seen"] += 1
                    if is_3bet:
                        pr["3bet"][showdown_cards] += 1
                    elif did_pfr:
                        # determine opener: first raise in the hole round
                        preflop_raises = [b for b in (hole_round.bets if hole_round else []) if b.type == "raises"]
                        if preflop_raises and preflop_raises[0].player == player_obj:
                            pr["openers"][showdown_cards] += 1
                        else:
                            pr["openers"][showdown_cards] += 1
                    elif did_vpip:
                        pr["callers"][showdown_cards] += 1

                per_hand_rows.append({
                    "player": name,
                    "hand_id": getattr(hand, "id", None),
                    "date": hand.date,
                    "position": pos_key,
                    "vpip": did_vpip,
                    "pfr": did_pfr,
                    "3bet": is_3bet,
                    "invested": invested,
                    "collected": collected,
                    "showdown_cards": showdown_cards,
                    "winner": any(w.name == name for w in hand.winner),
                })
            progress.update(task, advance=1)
    return pl.DataFrame(per_hand_rows)
# Build DataFrame
df = get_dataframe()

# Print summary for a particular player (example)
def print_player_summary(name: str):
    s = per_player_stats.get(name)
    if not s:
        print(f"No data for {name}")
        return
    hands = s["hands"]
    vpip_pct = s["vpip"] / hands * 100 if hands else 0.0
    pfr_pct = s["pfr"] / hands * 100 if hands else 0.0
    print(f"{name}: hands={hands} VPIP={s['vpip']} ({vpip_pct:.1f}%) PFR={s['pfr']} ({pfr_pct:.1f}%) showdowns={s['showdown_seen']}")

print_player_summary("Ivangennaro")

# dump CSV
out_csv = os.path.join(os.getcwd(), "player_stats.csv")
df.write_csv(out_csv)
print(f"Wrote {out_csv}")