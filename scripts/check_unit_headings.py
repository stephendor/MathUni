"""Validate edition-pinned unit title contracts against the syllabus."""
import argparse
import json
import re
import sys

import yaml


def contract_errors(unit, books, sections, contract):
    errors = []
    book = books.get(contract["book"])
    if not book:
        return ["book %s is absent" % contract["book"]]
    if book.get("edition") != contract["edition"]:
        errors.append("edition is %r, expected %r" % (
            book.get("edition"), contract["edition"]))
    indexed = sections.get(contract["book"], {}).get("sections", {})
    for section in contract["sections"]:
        if section not in indexed:
            errors.append("section %s is absent from the pinned edition" % section)
    title = unit["title"].lower()
    for term in contract["required_title_terms"]:
        if not re.search(r"\b%s\b" % re.escape(term.lower()), title):
            errors.append("unit title omits source-heading term %r" % term)
    return errors


def registry_errors(units, contracts):
    return ["heading contract names unknown unit %s" % unit
            for unit in sorted(set(contracts) - set(units))]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    parser.add_argument("--syllabus", default="curriculum/syllabus.yaml")
    parser.add_argument("--bookmap", default="resources/bookmap.json")
    parser.add_argument("--sections", default="resources/sections.json")
    parser.add_argument("--contracts", default="curriculum/unit-heading-contracts.json")
    args = parser.parse_args(argv)
    with open(args.syllabus, encoding="utf-8") as f:
        units = {u["id"]: u for u in yaml.safe_load(f)["units"]}
    with open(args.bookmap, encoding="utf-8") as f:
        books = json.load(f)
    with open(args.sections, encoding="utf-8") as f:
        sections = json.load(f)
    with open(args.contracts, encoding="utf-8") as f:
        contracts = json.load(f)
    missing_editions = sorted(name for name, data in books.items()
                              if not data.get("edition"))
    errors = (["bookmap entries lack edition: %s" % ", ".join(missing_editions)]
              if missing_editions else [])
    errors += registry_errors(units, contracts)
    if args.unit in contracts:
        errors += contract_errors(units[args.unit], books, sections,
                                  contracts[args.unit])
    for error in errors:
        print("FAIL " + error)
    print("%s %d heading/edition error(s)" % (
        "FAIL" if errors else "PASS", len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
