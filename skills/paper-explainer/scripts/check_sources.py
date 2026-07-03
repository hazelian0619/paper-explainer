#!/usr/bin/env python3
"""Faithfulness checker for paper-explainer tables.

The central failure mode of LLM paper summaries is *fabricated evidence*: the
model attaches a plausible-sounding quote to a claim, but the paper never
actually says it. This script defends against that in two layers:

  L1 (default, offline, deterministic)
      Every claim carries a verbatim quote. L1 checks that the quote actually
      EXISTS in the source text, using normalized fuzzy matching (difflib,
      standard library only). A fabricated quote will not match -> flagged
      `unsupported`. Very short quotes are flagged `invalid_quote` because they
      are too easy to attach to an overbroad claim. This layer needs no API key
      and no network.

  L2 (--strict, one LLM call per surviving claim)
      A real quote can still be attached to the WRONG claim ("citation
      swapping"). L2 asks an LLM judge whether each quote actually SUPPORTS the
      claim it is attached to. Requires ANTHROPIC_API_KEY.

Deliberately NOT implemented: embedding / semantic paraphrase matching. It only
makes L1 more lenient about wording without catching a new class of error, and
it adds a heavy dependency. See README "Known Limits".

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
DEFAULT_MIN_QUOTE_CHARS = 20
DEFAULT_MIN_QUOTE_TOKENS = 4
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


def quote_token_count(quote_norm: str) -> int:
    """Count evidence-bearing tokens across spaced and CJK text."""
    return len(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", quote_norm))


def quote_quality_issue(
    quote: str,
    min_chars: int,
    min_tokens: int,
) -> str:
    """Return a reason when a quote is too short to be useful evidence."""
    quote_norm = normalize(quote)
    char_count = len(re.sub(r"\s+", "", quote_norm))
    token_count = quote_token_count(quote_norm)
    if char_count >= min_chars or token_count >= min_tokens:
        return ""
    return (
        f"quote too short ({char_count} chars, {token_count} tokens; "
        f"need >= {min_chars} chars or >= {min_tokens} tokens)"
    )


@dataclass
class ClaimResult:
    table: str
    cell: str
    claim: str
    quote: str
    status: str            # "ok" | "unsupported" | "invalid_quote" | "skipped"
    ratio: float = 0.0
    issue: str = ""
    l2_supports: bool | None = None
    l2_reason: str = ""
    l2_error: bool = False


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
    def invalid_quotes(self) -> list[ClaimResult]:
        return [r for r in self.results if r.status == "invalid_quote"]

    @property
    def citation_swaps(self) -> list[ClaimResult]:
        return [r for r in self.results if r.l2_supports is False]

    @property
    def l2_errors(self) -> list[ClaimResult]:
        return [r for r in self.results if r.l2_error]


def run_l1(
    claims: list[dict],
    source: str,
    threshold: float,
    min_quote_chars: int = DEFAULT_MIN_QUOTE_CHARS,
    min_quote_tokens: int = DEFAULT_MIN_QUOTE_TOKENS,
) -> Report:
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

        issue = quote_quality_issue(quote, min_quote_chars, min_quote_tokens)
        if issue:
            report.results.append(
                ClaimResult(table, cell, claim, quote, "invalid_quote", issue=issue)
            )
            continue

        ratio = best_window_ratio(normalize(quote), source_norm)
        status = "ok" if ratio >= threshold else "unsupported"
        report.results.append(
            ClaimResult(table, cell, claim, quote, status, ratio=ratio)
        )
    return report


def parse_l2_verdict(raw: str) -> tuple[bool, str]:
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    verdict = json.loads(raw)
    if not isinstance(verdict, dict):
        raise ValueError("judge response must be a JSON object")
    supports = verdict.get("supports")
    if not isinstance(supports, bool):
        raise ValueError("judge response field 'supports' must be boolean")
    reason = str(verdict.get("reason", ""))[:120]
    return supports, reason


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
        r.l2_supports = None
        r.l2_reason = ""
        r.l2_error = False
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
            supports, reason = parse_l2_verdict(raw)
            r.l2_supports = supports
            r.l2_reason = reason
        except Exception as e:  # network / parse — report, don't crash the run
            r.l2_supports = None
            r.l2_error = True
            r.l2_reason = f"judge error: {e}"


def print_report(report: Report, strict: bool) -> None:
    checked = report.checked
    total = len(checked)
    unsupported = report.unsupported
    invalid = report.invalid_quotes
    ok = total - len(unsupported) - len(invalid)

    print("=" * 60)
    print("FAITHFULNESS REPORT")
    print("=" * 60)
    print(f"Claims checked : {total}   (skipped/empty: "
          f"{len(report.results) - total})")
    print(f"L1 quote-exists: {ok} ok / {len(unsupported)} unsupported")
    if invalid:
        print(f"L1 quote quality: {len(invalid)} invalid")

    for r in invalid:
        print(f"  ⚠ [{r.table} · {r.cell}] invalid quote")
        print(f"      reason: {r.issue}")
        print(f"      claim: {r.claim[:70]}")
        print(f"      quote: {r.quote[:70]}")

    for r in unsupported:
        print(f"  ⚠ [{r.table} · {r.cell}] no source match "
              f"(best ratio {r.ratio:.2f})")
        print(f"      claim: {r.claim[:70]}")
        print(f"      quote: {r.quote[:70]}")

    if strict:
        swaps = report.citation_swaps
        errors = report.l2_errors
        supported = [r for r in checked if r.l2_supports is True]
        print(f"L2 supports    : {len(supported)} supported / {len(swaps)} "
              f"citation-swap / {len(errors)} judge-error")
        for r in swaps:
            print(f"  ⚠ [{r.table} · {r.cell}] quote real but does not support claim")
            print(f"      reason: {r.l2_reason}")
        for r in errors:
            print(f"  ⚠ [{r.table} · {r.cell}] L2 judge error")
            print(f"      reason: {r.l2_reason}")

    print("-" * 60)
    verdict = "PASS" if not unsupported and not invalid and not (
        strict and (report.citation_swaps or report.l2_errors)
    ) else "REVIEW NEEDED"
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
    p.add_argument("--min-quote-chars", type=int, default=DEFAULT_MIN_QUOTE_CHARS,
                   help="Minimum non-space quote characters before L1 matching "
                        f"(default {DEFAULT_MIN_QUOTE_CHARS}).")
    p.add_argument("--min-quote-tokens", type=int, default=DEFAULT_MIN_QUOTE_TOKENS,
                   help="Minimum quote tokens before L1 matching "
                        f"(default {DEFAULT_MIN_QUOTE_TOKENS}).")
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

    report = run_l1(
        claims,
        source,
        args.threshold,
        min_quote_chars=args.min_quote_chars,
        min_quote_tokens=args.min_quote_tokens,
    )
    if args.strict:
        run_l2(report, args.model)

    if args.json:
        print(json.dumps(
            [r.__dict__ for r in report.results], ensure_ascii=False, indent=2))
    else:
        print_report(report, args.strict)

    # Non-zero exit when anything needs review — useful in CI / pre-commit.
    needs_review = report.unsupported or report.invalid_quotes or (
        args.strict and (report.citation_swaps or report.l2_errors)
    )
    return 1 if needs_review else 0


if __name__ == "__main__":
    raise SystemExit(main())
