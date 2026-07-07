"""SM-2-style spaced repetition scheduler. Zero-token: /review shells out here.
Ratings: 1=again 2=hard 3=good 4=easy."""
import json
import os
import sys
from datetime import date, timedelta

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EASE_FLOOR = 1.3
DECK = "srs/deck.json"


def rate_card(card, rating, today):
    c = dict(card)
    d = date.fromisoformat(today)
    if rating == 1:
        c["ease"] = max(EASE_FLOOR, round(c["ease"] - 0.2, 2))
        c["interval"] = 0
        c["lapses"] += 1
        c["due"] = today
    elif rating == 2:
        c["ease"] = max(EASE_FLOOR, round(c["ease"] - 0.15, 2))
        c["interval"] = max(1, round(c["interval"] * 1.2)) if c["interval"] else 1
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    elif rating == 3:
        c["interval"] = round(c["interval"] * c["ease"]) if c["interval"] else 1
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    else:
        c["ease"] = round(c["ease"] + 0.1, 2)
        c["interval"] = round(c["interval"] * c["ease"] * 1.5) if c["interval"] else 3
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    c["reps"] += 1
    return c


def due_cards(deck, today):
    return sorted((c for c in deck["cards"] if c["due"] <= today),
                  key=lambda c: c["due"])


def load_deck(path=DECK):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_deck(deck, path=DECK):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def main(argv):
    from srs.scheduler import rate_card as _rc  # self-import safe under both invocations
    today = date.today().isoformat()
    cmd = argv[0] if argv else "due"
    deck = load_deck()
    if cmd == "due":
        print(json.dumps(due_cards(deck, today), ensure_ascii=False, indent=1))
    elif cmd == "rate":
        cid, rating = argv[1], int(argv[2])
        for i, c in enumerate(deck["cards"]):
            if c["id"] == cid:
                deck["cards"][i] = rate_card(c, rating, today)
                save_deck(deck)
                print(json.dumps(deck["cards"][i], ensure_ascii=False))
                return
        print(f"ERROR: no card {cid}"); sys.exit(1)
    elif cmd == "add":
        with open(argv[1], encoding="utf-8") as f:
            new = json.load(f)
        ids = {c["id"] for c in deck["cards"]}
        added = 0
        for c in new:
            if c["id"] in ids:
                continue
            c.setdefault("ease", 2.5); c.setdefault("interval", 0)
            c.setdefault("due", today); c.setdefault("reps", 0); c.setdefault("lapses", 0)
            deck["cards"].append(c); added += 1
        save_deck(deck)
        print(f"added {added} cards ({len(deck['cards'])} total)")
    elif cmd == "stats":
        n = len(deck["cards"]); due = len(due_cards(deck, today))
        by_unit = {}
        for c in deck["cards"]:
            by_unit[c["unit"]] = by_unit.get(c["unit"], 0) + 1
        print(json.dumps({"total": n, "due_today": due, "by_unit": by_unit}, indent=1))
    else:
        print("usage: scheduler.py [due|rate <id> <1-4>|add <file>|stats]"); sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
