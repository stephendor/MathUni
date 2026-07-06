"""Render dashboard/index.html: kanban by status, module progress, streaks.
Pure stdlib + repo data; /status runs this CLI."""
import json
import os
import sys
from html import escape

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.validate_syllabus import load_syllabus

COLUMNS = ["unlocked", "in-progress", "mastered", "locked"]
LABELS = {"unlocked": "Unlocked", "in-progress": "In progress",
          "mastered": "Mastered", "locked": "Locked"}

CSS = """body{font-family:Segoe UI,system-ui,sans-serif;background:#101418;color:#e8e8e8;margin:2rem}
h1{font-weight:600}.streak{font-size:1.1rem;margin-bottom:1.5rem}
.board{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.col{background:#1a2027;border-radius:10px;padding:.8rem}.col h2{font-size:.95rem;text-transform:uppercase;letter-spacing:.05em;color:#8ab4f8}
.card{background:#232b34;border-radius:8px;padding:.6rem .8rem;margin:.5rem 0;font-size:.9rem}
.card small{color:#9aa5b1;display:block}
.mods{margin-top:2rem}.bar{background:#232b34;border-radius:6px;height:14px;overflow:hidden;margin:.3rem 0 1rem}
.fill{background:#4caf82;height:100%}"""


def render(syllabus, progress, streaks):
    units = syllabus.get("units", [])
    mods = {m["id"]: m for m in syllabus.get("modules", [])}
    status = {u["id"]: progress.get(u["id"], {}).get("status", "locked") for u in units}
    cols = []
    for c in COLUMNS:
        cards = "".join(
            f'<div class="card" data-status="{c}"><b>{escape(u["title"])}</b>'
            f'<small>{u["id"]} · {escape(mods.get(u["module"], {}).get("title", u["module"]))}</small></div>'
            for u in units if status[u["id"]] == c)
        cols.append(f'<div class="col"><h2>{LABELS[c]} ({sum(1 for u in units if status[u["id"]]==c)})</h2>{cards}</div>')
    modbars = []
    for mid, m in mods.items():
        mu = [u for u in units if u["module"] == mid]
        if not mu:
            continue
        done = sum(1 for u in mu if status[u["id"]] == "mastered")
        pct = int(100 * done / len(mu))
        modbars.append(f'<div><b>{escape(m["title"])}</b> {done}/{len(mu)}'
                       f'<div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>')
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>Nexus College</title>"
            f"<style>{CSS}</style></head><body><h1>Nexus College</h1>"
            f'<div class="streak">🔥 Streak: {streaks.get("current", 0)} (best {streaks.get("best", 0)}) · '
            f'{len(streaks.get("study_days", []))} study days total</div>'
            f'<div class="board">{"".join(cols)}</div>'
            f'<div class="mods"><h2>Module progress (mastered)</h2>{"".join(modbars)}</div>'
            "</body></html>")


def main():
    syllabus = load_syllabus("curriculum/syllabus.yaml")
    with open("state/progress.json", encoding="utf-8") as f:
        progress = json.load(f)
    with open("state/streaks.json", encoding="utf-8") as f:
        streaks = json.load(f)
    os.makedirs("dashboard", exist_ok=True)
    tmp = "dashboard/index.html.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(render(syllabus, progress, streaks))
    os.replace(tmp, "dashboard/index.html")
    print("dashboard/index.html written")


if __name__ == "__main__":
    main()
