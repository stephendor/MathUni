"""Compare explicit hypotheses around named results in sibling unit artifacts."""
import argparse
from html.parser import HTMLParser
import json
import os
import re
import sys

import yaml

QUALIFIERS = {
    "commutative": re.compile(r"\bcommutative\b", re.I),
    "finite": re.compile(r"\bfinite\b", re.I),
    "nonzero": re.compile(r"\bnon[- ]?zero\b", re.I),
    "nontrivial": re.compile(r"\bnon[- ]?trivial\b", re.I),
    "left": re.compile(r"\bleft[- ](?:R[- ]?)?(?:module|ideal)\b", re.I),
    "right": re.compile(r"\bright[- ](?:R[- ]?)?(?:module|ideal)\b", re.I),
    "integral domain": re.compile(r"\bintegral domain\b", re.I),
}
REF_PATTERN = re.compile(
    r"(Theorem|Definition|Lemma|Corollary|Proposition|Example)\s+"
    r"\d+[A-Za-z]?(?:\.\d+)*")
SCOPE = re.compile(
    r"^(?:let\b|assume\b|throughout\b|suppose\b|if\b|"
    r"for (?:a|an|every|any)\b)", re.I)
REF_PREFIX = re.compile(
    r"^(?:(?:Theorem|Definition|Lemma|Corollary|Proposition|Example)\s+"
    r"\d+[A-Za-z]?(?:\.\d+)*[.:]?\s*)", re.I)
DEFAULT_CONTRACTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "curriculum", "hypothesis-contracts.json")
SYLLABUS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "curriculum", "syllabus.yaml")


def registry_errors(units, contracts):
    return ["hypothesis contract names unknown unit %s" % unit
            for unit in sorted(set(contracts) - set(units))]


