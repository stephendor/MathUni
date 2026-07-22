"""FSRS-4.5 scheduler core — a drop-in replacement for the SM-2 math in
`srs/scheduler.py`, staged behind the engram trip-wire (see docs/engram-fsrs-swap.md).

Vendored from the FSRS-4.5 core of engram (F:/Projects/engram/scripts/engram.py),
itself from open-spaced-repetition's FSRS-4.5. Only the *scheduling math* is
taken — NOT engram's concept-graph engine, receipts home, or learner model.
State stays repo-local in srs/deck.json; the flat flashcard deck is unchanged.

Stdlib only. Ratings: 1=again 2=hard 3=good 4=easy (same convention as scheduler.py).

Card memory fields (added on migration / first FSRS review):
  s    stability (days until R decays to `retention`)
  d    difficulty (1..10)
  last date of the last review (ISO)
Shared with SM-2: due, reps, lapses. The SM-2-only ease/interval are dropped.
Deck-level `memory`: {interval_multiplier, desired_retention} (refit tunes the multiplier).
"""
import json
import math
import os
from datetime import date, timedelta

RETENTION_DEFAULT = 0.90
INTERVAL_MAX = 365
REVIEW_LOG = "srs/reviews.jsonl"   # appended on each FSRS review; refit reads it
REFIT_THRESHOLD = 50               # min FSRS reviews (with a prediction) before refit is meaningful

# FSRS-4.5 default parameters (open-spaced-repetition). w[0..3] are initial
# stabilities for Again/Hard/Good/Easy; the rest shape difficulty and growth.
W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
     1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]
DECAY = -0.5
FACTOR = 19.0 / 81.0  # chosen so R(t=S) = 0.9

# ---------------------------------------------------------------- fsrs core

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def retrievability(elapsed_days, stability):
    if stability <= 0:
        return 0.0
    return (1.0 + FACTOR * elapsed_days / stability) ** DECAY

def interval_for(stability, retention=RETENTION_DEFAULT, multiplier=1.0):
    days = stability / FACTOR * (retention ** (1.0 / DECAY) - 1.0) * multiplier
    return int(clamp(round(days), 1, INTERVAL_MAX))

def init_stability(g):
    return clamp(W[g - 1], 0.1, 100.0)

def init_difficulty(g):
    return clamp(W[4] - (g - 3) * W[5], 1.0, 10.0)

def next_difficulty(d, g):
    nd = d - W[6] * (g - 3)
    nd = W[7] * init_difficulty(4) + (1.0 - W[7]) * nd  # mean reversion
    return clamp(nd, 1.0, 10.0)

def next_stability_recall(d, s, r, g):
    hard_penalty = W[15] if g == 2 else 1.0
    easy_bonus = W[16] if g == 4 else 1.0
    grow = (math.exp(W[8]) * (11.0 - d) * (s ** -W[9])
            * (math.exp(W[10] * (1.0 - r)) - 1.0) * hard_penalty * easy_bonus)
    return clamp(s * (1.0 + grow), 0.1, 36500.0)

def next_stability_forget(d, s, r):
    sf = W[11] * (d ** -W[12]) * (((s + 1.0) ** W[13]) - 1.0) * math.exp(W[14] * (1.0 - r))
    return clamp(min(sf, s), 0.1, 36500.0)  # a lapse never increases stability

# ---------------------------------------------------------------- card ops

def _elapsed(last, today):
    if not last:
        return 0
    t = today if isinstance(today, date) else date.fromisoformat(today)
    return max(0, (t - date.fromisoformat(last)).days)

def predicted_retrievability(card, today):
    """R the model expects for this card *now* — None if the card is unseen."""
    s0, last = card.get("s"), card.get("last")
    if s0 is None or not last:
        return None
    return round(retrievability(_elapsed(last, today), s0), 4)

