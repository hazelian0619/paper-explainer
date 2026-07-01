#!/usr/bin/env python3
"""Faithfulness checker for paper-explainer tables.

The central failure mode of LLM paper summaries is *fabricated evidence*: the
model attaches a plausible-sounding quote to a claim, but the paper never
actually says it. This script defends against that in two layers:

  L1 (default, offline, deterministic)
      Every claim carries a verbatim quote. L1 checks that the quote actually
      EXISTS in the source text, using normalized fuzzy matching (difflib,
      standard library only). A fabricated quote will not match -> flagged
      `unsupported`. This layer needs no API key and no network.

  L2 (--strict, one LLM call per surviving claim)
      A real quote can still be attached to the WRONG claim ("citation
      swapping"). L2 asks an LLM judge whether each quote actually SUPPORTS the
      claim it is attached to. Requires ANTHROPIC_API_KEY.

Deliberately NOT implemented: embedding / semantic paraphrase matching. It only
makes L1 more lenient about wording without catching a new class of error, and
it adds a heavy dependency. See README "Why no embeddings".

Input JSON shape (a list of claim objects):

  [
    {"table": "表1", "cell": "核心问题", "claim": "...", "quote": "verbatim ..."},
    ...
  ]

Cells with quote == "" or "缺失" are treated as intentionally-empty and skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher

# Quotes at/above this normalized similarity to some window of the source are
# considered "present in the source". 0.85 tolerates minor OCR/whitespace/quote
# -char drift while still rejecting invented text.
DEFAULT_THRESHOLD = 0.85
MISSING_MARKERS = {"", "缺失", "missing", "n/a", "na", "-", "—"}


def normalize(text: str) -> str:
    """Lowercase, unify quotes/dashes, collapse whitespace.

    Matching should be robust to formatting noise (PDF extraction inserts stray
    newlines, curly vs straight quotes, etc.) but NOT to invented content.
    """
    text = text.lower()
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def best_window_ratio(quote_norm: str, source_norm: str) -> float:
    """Best similarity between the quote and any same-length window of source.

    A fabricated quote shares no long contiguous run with the source, so its
    best-window ratio stays low. A real quote (even with minor drift) aligns to
    some window at high ratio. We anchor the search on the longest common
    substring so this stays fast on paper-length sources.
    """
    if not quote_norm:
        return 0.0
    if quote_norm in source_norm:
        return 1.0

    matcher = SequenceMatcher(None, quote_norm, source_norm, autojunk=False)
    # Longest block of the quote that appears verbatim in the source.
    block = matcher.find_longest_match(0, len(quote_norm), 0, len(source_norm))
    if block.size == 0:
        return 0.0

    qlen = len(quote_norm)
    # Center a quote-length window on the matched region and score the overlap.
    start = max(0, block.b - block.a)
    end = min(len(source_norm), start + qlen)
    start = max(0, end - qlen)
    window = source_norm[start:end]
    return SequenceMatcher(None, quote_norm, window, autojunk=False).ratio()


@dataclass
class ClaimResult:
    table: str
    cell: str
    claim: str
    quote: str
    status: str            # "ok" | "unsupported" | "skipped"
    ratio: float = 0.0
    l2_supports: bool | None = None
    l2_reason: str = ""


@dataclass
class Report:
    results: list[ClaimResult] = field(default_factory=list)

    @property
    def checked(self) -> list[ClaimResult]:
        return [r for r in self.results if r.status != "skipped"]

    @property
    def unsupported(self) -> list[ClaimResult]:
        return [r for r in self.results if r.status == "unsupported"]

    @property
    def citation_swaps(self) -> list[ClaimResult]:
        return [r for r in self.results if r.l2_supports is False]


def run_l1(claims: list[dict], source: str, threshold: float) -> Report:
    """L1: does each quote actually exist in the source?"""
    source_norm = normalize(source)
    report = Report()
    for c in claims:
        quote = (c.get("quote") or "").strip()
        claim = (c.get("claim") or "").strip()
        table = c.get("table", "?")
        cell = c.get("cell", "?")

        if quote.lower() in MISSING_MARKERS or not claim:
            report.results.append(
                ClaimResult(table, cell, claim, quote, "skipped")
            )
            continue

        ratio = best_window_ratio(normalize(quote), source_norm)
        status = "ok" if ratio >= threshold else "unsupported"
        report.results.append(
            ClaimResult(table, cell, claim, quote, status, ratio=ratio)
        )
    return report


def run_l2(report: Report, model: str) -> None:
    """L2 (--strict): does each real quote actually support its claim?

    Mutates `report` in place. Only claims that passed L1 are judged — there is
    no point asking whether a fabricated quote supports anything.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        sys.stderr.write(
            "[--strict] requires the `anthropic` package: pip install anthropic\n"
        )
        sys.exit(2)

    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    for r in report.results:
        if r.status != "ok":
            continue
        prompt = (
            "You are checking whether a quote supports a claim.\n\n"
            f"CLAIM: {r.claim}\n"
            f"QUOTE (from the paper): {r.quote}\n\n"
            "Does the QUOTE provide direct support for the CLAIM? Answer strictly "
            'as JSON: {"supports": true|false, "reason": "<=15 words"}.'
        )
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
            verdict = json.loads(raw)
            r.l2_supports = bool(verdict.get("supports"))
            r.l2_reason = str(verdict.get("reason", ""))[:120]
        except Exception as e:  # network / parse — report, don't crash the run
            r.l2_supports = None
            r.l2_reason = f"judge error: {e}"


