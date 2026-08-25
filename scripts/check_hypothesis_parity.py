"""Compare explicit hypotheses around named results in sibling unit artifacts."""
import argparse
from html.parser import HTMLParser
import json
import os
import re
import sys

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


class Blocks(HTMLParser):
    BREAKS = {"p", "div", "li", "h1", "h2", "h3", "footer", "details"}

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BREAKS:
            self.parts.append("\n")

    def handle_data(self, data):
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


def qualifiers(contexts):
    terms = set()
    for context in contexts:
        for sentence in re.split(r"(?<=[.!?])\s+", context):
            candidate = REF_PREFIX.sub(
                "", sentence.strip().lstrip("*_() abcdefg.:-"))
            if not SCOPE.search(candidate):
                continue
            terms.update(name for name, pattern in QUALIFIERS.items()
                         if pattern.search(candidate))
    return terms


def parity_errors(problem_text, lesson_text):
    problem = result_contexts(problem_text)
    lesson = result_contexts(lesson_text, html=True)
    errors = []
    for ref in sorted(set(problem) & set(lesson)):
        problem_terms = qualifiers(problem[ref])
        lesson_terms = qualifiers(lesson[ref])
        if problem_terms != lesson_terms:
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
            joined = " ".join(contexts[ref])
            found = {name for name, pattern in QUALIFIERS.items()
                     if pattern.search(joined)}
            missing = expected - found
            if missing:
                errors.append("%s %s missing hypotheses %s" % (
                    artifact, ref, sorted(missing)))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    parser.add_argument("--contracts", default=DEFAULT_CONTRACTS)
    parser.add_argument("problem_set_path")
    parser.add_argument("lesson_html_path")
    args = parser.parse_args(argv)
    with open(args.problem_set_path, encoding="utf-8") as handle:
        problem = handle.read()
    with open(args.lesson_html_path, encoding="utf-8") as handle:
        lesson = handle.read()
    with open(args.contracts, encoding="utf-8") as handle:
        contracts = json.load(handle)
    errors = contract_errors(problem, lesson, contracts.get(args.unit, {}))
    for error in errors:
        print("FAIL " + error)
    print("%s %d contracted hypothesis error(s)" % (
        "FAIL" if errors else "PASS", len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
