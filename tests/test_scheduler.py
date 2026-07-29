import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from srs.scheduler import rate_card, due_cards

def card(**kw):
    c = {"id": "x", "unit": "la-01", "type": "definition", "front": "f",
         "back": "b", "ease": 2.5, "interval": 0, "due": "2026-07-07",
         "reps": 0, "lapses": 0}
    c.update(kw); return c

def test_new_card_good_schedules_one_day():
    c = rate_card(card(), 3, "2026-07-07")
    assert c["interval"] == 1 and c["due"] == "2026-07-08" and c["reps"] == 1

def test_new_card_easy_schedules_three_days():
    c = rate_card(card(), 4, "2026-07-07")
    assert c["interval"] == 3 and c["due"] == "2026-07-10"

def test_good_multiplies_by_ease():
    c = rate_card(card(interval=4, reps=2), 3, "2026-07-07")
    assert c["interval"] == 10  # round(4 * 2.5)

def test_again_resets_and_counts_lapse():
    c = rate_card(card(interval=10, reps=5), 1, "2026-07-07")
    assert c["interval"] == 0 and c["due"] == "2026-07-07" and c["lapses"] == 1
    assert c["ease"] == 2.3

def test_ease_floors_at_1_3():
    c = rate_card(card(ease=1.35), 1, "2026-07-07")
    assert c["ease"] == 1.3

def test_hard_grows_slowly_and_drops_ease():
    c = rate_card(card(interval=10, ease=2.5), 2, "2026-07-07")
    assert c["interval"] == 12 and c["ease"] == 2.35  # round(10*1.2)

def test_due_cards_filters_and_sorts():
    deck = {"cards": [card(id="a", due="2026-07-08"), card(id="b", due="2026-07-06"),
                      card(id="c", due="2026-07-07")]}
    ids = [c["id"] for c in due_cards(deck, "2026-07-07")]
    assert ids == ["b", "c"]

def test_stdout_commands_emit_utf8_json_when_parent_requests_cp1252(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    (tmp_path / "srs").mkdir()
    shutil.copy(repo / "srs/config.json", tmp_path / "srs/config.json")
    deck = {
        "cards": [card(id="unicode", front="A₁ ∩ A₂ ⇒ B", due="2000-01-01")],
    }
    (tmp_path / "srs/deck.json").write_text(
        json.dumps(deck, ensure_ascii=False), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    script = repo / "srs/scheduler.py"

    for command in (["due"], ["stats"], ["rate", "unicode", "3"]):
        result = subprocess.run(
            [sys.executable, str(script), *command],
            cwd=tmp_path, env=env, capture_output=True,
        )
        assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
        json.loads(result.stdout.decode("utf-8"))