def rate_card(card, rating, today, retention=RETENTION_DEFAULT, im=1.0):
    """Pure transition, drop-in for scheduler.rate_card: card + rating -> new card.

    `today` is an ISO date string (matching scheduler.py). `retention`/`im` come
    from deck-level memory; defaults reproduce stock FSRS-4.5.
    """
    g = int(rating)
    d0, s0, last = card.get("d"), card.get("s"), card.get("last")
    on = date.fromisoformat(today)
    if s0 is None:  # first exposure under FSRS
        s, d = init_stability(g), init_difficulty(g)
    else:
        r = retrievability(_elapsed(last, today), s0)
        d = next_difficulty(d0, g)
        s = next_stability_forget(d0, s0, r) if g == 1 else next_stability_recall(d0, s0, r, g)
    ivl = interval_for(s, retention, im)
    c = dict(card)
    c.pop("ease", None); c.pop("interval", None)  # shed SM-2-only fields
    c.update({
        "s": round(s, 4), "d": round(d, 4), "last": today,
        "due": (on + timedelta(days=ivl)).isoformat(),
        "reps": card.get("reps", 0) + 1,
        "lapses": card.get("lapses", 0) + (1 if (g == 1 and s0 is not None) else 0),
    })
    return c

def review_record(card_before, rating, today):
    """Evidence line for refit: the prediction made *before* applying the rating."""
    return {"ts": today, "id": card_before.get("id"), "unit": card_before.get("unit"),
            "rating": int(rating), "r": predicted_retrievability(card_before, today)}

def migrate_card(card, today):
    """Seed FSRS state from a card's SM-2 state, mechanically and losslessly for
    reps/lapses/due. Stability is seeded from the current interval (since
    interval_for(s,0.9)==s), difficulty neutral; unseen cards (interval 0) are
    left for first-review initialisation."""
    if "s" in card:
        return card  # already FSRS
    c = dict(card)
    ivl = c.pop("interval", 0) or 0
    c.pop("ease", None)
    if ivl > 0:
        c["s"] = float(max(0.1, ivl))
        c["d"] = round(init_difficulty(3), 4)  # neutral ("good")
        c["last"] = today
        c.setdefault("due", (date.fromisoformat(today) + timedelta(days=ivl)).isoformat())
    else:
        c["s"] = None; c["d"] = None; c["last"] = None
    return c

def migrate_deck(deck, today):
    deck.setdefault("memory", {"interval_multiplier": 1.0, "desired_retention": RETENTION_DEFAULT})
    deck["cards"] = [migrate_card(c, today) for c in deck["cards"]]
    deck["scheduler"] = "fsrs"
    return deck

# ---------------------------------------------------------------- refit

def refit(records, prev_multiplier=1.0, force=False):
    """Coarse per-user fit (engram v1): one interval multiplier. Compares observed
    recall to the model's predictions and rescales along the power-forgetting curve.
    Guarded on >=REFIT_THRESHOLD reviews that carried a prediction."""
    usable = [r for r in records if r.get("r") is not None]
    n = len(usable)
    if n < REFIT_THRESHOLD and not force:
        return {"ok": False, "n": n,
                "reason": "need >=%d reviews with predictions, have %d" % (REFIT_THRESHOLD, n)}
    observed = sum(1.0 for r in usable if r["rating"] != 1) / n
    predicted = sum(r["r"] for r in usable) / n
    def inv(x):
        return (clamp(x, 0.5, 0.999) ** (1.0 / DECAY)) - 1.0
    mult = clamp(inv(predicted) / inv(observed), 0.5, 1.5)
    return {"ok": True, "n": n, "observed_recall": round(observed, 3),
            "predicted_recall": round(predicted, 3),
            "interval_multiplier": {"before": prev_multiplier, "after": round(mult, 3)}}

# ---------------------------------------------------------------- selftest

def _approx(a, b, tol=0.001):
    return abs(a - b) <= tol * max(1.0, abs(b))

