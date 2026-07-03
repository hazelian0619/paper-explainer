# Paper Explainer

> A small faithfulness gate for AI-generated paper notes.

AI can write paper notes that look careful, cite specific evidence, and still
attach a claim to a quote the paper never said. That is the dangerous part: the
mistake looks scholarly.

`paper-explainer` turns those notes into checkable claim/quote pairs. Every
important claim needs a verbatim quote, and the checker verifies that the quote
is real, substantial enough to count as evidence, and optionally judged to
support the claim.

This is not another paper summarizer. It is the test step after an agent writes
paper notes.

## Why This Exists

Most AI paper tools optimize for fluent summaries. This project optimizes for a
more uncomfortable question:

> Can this note point to the exact sentence in the paper that makes it true?

That gives you a practical review loop:

1. Let an agent draft structured paper notes.
2. Extract the claims and their quoted evidence.
3. Run the faithfulness checker.
4. Fix unsupported cells before trusting or sharing the notes.

The value is not magic paper understanding. The value is making fabricated
evidence visible.

## 30-Second Demo

```bash
git clone https://github.com/hazelian0619/paper-explainer.git
cd paper-explainer
make demo
```

The demo contains one deliberately fake citation. A healthy run catches it:

```text
L1 quote-exists: 3 ok / 1 unsupported
  ⚠ [Table 7 · Fake citation demo] no source match (best ratio 0.33)
      claim: The method reaches 99 percent top-1 accuracy on ImageNet.
      quote: our method achieves 99% top-1 accuracy on the ImageNet benchmark
VERDICT: REVIEW NEEDED
```

That is the core promise: plausible unsupported evidence should fail loudly.

For a passing example:

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected:

```text
L1 quote-exists: 4 ok / 0 unsupported
VERDICT: PASS
```

## What You Get

- A deterministic offline L1 checker with zero runtime dependencies.
- A quote quality guard that rejects tiny non-evidence quotes like `"The"`.
- A fuzzy source-match check for fabricated quotes.
- Optional `--strict` mode for judging whether a real quote supports its claim.
- Agent-facing instructions for Claude Code, Codex, Cursor, Copilot, and other
  `AGENTS.md`-aware tools.
- Runnable failing and passing examples.
- CI that runs tests and the fake-citation demo.

## How It Works

`paper-explainer` checks claim/quote pairs:

- **claim:** what the note says about the paper
- **quote:** the exact source text that supports that claim

The checker has three gates:

| Gate | Default? | Catches | How |
|---|---:|---|---|
| Quote quality | Yes | Tiny, non-evidence quotes such as `"The"` | Minimum quote length/token guard |
| Quote exists | Yes | Fabricated quotes that do not appear in the source | Offline fuzzy matching with Python standard library |
| Quote supports claim | Optional | Real quotes attached to the wrong claim | LLM judge via `--strict` |

Default L1 is local, deterministic, and dependency-free. Strict mode is
optional because it makes model calls and needs `ANTHROPIC_API_KEY`.

## Manual Usage

Create a JSON file of claim/quote pairs:

```json
[
  {
    "table": "Table 1",
    "cell": "Core problem",
    "claim": "Robots integrate multimodal perception to make HRI decisions.",
    "quote": "how robots integrate multimodal perception from vision, language, and touch to make decisions in human-robot interaction"
  }
]
```

Run the checker against the source text:

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables claims.json \
  --source paper.txt
```

Exit codes:

| Code | Meaning |
|---:|---|
| 0 | All checked claims passed |
| 1 | At least one claim needs review |
| 2 | Input or setup error |

Useful options:

```bash
--json                  Emit machine-readable results
--threshold 0.85        Tune fuzzy quote matching
--min-quote-chars 20    Reject quotes with too little text
--min-quote-tokens 4    Reject quotes with too few tokens
--strict                Add L2 support judging
```

By default, a quote passes the quality guard if it has at least 20 non-space
characters or at least 4 tokens. You can tune those thresholds for specialized
notes, but the default blocks trivial evidence like `"The"`.

## Agent Skill Workflow

The repo also packages the workflow as an agent skill:

| Environment | Entry Point |
|---|---|
| Claude Code / claude.ai / Agent SDK | `skills/paper-explainer/SKILL.md` |
| Codex / Cursor / Copilot / AGENTS.md-aware tools | `AGENTS.md` |
| Plain CLI | `skills/paper-explainer/scripts/check_sources.py` |

The intended workflow:

1. Extract or receive the paper source text.
2. Fill a concept map before writing full paper notes.
3. Attach a verbatim quote to every evidence-bearing claim.
4. Run the checker.
5. Repair flagged cells or mark them missing.

## When To Use It

Use this when you want to:

- review AI-generated literature notes
- prepare notes for paper discussion or reproduction
- catch fabricated evidence before sharing a summary
- make an agent's paper-reading workflow more auditable
- keep a lightweight local check instead of adopting a full paper platform

Do not use it as:

- a full PDF parser
- a paper search engine
- a web app
- a Notion exporter
- an embedding or RAG framework
- a guarantee that the whole paper was summarized completely

## Known Limits

This project verifies the evidence attached to claims. It does not verify
claims that have no quote, source text you did not provide, PDF extraction
quality, or whether every important point in the paper was captured.

That boundary is intentional. The project stays small so the core check remains
easy to run, inspect, and trust.

## Development

```bash
make test
make demo
make validate-skill
```

CI runs tests and the fake-citation demo on Python 3.11 and 3.12.

## Roadmap

- More worked examples across ML, systems, and biomedical papers.
- A single `make check` command for all local verification.
- Batch and cache support for `--strict`.
- Optional source-fetch helpers for arXiv-style inputs.
- Stronger table-to-claim extraction.

## License

MIT.
