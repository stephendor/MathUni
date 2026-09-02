"""Spaced-repetition scheduler. Zero-token: /review shells out here.
Ratings: 1=again 2=hard 3=good 4=easy.

Two engines share the flat deck.json: the default SM-2 (rate_card below) and the
vendored FSRS-4.5 core in srs/fsrs.py. FSRS is staged behind srs/config.json
("scheduler": "sm2"|"fsrs"); it stays dormant until `swap-to-fsrs` flips it, which
the engram trip-wire prompts once ~50 reviews are logged. See docs/engram-fsrs-swap.md."""
import json
import os
import sys
import threading
from datetime import date, timedelta

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cards carry maths Unicode (⇒, ∩, subscripts). Force UTF-8 I/O so JSON output
# does not crash under a legacy console codepage (Windows cp1252 when piped).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

EASE_FLOOR = 1.3
DECK = "srs/deck.json"
CONFIG = "srs/config.json"
DEFAULT_CONFIG = {"scheduler": "sm2", "engram_threshold": 50}

# The deck is a whole-file read-modify-write. scripts/serve.py is threaded, so
# two /api/rate requests -- two review tabs, or a double-click -- could load
# the same snapshot and both save it, silently dropping one rating while both
# clients were told it succeeded. os.replace makes each write atomic; it does
# nothing about a lost update. This serialises the whole transaction.
_DECK_LOCK = threading.Lock()


def rate_card(card, rating, today):
    """SM-2 transition (unchanged). Returns the updated card."""
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
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(deck, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def load_config(path=CONFIG):
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        pass
    return cfg


def save_config(cfg, path=CONFIG):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def total_reps(deck):
    return sum(c.get("reps", 0) for c in deck["cards"])


def engram_ready(deck, cfg):
    """The staged FSRS swap is worthwhile once enough reviews exist AND we're still on SM-2."""
    return cfg.get("scheduler") == "sm2" and total_reps(deck) >= cfg.get("engram_threshold", 50)


def engram_banner(deck, cfg):
    return (
        "[engram] %d reviews logged — the FSRS-4.5 swap is now worthwhile "
        "(it outperforms SM-2 once there is history to fit).\n"
        "         Flip when ready:  python srs/scheduler.py swap-to-fsrs\n"
        "         Details: docs/engram-fsrs-swap.md  "
        "(per-user refit unlocks after ~%d further FSRS reviews)"
        % (total_reps(deck), cfg.get("engram_threshold", 50))
    )


def rate_and_save(cfg, cid, rating, today, path=DECK):
    """Load, rate and save under one lock. The safe entry point for callers
    that may run concurrently (the server); returns the updated card or None.

    Re-reads the deck INSIDE the lock deliberately: a snapshot taken before
    acquiring it is exactly the stale copy this is here to prevent.
    """
    with _DECK_LOCK:
        deck = load_deck(path)
        return apply_rating(deck, cfg, cid, rating, today, path=path)


def apply_rating(deck, cfg, cid, rating, today, path=DECK):
    """Rate one card through whichever engine is configured, and persist.

    Extracted from main() so the local server writes back through the same
    path the CLI uses. Two copies of the SM-2/FSRS branch would be two chances
    to diverge, and the one in the server would be the one nobody reads.

    Callers that can overlap must use rate_and_save() instead: this operates on
    a deck the caller already loaded, and cannot protect a read it did not do.

    Returns the updated card, or None when no card carries that id.
    """
    for i, c in enumerate(deck["cards"]):
        if c["id"] != cid:
            continue
        if cfg.get("scheduler") == "fsrs":
            from srs import fsrs
            mem = deck.get("memory", {})
            rec = fsrs.review_record(c, rating, today)
            with open(fsrs.REVIEW_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            deck["cards"][i] = fsrs.rate_card(
                c, rating, today,
                retention=mem.get("desired_retention", fsrs.RETENTION_DEFAULT),
                im=mem.get("interval_multiplier", 1.0))
        else:
            deck["cards"][i] = rate_card(c, rating, today)
        save_deck(deck, path)
        return deck["cards"][i]
    return None


def main(argv):
    today = date.today().isoformat()
    cmd = argv[0] if argv else "due"
    deck = load_deck()
    cfg = load_config()

    # Trip-wire: surface the deferred FSRS swap on the review path, once, on stderr
    # (stdout stays pure JSON for the skills). Self-silences after swap-to-fsrs.
    if cmd in ("due", "rate") and engram_ready(deck, cfg):
        print(engram_banner(deck, cfg), file=sys.stderr)

    if cmd == "due":
        print(json.dumps(due_cards(deck, today), ensure_ascii=False, indent=1))
    elif cmd == "rate":
        cid, rating = argv[1], int(argv[2])
        card = apply_rating(deck, cfg, cid, rating, today)
        if card is None:
            print(f"ERROR: no card {cid}"); sys.exit(1)
        print(json.dumps(card, ensure_ascii=False))
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
        print(json.dumps({
            "total": n, "due_today": due, "by_unit": by_unit,
            "scheduler": cfg.get("scheduler", "sm2"),
            "engram": {"total_reps": total_reps(deck),
                       "threshold": cfg.get("engram_threshold", 50),
                       "ready": engram_ready(deck, cfg)},
        }, indent=1))
    elif cmd == "swap-to-fsrs":
        from srs import fsrs
        if cfg.get("scheduler") == "fsrs":
            print("already on FSRS — nothing to do"); return
        fsrs.migrate_deck(deck, today)
        save_deck(deck)
        cfg["scheduler"] = "fsrs"; save_config(cfg)
        print("swapped to FSRS-4.5: migrated %d cards, config updated. "
              "SM-2 ease/interval shed; stability seeded from intervals." % len(deck["cards"]))
    elif cmd == "refit":
        from srs import fsrs
        records = []
        try:
            with open(fsrs.REVIEW_LOG, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except FileNotFoundError:
            pass
        force = len(argv) > 1 and argv[1] == "--force"
        mem = deck.setdefault("memory", {"interval_multiplier": 1.0,
                                         "desired_retention": fsrs.RETENTION_DEFAULT})
        res = fsrs.refit(records, mem.get("interval_multiplier", 1.0), force=force)
        if res["ok"]:
            mem["interval_multiplier"] = res["interval_multiplier"]["after"]
            save_deck(deck)
        print(json.dumps(res, indent=1))
    else:
        print("usage: scheduler.py [due|rate <id> <1-4>|add <file>|stats|swap-to-fsrs|refit [--force]]")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
