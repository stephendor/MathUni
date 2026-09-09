"""Check that cross-unit references resolve to both governed artifacts."""
import argparse
import os
import re
import sys


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT_REF = re.compile(r"(?<![A-Za-z0-9])([a-z][a-z0-9]*-\d{2})(?![A-Za-z0-9])")
# Modules that no longer exist but whose ids a lesson may still legitimately
# name (a forward pointer to retired material, a historical note). Adding one
# here makes `gt-01` recognised as unit-shaped anywhere, not only after a
# cross-reference cue -- so the reference is then held to the missing-artifact
# check instead of being silently ignored as prose.
#
# It is an allowlist, so it ratchets: `--audit-retired` fails on an entry that
# has come back as a live module, and on one that nothing in the governed
# corpus references any more. Without that rule the set is a suppression list
# with a comment -- "the last reference was deleted two semesters ago" emits no
# signal, and absence of a signal cannot be read as absence of a backlog.
# Struck 2026-09-09: `gt` was the first thing --audit-retired reported. No file
# in the 290-file governed corpus had named a gt-NN unit for two semesters, so
# the entry had been excusing nothing and saying nothing about it. The empty
# set is the finished state, not the unconfigured one.
RETIRED_MODULES = set()


def governed_modules(repo=REPO):
    module_dir = os.path.join(repo, "curriculum", "modules")
    if os.path.isdir(module_dir):
        current = {os.path.splitext(name)[0] for name in os.listdir(module_dir)
                   if name.endswith(".md")}
    else:
        lesson_dir = os.path.join(repo, "lessons")
        current = set(os.listdir(lesson_dir)) if os.path.isdir(lesson_dir) else set()
        set_dir = os.path.join(repo, "problems", "sets")
        if os.path.isdir(set_dir):
            current.update(name.rsplit("-", 1)[0]
                           for name in os.listdir(set_dir) if name.endswith(".md"))
    return current | RETIRED_MODULES


def strip_noise(text):
    """Drop script/style bodies and comments — the containers whose contents a
    reader never sees, so a unit id inside one is not a cross-reference."""
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text,
                  flags=re.I | re.S)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def unit_refs(text, repo=REPO):
    text = strip_noise(text)
    modules = governed_modules(repo)
    refs = set()
    for match in UNIT_REF.finditer(text):
        uid = match.group(1)
        module = uid.rsplit("-", 1)[0]
        # Known module ids are unambiguous anywhere. An unknown prefix is only
        # unit-shaped evidence in an explicit cross-reference context; this
        # avoids treating mathematical compounds such as "genus-11" as ids.
        context = text[max(0, match.start() - 24):match.start()]
        cross_reference = re.search(
            r"(?:see|unit|lesson|problem set|from|deferred to|developed in|"
            r"covered in|proved in|introduced in|reviewed in|builds on)\s+$",
            context, re.I)
        if module in modules or cross_reference:
            refs.add(uid)
    return sorted(refs)


def missing_references(text, repo=REPO):
    missing = []
    for uid in unit_refs(text, repo=repo):
        module = uid.rsplit("-", 1)[0]
        expected = (
            os.path.join("problems", "sets", uid + ".md"),
            os.path.join("lessons", module, uid + ".html"),
        )
        absent = [path for path in expected
                  if not os.path.isfile(os.path.join(repo, path))]
        if absent:
            missing.append((uid, absent))
    return missing


def governed_corpus(repo=REPO):
    """Every governed lesson and problem set, derived from the syllabus.

    The population is derived mechanically rather than globbed, so a unit whose
    artifact is missing is a visible absence rather than a smaller denominator.
    Returns (paths, missing).
    """
    import yaml
    with open(os.path.join(repo, "curriculum", "syllabus.yaml"),
              encoding="utf-8") as handle:
        uids = [row["id"] for row in yaml.safe_load(handle)["units"]]
    paths, missing = [], []
    for uid in uids:
        module = uid.rsplit("-", 1)[0]
        for rel in (os.path.join("problems", "sets", uid + ".md"),
                    os.path.join("lessons", module, uid + ".html")):
            full = os.path.join(repo, rel)
            (paths if os.path.isfile(full) else missing).append(rel)
    return paths, missing


def stale_retired_modules(repo=REPO):
    """RETIRED_MODULES entries that no longer excuse anything.

    Two ways an entry rots, both the shapes `mission.py --known-failing`
    names: the module has come BACK (the entry now shadows a live module and
    can only confuse the unknown-module message), or nothing in the governed
    corpus references it any more (the entry outlives the thing it excused).

    Returns (stale, scanned, missing) -- the denominator is reported with the
    verdict so a shrunken population cannot look like a clean audit.
    """
    module_dir = os.path.join(repo, "curriculum", "modules")
    live = set()
    if os.path.isdir(module_dir):
        live = {os.path.splitext(n)[0] for n in os.listdir(module_dir)
                if n.endswith(".md")}
    paths, missing = governed_corpus(repo)
    referenced = set()
    for rel in paths:
        with open(os.path.join(repo, rel), encoding="utf-8") as handle:
            text = handle.read()
        for match in UNIT_REF.finditer(strip_noise(text)):
            referenced.add(match.group(1).rsplit("-", 1)[0])
    stale = []
    for mod in sorted(RETIRED_MODULES):
        if mod in live:
            stale.append((mod, "module %r is live again in "
                               "curriculum/modules, so the retirement entry"
                               " now shadows a governed module" % mod))
        elif mod not in referenced:
            stale.append((mod, "nothing in the governed corpus names a %s-NN"
                               " unit any more, so the entry excuses nothing"
                          % mod))
    return stale, len(paths), missing


def audit_retired(repo=REPO):
    stale, scanned, missing = stale_retired_modules(repo)
    for mod, why in stale:
        print("STALE %r is listed in check_unit_references.RETIRED_MODULES but"
              " %s. The set is a ratchet and may only shrink -- strike the"
              " entry." % (mod, why))
    if missing:
        print("NOTE %d governed artifact(s) are absent and were not scanned:"
              " %s" % (len(missing), ", ".join(sorted(missing)[:5])))
    print("%s retired-module audit: %d entr%s over %d governed file(s), %d"
          " stale" % ("FAIL" if stale else "PASS", len(RETIRED_MODULES),
                      "y" if len(RETIRED_MODULES) == 1 else "ies",
                      scanned, len(stale)))
    return 1 if stale else 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--audit-retired", action="store_true",
                        help="corpus-wide ratchet over RETIRED_MODULES")
    args = parser.parse_args(argv)
    if args.audit_retired:
        if args.paths:
            parser.error("--audit-retired derives its own population")
        return audit_retired()
    if not args.paths:
        parser.error("give one or more paths, or --audit-retired")
    failed = False
    checked = 0
    for path in args.paths:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        refs = unit_refs(text)
        checked += len(refs)
        modules = governed_modules()
        for uid in refs:
            module = uid.rsplit("-", 1)[0]
            if module not in modules:
                failed = True
                print("FAIL %s references %s with unknown module %s" % (
                    path, uid, module))
        for uid, absent in missing_references(text):
            failed = True
            print("FAIL %s references %s, missing %s" % (
                path, uid, ", ".join(absent)))
    print("%s checked %d cross-unit reference(s)" % (
        "FAIL" if failed else "PASS", checked))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