def print_report(report: Report, strict: bool) -> None:
    checked = report.checked
    total = len(checked)
    unsupported = report.unsupported
    ok = total - len(unsupported)

    print("=" * 60)
    print("FAITHFULNESS REPORT")
    print("=" * 60)
    print(f"Claims checked : {total}   (skipped/empty: "
          f"{len(report.results) - total})")
    print(f"L1 quote-exists: {ok} ok / {len(unsupported)} unsupported")

    for r in unsupported:
        print(f"  ⚠ [{r.table} · {r.cell}] no source match "
              f"(best ratio {r.ratio:.2f})")
        print(f"      claim: {r.claim[:70]}")
        print(f"      quote: {r.quote[:70]}")

    if strict:
        swaps = report.citation_swaps
        judged = [r for r in checked if r.l2_supports is not None or r.status == "ok"]
        print(f"L2 supports    : {len([r for r in checked if r.l2_supports])} "
              f"supported / {len(swaps)} citation-swap")
        for r in swaps:
            print(f"  ⚠ [{r.table} · {r.cell}] quote real but does not support claim")
            print(f"      reason: {r.l2_reason}")

    print("-" * 60)
    verdict = "PASS" if not unsupported and not (strict and report.citation_swaps) \
        else "REVIEW NEEDED"
    print(f"VERDICT: {verdict}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Verify that paper-explainer table quotes are grounded in the source.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--tables", required=True,
                   help="JSON file: list of {table, cell, claim, quote} objects.")
    p.add_argument("--source", required=True,
                   help="Plain-text file of the paper (the text quotes are checked against).")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help=f"L1 match threshold 0-1 (default {DEFAULT_THRESHOLD}).")
    p.add_argument("--strict", action="store_true",
                   help="Also run L2 LLM support-judge (needs ANTHROPIC_API_KEY).")
    p.add_argument("--model", default="claude-opus-4-8",
                   help="Model for --strict (default claude-opus-4-8).")
    p.add_argument("--json", action="store_true",
                   help="Emit the report as JSON instead of text.")
    args = p.parse_args(argv)

    try:
        with open(args.tables, encoding="utf-8") as f:
            claims = json.load(f)
        with open(args.source, encoding="utf-8") as f:
            source = f.read()
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"error reading input: {e}\n")
        return 2

    if not isinstance(claims, list):
        sys.stderr.write("--tables must contain a JSON list of claim objects.\n")
        return 2

    report = run_l1(claims, source, args.threshold)
    if args.strict:
        run_l2(report, args.model)

    if args.json:
        print(json.dumps(
            [r.__dict__ for r in report.results], ensure_ascii=False, indent=2))
    else:
        print_report(report, args.strict)

    # Non-zero exit when anything needs review — useful in CI / pre-commit.
    needs_review = report.unsupported or (args.strict and report.citation_swaps)
    return 1 if needs_review else 0


if __name__ == "__main__":
    raise SystemExit(main())