def selftest():
    total = [0]; failures = []
    def check(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            failures.append(name)

    # --- core identities (ported from engram selftest) ---
    check("R(t=S) == 0.9", _approx(retrievability(10, 10), 0.9))
    check("interval(S, 0.9) == S", interval_for(10, 0.9) == 10)
    check("interval multiplier scales", interval_for(10, 0.9, 0.5) == 5)
    check("initial stabilities ordered", W[0] < W[1] < W[2] < W[3])
    d, s, r = 5.0, 10.0, 0.9
    check("stability growth ordered hard<good<easy",
          next_stability_recall(d, s, r, 2) < next_stability_recall(d, s, r, 3)
          < next_stability_recall(d, s, r, 4))
    check("all recall ratings grow stability", s < next_stability_recall(d, s, r, 2))
    check("lapse shrinks stability", next_stability_forget(d, s, r) < s)
    check("lapse capped at prior S", next_stability_forget(2.0, 0.5, 0.99) <= 0.5)
    check("again raises difficulty", next_difficulty(5.0, 1) > 5.0)
    check("easy lowers difficulty", next_difficulty(5.0, 4) < 5.0)
    check("difficulty clamped", next_difficulty(10.0, 1) <= 10.0 and next_difficulty(1.0, 4) >= 1.0)
    check("R monotonic in elapsed", retrievability(20, 10) < retrievability(5, 10))
    check("harder material grows slower",
          next_stability_recall(9.0, s, r, 3) < next_stability_recall(2.0, s, r, 3))

    # --- card round-trip (drop-in behaviour) ---
    fresh = {"id": "x", "unit": "u", "ease": 2.5, "interval": 0, "due": "2026-07-05",
             "reps": 0, "lapses": 0}
    c1 = rate_card(fresh, 3, "2026-07-05")
    check("first review seeds s/d", c1["s"] is not None and c1["d"] is not None)
    check("first review sheds SM-2 fields", "ease" not in c1 and "interval" not in c1)
    check("good schedules into the future", c1["due"] > "2026-07-05" and c1["reps"] == 1)
    c2 = rate_card(c1, 1, c1["due"])
    check("again records a lapse", c2["lapses"] == 1)
    check("again shrinks stability", c2["s"] < c1["s"])

    # --- migration preserves reps/lapses/due, seeds stability from interval ---
    sm2 = {"id": "y", "unit": "u", "ease": 2.6, "interval": 12, "due": "2026-08-01",
           "reps": 3, "lapses": 1}
    m = migrate_card(sm2, "2026-07-22")
    check("migrate seeds stability from interval", _approx(m["s"], 12.0, 0.0001))
    check("migrate preserves reps/lapses/due",
          m["reps"] == 3 and m["lapses"] == 1 and m["due"] == "2026-08-01")
    check("migrate drops ease/interval", "ease" not in m and "interval" not in m)
    unseen = migrate_card({"id": "z", "unit": "u", "ease": 2.5, "interval": 0,
                           "due": "2026-07-05", "reps": 0, "lapses": 0}, "2026-07-22")
    check("migrate leaves unseen card for first-review init", unseen["s"] is None)

    # --- refit guard + direction (negative control on the threshold) ---
    thin = refit([{"rating": 3, "r": 0.9}] * 10)
    check("refit guarded under threshold", thin["ok"] is False and thin["n"] == 10)
    worse = [{"rating": (1 if i < 20 else 3), "r": 0.9} for i in range(50)]  # 60% observed vs 90% predicted
    fit = refit(worse)
    check("refit fires at threshold", fit["ok"] is True and fit["n"] == 50)
    check("refit shortens intervals when recall worse than predicted",
          fit["interval_multiplier"]["after"] < 1.0)

    print("\n%d/%d checks passed" % (total[0] - len(failures), total[0]))
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    print("usage: python srs/fsrs.py selftest")
