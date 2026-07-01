# AGENTS.md — Paper Explainer

> Cross-agent instructions (Codex, Cursor, Copilot, and other AGENTS.md-aware
> tools). Claude Code / claude.ai users are served by
> `skills/paper-explainer/SKILL.md` instead — **both entry points drive the same
> templates and the same checker script**, so behavior is identical.

## What this project does

Turn an academic paper into a set of structured, **source-grounded** knowledge
tables. Every evidence-bearing cell must carry a verbatim quote from the paper,
and those quotes are machine-verified so fabricated evidence gets flagged.

## Shared assets (do not duplicate — reference these)

- Table templates: `skills/paper-explainer/reference/tables.md`
- Faithfulness checker: `skills/paper-explainer/scripts/check_sources.py`
- Worked example: `skills/paper-explainer/examples/`

## Workflow

1. **Get the source text.** Paste, `pdftotext paper.pdf paper.txt`, or fetch the
   arXiv page. Save it to a file — the checker needs it later. If you only have
   the abstract, say so; quotes can only be verified against the text you have.

2. **Concept map first.** Read `reference/tables.md` and fill ONLY the
   概念-定位映射表 (concept-definition map) at the end, then emit a short text
   knowledge tree. Locking terminology first reduces downstream errors.

3. **Fill tables 1–15.** One sentence per cell; unknown → `缺失`. Every
   evidence-bearing conclusion needs both a 证据来源 type AND a verbatim 原文引文
   (copied exactly from the source, never paraphrased or invented).

4. **Verify.** Extract the (claim, quote) pairs to JSON and run:

   ```bash
   python skills/paper-explainer/scripts/check_sources.py \
       --tables filled_tables.json --source paper.txt
   ```

   - Default: L1 checks each quote actually exists in the source (offline,
     deterministic). Fabricated quotes → `⚠ unsupported`.
   - `--strict`: adds L2, an LLM judge for whether each quote actually supports
     its claim. Needs `ANTHROPIC_API_KEY`.

   JSON input shape (list of objects):
   ```json
   [{"table": "表1", "cell": "核心问题", "claim": "...", "quote": "verbatim ..."}]
   ```

5. **Report & repair.** Show flagged cells. For each `⚠ unsupported`: find the
   correct quote, or mark the cell `缺失`. Never leave a fabricated quote.

## Hard rules

- One sentence per cell; concrete, few adjectives, high information density.
- Every key conclusion tagged with 证据来源 AND a verbatim 原文引文.
- Fill the concept-definition map before the 15 tables.
- Never invent a quote to fill the 原文引文 column — write `缺失` instead.