class Blocks(HTMLParser):
    BREAKS = {"p", "div", "li", "h1", "h2", "h3", "footer", "details"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style"}:
            self.hidden_depth += 1
        elif not self.hidden_depth and tag in self.BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1
        elif not self.hidden_depth and tag in self.BREAKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


def text_blocks(text, html=False):
    if html:
        parser = Blocks()
        parser.feed(text)
        text = "".join(parser.parts)
    return [re.sub(r"\s+", " ", block).strip()
            for block in re.split(r"\n\s*\n|\n", text) if block.strip()]


def result_contexts(text, html=False):
    blocks = text_blocks(text, html=html)
    out = {}
    for index, block in enumerate(blocks):
        refs = sorted({match.group(0) for match in REF_PATTERN.finditer(block)})
        if not refs:
            continue
        context = block
        for prior_block in reversed(blocks[max(0, index - 4):index]):
            if prior_block.startswith("##") or prior_block == "---":
                break
            prior = prior_block.lstrip("*_() abcdefg.:-")
            if SCOPE.search(prior):
                context = prior_block + " " + context
                break
        for ref in refs:
            out.setdefault(ref, []).append(context)
    return out


def positive_qualifiers(text):
    terms = set()
    for name, pattern in QUALIFIERS.items():
        for match in pattern.finditer(text):
            prefix = text[max(0, match.start() - 12):match.start()]
            if not re.search(r"(?:\bnot\s+|\bnon[- ]?)$", prefix, re.I):
                terms.add(name)
    return terms


def sentences(text):
    """Split prose without cutting result numbers or page abbreviations."""
    protected = re.sub(r"\b([Pp])\.", r"\1<DOT>", text)
    protected = re.sub(r"(?<=\d)\.(?=\d)", "<DOT>", protected)
    return [part.replace("<DOT>", ".") for part in
            re.split(r"(?<=[.!?])\s+", protected)]


def qualifiers(contexts):
    terms = set()
    for context in contexts:
        for sentence in re.split(r"(?<=[.!?])\s+", context):
            candidate = REF_PREFIX.sub(
                "", sentence.strip().lstrip("*_() abcdefg.:-"))
            if not SCOPE.search(candidate):
                continue
            positive = positive_qualifiers(candidate)
            terms.update(positive)
            for name, pattern in QUALIFIERS.items():
                for match in pattern.finditer(candidate):
                    prefix = candidate[max(0, match.start() - 12):match.start()]
                    if name not in positive and re.search(
                            r"(?:\bnot\s+|\bnon[- ]?)$", prefix, re.I):
                        terms.add("not " + name)
    return terms


def parity_errors(problem_text, lesson_text):
    problem = result_contexts(problem_text)
    lesson = result_contexts(lesson_text, html=True)
    errors = []
    for ref in sorted(set(problem) & set(lesson)):
        # Compare result statements/instructions, not incidental mentions in
        # surrounding discussion.  A problem may say "Suppose V is finite"
        # and later mention a prior theorem while explaining a different
        # claim; charging that scope to the mention creates false parity.
        direct = re.compile(
            r"^(?:(?:(?:let|assume|throughout|suppose|if)\b[^.!?]*?"
            r"(?:[.!?]\s+|\band\s+)))?(?:prove\s+)?%s\b"
            % re.escape(ref), re.I)

        def is_direct(context):
            candidate = re.sub(r"^[\s*_()\d.:-]+", "", context)
            return bool(direct.search(candidate))

        problem_contexts = [c for c in problem[ref] if is_direct(c)]
        lesson_contexts = [c for c in lesson[ref] if is_direct(c)]
        if not problem_contexts or not lesson_contexts:
            continue
        problem_terms = qualifiers(problem_contexts)
        lesson_terms = qualifiers(lesson_contexts)
        # The lesson is allowed to teach a theorem in a narrower setting than
        # a later exercise needs.  The dangerous direction is the reverse:
        # the set depends on a hypothesis that its supplying lesson omitted.
        if problem_terms - lesson_terms:
            errors.append((ref, problem_terms, lesson_terms))
    return errors


def contract_errors(problem_text, lesson_text, requirements):
    problem = result_contexts(problem_text)
    lesson = result_contexts(lesson_text, html=True)
    errors = []
    for ref, expected in sorted(requirements.items()):
        expected = set(expected)
        for artifact, contexts in (("set", problem), ("lesson", lesson)):
            if ref not in contexts:
                errors.append("%s missing named result %s" % (artifact, ref))
                continue
            scoped = []
            for context in contexts[ref]:
                context_sentences = sentences(context)
                for index, sentence in enumerate(context_sentences):
                    if ref not in sentence:
                        continue
                    parts = [sentence]
                    # HTML theorem labels commonly form a sentence of their
                    # own (`Corollary 9.11.</strong> Suppose ...`). Its actual
                    # statement is the next sentence, so keep that one too.
                    label = sentence.strip().rstrip(".")
                    if label.endswith(ref) and index + 1 < len(context_sentences):
                        parts.append(context_sentences[index + 1])
                    # A scope paragraph may explain why its standing
                    # hypothesis matters before the result appears. Search
                    # backward to the nearest explicit scope sentence, but
                    # never cross another named result.
                    for prior in reversed(context_sentences[:index]):
                        if REF_PATTERN.search(prior):
                            break
                        if SCOPE.search(prior.lstrip("*_() abcdefg.:-")):
                            parts.insert(0, prior)
                            break
                    scoped.append(" ".join(parts))
            joined = " ".join(scoped)
            found = positive_qualifiers(joined)
            missing = expected - found
            if missing:
                errors.append("%s %s missing hypotheses %s" % (
                    artifact, ref, sorted(missing)))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    parser.add_argument("--contracts", default=DEFAULT_CONTRACTS)
    parser.add_argument("--syllabus", default=SYLLABUS)
    parser.add_argument("problem_set_path")
    parser.add_argument("lesson_html_path")
    args = parser.parse_args(argv)
    with open(args.problem_set_path, encoding="utf-8") as handle:
        problem = handle.read()
    with open(args.lesson_html_path, encoding="utf-8") as handle:
        lesson = handle.read()
    with open(args.contracts, encoding="utf-8") as handle:
        contracts = json.load(handle)
    with open(args.syllabus, encoding="utf-8") as handle:
        units = {unit["id"] for unit in yaml.safe_load(handle)["units"]}
    errors = registry_errors(units, contracts)
    errors += contract_errors(problem, lesson, contracts.get(args.unit, {}))
    errors.extend(
        "%s differs: set=%s lesson=%s" %
        (ref, sorted(problem_terms), sorted(lesson_terms))
        for ref, problem_terms, lesson_terms in parity_errors(problem, lesson)
    )
    for error in errors:
        print("FAIL " + error)
    print("%s %d hypothesis parity error(s)" % (
        "FAIL" if errors else "PASS", len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
