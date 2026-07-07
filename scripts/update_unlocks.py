"""Recompute progress.json from mastery.json + DAG. Only path to 'mastered'."""
import json
import os
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.validate_syllabus import load_syllabus

GATE = 0.8


def recompute(units, progress, mastery):
    prog = {u["id"]: dict(progress.get(u["id"], {"status": "locked"})) for u in units}
    for uid, rec in mastery.items():
        if uid in prog and rec.get("score", 0) >= GATE:
            prog[uid]["status"] = "mastered"
    mastered = {u for u, p in prog.items() if p["status"] == "mastered"}
    for u in units:
        cur = prog[u["id"]]["status"]
        if cur in ("mastered", "in-progress"):
            continue
        if all(p in mastered for p in u["prereqs"]):
            prog[u["id"]]["status"] = "unlocked"
    return prog


def main():
    units = load_syllabus("curriculum/syllabus.yaml")["units"]
    with open("state/progress.json", encoding="utf-8") as f:
        progress = json.load(f)
    mastery = {}
    if os.path.exists("state/mastery.json"):
        with open("state/mastery.json", encoding="utf-8") as f:
            mastery = json.load(f)
    new = recompute(units, progress, mastery)
    newly = [u for u in new if new[u]["status"] == "unlocked"
             and progress.get(u, {}).get("status") == "locked"]
    tmp = "state/progress.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
    os.replace(tmp, "state/progress.json")
    print(json.dumps({"newly_unlocked": newly}))


if __name__ == "__main__":
    main()
