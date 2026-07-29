"""Reconcile curriculum unit ids across every store that mirrors them."""
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_syllabus import load_syllabus

UNIT_ID = re.compile(r"^[a-z][a-z0-9]*-\d{2}$")


def _json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def find_orphans(root=Path(".")):
    root = Path(root)
    syllabus = load_syllabus(root / "curriculum/syllabus.yaml")
    live = {unit["id"] for unit in syllabus.get("units", [])}
    refs = []

    progress = _json(root / "state/progress.json")
    refs.extend(("state/progress.json", unit_id) for unit_id in progress)
    errors = []

    for rel in ("srs/deck.json", "srs/seed-batch-01.json"):
        data = _json(root / rel)
        cards = data.get("cards", []) if isinstance(data, dict) else data
        refs.extend((rel, card.get("unit")) for card in cards)

    patterns = (
        ("lessons/*/*.html", lambda path: path.stem),
        ("problems/sets/*.md", lambda path: path.stem.removesuffix("-remedial")),
        ("problems/solutions/*.md", lambda path: path.stem),
        ("learning-records/*.md", lambda path: path.stem),
    )
    for pattern, unit_from_path in patterns:
        for path in root.glob(pattern):
            unit_id = unit_from_path(path)
            if UNIT_ID.match(unit_id):
                refs.append((path.relative_to(root).as_posix(), unit_id))

    errors.extend(
        f"{path}: orphan unit id {unit_id!r}"
        for path, unit_id in refs
        if unit_id and unit_id not in live
    )

    modules = {unit["id"]: unit.get("module") for unit in syllabus.get("units", [])}
    for unit_id, record in progress.items():
        if record.get("status") not in {"mastered", "in-progress"}:
            continue
        module = modules.get(unit_id)
        if not module:
            continue
        expected = (
            root / f"lessons/{module}/{unit_id}.html",
            root / f"problems/sets/{unit_id}.md",
            root / f"problems/solutions/{unit_id}.md",
            root / f"learning-records/{unit_id}.md",
        )
        errors.extend(
            f"{path.relative_to(root).as_posix()}: missing for "
            f"{record.get('status')} unit {unit_id!r}"
            for path in expected
            if not path.exists()
        )
    return errors


def main():
    try:
        errors = find_orphans()
    except (FileNotFoundError, ValueError, TypeError) as exc:
        print(f"ERROR: curriculum integrity inputs unavailable: {exc}")
        return 1
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("unit ids consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
