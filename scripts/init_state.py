"""Seed state/ from curriculum/syllabus.yaml. Refuses to clobber existing
progress without --force. Writes atomically (tmp file + rename)."""
import json
import os
import sys
from datetime import date

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.validate_syllabus import load_syllabus
else:
    from scripts.validate_syllabus import load_syllabus


def seed_progress(doc):
    return {u["id"]: {"status": "unlocked" if not u.get("prereqs") else "locked"}
            for u in doc.get("units", [])}


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv):
    force = "--force" in argv
    if os.path.exists("state/progress.json") and \
            os.path.getsize("state/progress.json") > 2 and not force:
        print("state/progress.json exists; use --force to reseed")
        sys.exit(1)
    os.makedirs("state/sessions", exist_ok=True)
    doc = load_syllabus("curriculum/syllabus.yaml")
    write_atomic("state/progress.json",
                 json.dumps(seed_progress(doc), indent=2))
    write_atomic("state/streaks.json", json.dumps(
        {"current": 0, "best": 0, "study_days": [],
         "seeded": date.today().isoformat()}, indent=2))
    write_atomic("state/SESSION-HANDOFF.md",
                 "# Session Handoff\n\nFresh install; no sessions yet. "
                 "Start with /today (Phase 1).\n")
    print("state seeded")


if __name__ == "__main__":
    main(sys.argv[1:])
