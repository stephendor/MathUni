"""prose_universals.py — ADVISORY. Flag unhedged universals in uncited prose.

Not a gate. Exit code is 0 whatever it finds, it is not in `unit-gates.json`,
and it is not in CI. Read it while authoring; nothing is blocked on it.

Why it exists
-------------
Across two CodeRabbit rounds on the `s3-content` branch — 16 findings on 7 units
— the single largest defect category was the unhedged universal quantifier in
*explanatory* prose: a sentence that cites no theorem, and so is touched by none
of the eight gates. Four were false at a boundary the author had not pictured:

  * "uncountable for any space with more than one point" — a discrete space on
    m points has exactly m singular n-simplices, since the standard n-simplex
    is connected;
  * "no constraint on a space is visible in the mere isomorphism type of its
    fundamental group" — Hatcher's Corollary 1.28 constrains the class of
    2-complexes;
  * the torus-knot centre claim, false at m = 1 or n = 1, where Hatcher states
    the hypothesis m, n > 1 explicitly on the cited page;
  * and — the strongest of the four — a *correction* written in the previous
    round, asserting that Z/2 torsion is invisible to an F_2 barcode. It is
    not: H_*(RP^2; F_2) = (F_2, F_2, F_2), and what is lost is only that the
    class is torsion.

The gates check structure, citation presence, tag balance and mission-strip
fidelity. None checks whether a sentence is TRUE, and prose that cites nothing
has no denominator to be checked against. Rescoping a claim is not a licence to
assert; a correction inherits exactly the lack of defence that produced the
error it replaces.

Why advisory and not a gate
---------------------------
A regex over these quantifiers is cheap and IS very noisy. Measured on the
corpus at introduction (2026-09-09): **3,574 flagged sentences across 145
lessons, a mean of 24.6 per lesson and a maximum of 54** (an2-06). Four of
those thousands are the known-false ones below. That ratio is the whole
argument for the tool's status: it is a reading order, not a defect list, and
a blocking gate at this precision would be a demand to rewrite the corpus. The corpus
uses hedged universals correctly and often — "usually uncountable" is right
where it appears — and this tool cannot tell a true universal from a false one.
It ranks sentences for a human to check; it does not judge them. Making it
blocking would train the author to phrase around it, which is worse than
nothing: the sentence would stop matching and stay false.

What it asks you to do
----------------------
For each flagged sentence, run the standard degenerate list and either name the
boundary case in the sentence or hedge it:

    empty · one point · finite / discrete · trivial group · exponent or
    index 1 · characteristic 2

Where the SOURCE carries the hypothesis and the lesson dropped it, that is a
gate-2 source read-back failure, not a judgement call — see
`curriculum/LESSON-GUIDE.md §Source read-back`.

  python scripts/prose_universals.py <lesson_html_path> [...]
  python scripts/prose_universals.py --selftest

Exit 0 always (2 on usage error, 1 only from --selftest).
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from scripts.citations import rendered_text, sentence_breaks  # noqa: E402

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# The quantifiers the observation names, plus the negative forms that carry the
# same universal force. "must" and "only" are deliberately absent: they are
# overwhelmingly deontic or restrictive in this corpus and flagging them buries
# the rest.
UNIVERSAL = re.compile(
    r"(?<![\w-])(every|any|all|no|none|always|never|cannot|can't|"
    r"nothing|nowhere|impossible|arbitrary)(?![\w-])", re.I)

# A hedge anywhere in the sentence means the author has already signalled that
# the claim is typical rather than universal. "usually uncountable" is correct
# where it appears twice in the corpus, and flagging it is how an advisory
# becomes ignored.
HEDGE = re.compile(
    r"(?<![\w-])(usually|typically|often|generally|in general|mostly|"
    r"commonly|normally|as a rule|for most|almost all|almost every|"
    r"tends? to|need not|not necessarily|in practice|roughly|broadly|"
    r"here|in this case|on this sample|for these)(?![\w-])", re.I)

# There is NO third filter for "the sentence already names its boundary case",
# and the attempt to write one is worth recording, because it failed against
# this file's own negative controls in the dangerous direction.
#
# The obvious rule — suppress a sentence containing "empty", "trivial",
# "discrete", "finite", "infinite", "one point", "more than one" — suppressed
# NC1 ("uncountable for any space with more than one point") on "more than one
# point" and NC3 ("always the infinite cyclic subgroup") on "infinite". Both
# are false. Naming a degenerate word is not evidence that the author checked
# the degenerate case; in NC1 the named boundary IS where the claim breaks, and
# the words are ordinary mathematical vocabulary besides.
#
# Restricting it to a leading hypothesis frame ("For any space with more than
# one point, ...") fails identically, since that is a paraphrase of NC1.
#
# So a correct sentence that states its hypothesis — "for nontrivial m and n
# the centre is always infinite cyclic" — is flagged here, and that is the
# tool's noise floor, stated rather than engineered away. An advisory may cost
# a reader a second look. A filter that hides a false universal costs more.

# The sentence cites something, so gate 2 has a denominator for it and it is
# not this tool's population. Matches "Theorem 1.2", "p. 43", "§3.1", "(Hatcher
# 1.28)" and the class="cite" spans the footer uses.
CITED = re.compile(
    r"(?<![\w-])(Theorem|Lemma|Proposition|Corollary|Definition|Example|"
    r"Exercise|Notation|Remark|Axiom|Fact|Principle)s?\s+\d"
    r"|§\s*\d|(?<![\w-])pp?\.\s*\d", re.I)

DEGENERATE = ("empty", "one point", "finite / discrete", "trivial group",
              "exponent or index 1", "characteristic 2")


def sentences(text):
    """Rendered prose, split on real sentence boundaries."""
    out, cursor = [], 0
    for match in sentence_breaks(text):
        out.append(text[cursor:match.start() + 1].strip())
        cursor = match.end()
    tail = text[cursor:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]


def flags(html):
    """[(sentence, [quantifiers])] — uncited and unhedged.

    Two filters, each of which removes a class this tool has nothing useful
    to say about:

      * CITED — gate 2 already has a denominator for the sentence;
      * HEDGE — the author has already marked the claim as typical.

    There is deliberately no "already names its boundary" filter; see the note
    on the missing BOUNDARY pattern above for the two negative controls that
    ruled it out.
    """
    text = re.sub(r"\s+", " ", rendered_text(html))
    out = []
    for sentence in sentences(text):
        words = UNIVERSAL.findall(sentence)
        if not words:
            continue
        if CITED.search(sentence) or HEDGE.search(sentence):
            continue
        out.append((sentence, sorted({w.lower() for w in words})))
    return out


def report(path):
    with open(path, encoding="utf-8") as handle:
        found = flags(handle.read())
    print("%s — %d unhedged universal(s) in uncited prose" % (path, len(found)))
    for sentence, words in found:
        print("\n  [%s] %s" % (", ".join(words),
                               sentence if len(sentence) <= 300
                               else sentence[:297] + "..."))
    if found:
        print("\n  Check each against: %s." % " · ".join(DEGENERATE))
        print("  Name the boundary in the sentence, or hedge it. Where the"
              " source carries\n  the hypothesis, dropping it is a gate-2"
              " read-back failure, not a judgement call.")
    return len(found)


def selftest():
    total, fails = [0], []

    def check_one(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    def flagged(sentence):
        return bool(flags("<p>%s</p>" % sentence))

    # --- the negative-control corpus ------------------------------------
    # Four sentences confirmed false in review. Each must be flagged; if a
    # later refinement stops flagging one, that is a regression and this fails.
    check_one("NC1 — 'uncountable for any space with more than one point'"
              " (false: a discrete space on m points has m singular"
              " n-simplices)",
              flagged("The singular chain group is uncountable for any space"
                      " with more than one point."))
    check_one("NC2 — 'no constraint ... visible in the isomorphism type'"
              " (false: Corollary 1.28 constrains the class of 2-complexes)",
              flagged("There is no constraint on a space visible in the mere"
                      " isomorphism type of its fundamental group."))
    check_one("NC3 — the torus-knot centre claim (false at m = 1 or n = 1,"
              " and the source states m, n > 1 on the cited page)",
              flagged("The centre of the torus-knot group is always the"
                      " infinite cyclic subgroup generated by that element."))
    check_one("NC4 — the correction that was itself false (H_*(RP^2; F_2)"
              " is (F_2, F_2, F_2); only torsion-ness is lost)",
              flagged("Z/2 torsion is never visible to a barcode computed"
                      " over F_2."))

    # --- hedged and bounded uses must stay quiet ------------------------
    # An advisory that fires on correct prose is an advisory nobody reads.
    check_one("a hedged universal is not flagged",
              not flagged("The singular chain group is usually uncountable."))
    check_one("...nor one whose sentence carries a citation",
              not flagged("By Theorem 1.28 no 2-complex has that group."))
    check_one("...nor one citing a page",
              not flagged("Munkres never assumes Hausdorff here, p. 43."))
    # The noise floor, pinned so it is a stated cost and not a surprise: a
    # CORRECT sentence that states its hypothesis is still flagged, because no
    # rule separates "names the boundary" from "was checked at the boundary"
    # without also hiding NC1 and NC3.
    check_one("a correct sentence stating its hypothesis is flagged anyway"
              " (the stated noise floor)",
              flagged("For nontrivial m and n the centre is always infinite"
                      " cyclic."))
    check_one("a sentence with no universal at all is not flagged",
              not flagged("The barcode has six bars."))

    # --- boundaries of the matcher --------------------------------------
    check_one("'any' inside a word is not a match",
              not flagged("The company of maps is a functor."))
    check_one("'no' inside a hyphenated word is not a match",
              not flagged("The no-op map is the identity."))
    check_one("...while a real 'no' is",
              flagged("There is no such map."))
    check_one("the quantifiers found are reported, deduplicated and sorted",
              flags("<p>No space is never both, and no map is.</p>")[0][1]
              == ["never", "no"])
    check_one("script contents are not prose",
              not flags("<script>var s = 'every point is fixed.';</script>"))
    check_one("a sentence is not split at 'p. 43'",
              len(sentences("Read p. 43. Then continue.")) == 2)

    # --- the limit, stated ----------------------------------------------
    # The fifth review finding — "Example 1.25 violates the neighbourhood
    # hypothesis", where the hypothesis in fact holds and the shrinking wedge
    # is simply not the wedge sum — carries no universal quantifier and is a
    # misreading of the source, not an over-claim. This tool cannot see it,
    # and pinning that here keeps the claim honest rather than implied.
    check_one("a misread source with no universal is OUT of scope (stated)",
              not flagged("Example 1.25 violates the neighbourhood"
                          " hypothesis."))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    if not argv:
        print("usage: prose_universals.py <lesson_html_path> [...]"
              " | --selftest")
        return 2
    total = 0
    for path in argv:
        total += report(path)
        print("")
    print("ADVISORY %d sentence(s) across %d file(s). This is not a gate and"
          " nothing is blocked on it." % (total, len(argv)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
