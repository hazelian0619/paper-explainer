# Paper Explainer

> Turn AI paper notes into checkable claims.

AI-generated paper summaries often sound grounded while attaching claims to quotes the paper never said. `paper-explainer` is a small faithfulness gate for paper notes: every important claim must carry a verbatim quote, and the checker verifies whether that quote appears in the source text.

It is not another paper summarizer. It is the test step after an agent writes paper notes.

## 30-second demo

```bash
git clone https://github.com/hazelian0619/paper-explainer.git
cd paper-explainer
make demo
```

The demo intentionally includes one fake citation:

```text
L1 quote-exists: 3 ok / 1 unsupported
  ⚠ [Table 7 · Fake citation demo] no source match (best ratio 0.33)
      claim: The method reaches 99 percent top-1 accuracy on ImageNet.
      quote: our method achieves 99% top-1 accuracy on the ImageNet benchmark
VERDICT: REVIEW NEEDED
```

That is the point: plausible unsupported evidence should fail loudly.

## What it checks

`paper-explainer` uses two layers:

| Layer | What it catches | How it works | Cost |
|---|---|---|---|
| L1 default | A model invented a quote that is not in the source | Standard-library normalized fuzzy matching | Offline, deterministic, zero dependencies |
| L2 `--strict` | A real quote is attached to the wrong claim | LLM judge over the claim/quote pair | Optional model calls |

L1 is deliberately strict about evidence text. If the quote is a paraphrase, the checker should flag it, because the workflow requires verbatim evidence.

## Manual usage

Prepare a JSON list of claim/quote pairs:

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

Run:

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

For a passing example, see `examples/real-paper-demo/`.
For a failing example, see `examples/mini-fake-citation/`.

## Agent skill workflow

The repo also packages the workflow as an agent skill:

| Environment | Entry point |
|---|---|
| Claude Code / claude.ai / Agent SDK | `skills/paper-explainer/SKILL.md` |
| Codex / Cursor / Copilot / AGENTS.md-aware tools | `AGENTS.md` |
| Plain CLI | `skills/paper-explainer/scripts/check_sources.py` |

The skill asks the agent to:

1. Extract or receive source text.
2. Fill a concept map before filling the full paper tables.
3. Attach a verbatim quote to every evidence-bearing claim.
4. Run the checker.
5. Repair unsupported cells or mark them missing.

## Project boundary

This project intentionally stays small.

It does:

- Verify source-grounded claim/quote pairs.
- Provide table templates for structured paper notes.
- Package the workflow for agent environments.
- Make unsupported evidence visible in reports and exit codes.

It does not aim to be:

- A paper library manager.
- A PDF parsing platform.
- A Notion exporter.
- A web app.
- An embedding or RAG framework.
- A one-click system for reading every paper.

## Development

```bash
make test
make demo
```

Local Codex skill validation:

```bash
make validate-skill
```

## Roadmap

- More worked examples across ML, systems, and biomedical papers.
- Batch and cache support for `--strict`.
- Optional source-fetch helpers for arXiv-style inputs.
- Stronger table-to-claim extraction.

## License

MIT.
