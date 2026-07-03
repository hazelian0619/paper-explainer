# Paper Explainer

> Turn AI paper notes into checkable, source-grounded claims.

AI paper summaries can sound confident while citing evidence the paper never
said. `paper-explainer` is a small faithfulness gate for that failure mode: an
agent writes structured paper notes, then this checker verifies that every
important claim is backed by a real verbatim quote from the source text.

It is not a paper reader, PDF parser, or summarizer. It is the test step after
an agent writes paper notes.

## 30-Second Demo

```bash
git clone https://github.com/hazelian0619/paper-explainer.git
cd paper-explainer
make demo
```

The demo contains one deliberately fake citation. A healthy run prints:

```text
L1 quote-exists: 3 ok / 1 unsupported
  ⚠ [Table 7 · Fake citation demo] no source match (best ratio 0.33)
      claim: The method reaches 99 percent top-1 accuracy on ImageNet.
      quote: our method achieves 99% top-1 accuracy on the ImageNet benchmark
VERDICT: REVIEW NEEDED
```

That is the point: unsupported evidence should fail loudly.

For a clean path, run:

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

## What It Checks

`paper-explainer` checks claim/quote pairs. Each pair says:

- **claim:** what the note says about the paper
- **quote:** the exact source text that supports that claim

The checker has two layers:

| Layer | Default? | Catches | How |
|---|---:|---|---|
| L1 quote quality | Yes | Tiny, non-evidence quotes such as `"The"` | Minimum quote length/token guard |
| L1 quote exists | Yes | Fabricated quotes that do not appear in the source | Offline fuzzy matching with Python standard library |
| L2 support judge | Optional | Real quotes attached to the wrong claim | LLM judge via `--strict` |

Default L1 is deterministic, offline, and dependency-free. L2 is optional
because it makes model calls and needs `ANTHROPIC_API_KEY`.

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

## Known Limits

This project intentionally stays small.

It does verify:

- whether a quote is long enough to be useful evidence
- whether a quote appears in the provided source text
- whether strict-mode judge responses are valid and review-needed on failure
- whether optional L2 thinks a real quote supports its claim

It does not verify:

- claims that have no quote
- source text you did not provide
- PDF extraction quality
- whether the whole paper was summarized well
- whether every important claim in the paper was captured

It also avoids heavy scope:

- no web app
- no Notion exporter
- no embedding or RAG framework
- no paper library manager
- no one-click PDF understanding pipeline

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
