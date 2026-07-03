# AGENTS.md — Paper Explainer

> Cross-agent instructions (Codex, Cursor, Copilot, and other AGENTS.md-aware
> tools). Claude Code / claude.ai users are served by
> `skills/paper-explainer/SKILL.md` instead — **both entry points drive the same
> templates and the same checker script**, so behavior is identical.

## What this project does

Turn an academic paper into a concept map and selected evidence-backed tables.
The project is a paper-reading skill with workflows for skim, review,
reproduce, teach, literature review, and evidence audit. Every evidence-bearing
cell must carry a verbatim quote from the paper, and those quotes are
machine-verified so fabricated or too-thin evidence gets flagged.

## Shared assets (do not duplicate — reference these)

- Table templates: `skills/paper-explainer/reference/tables.md`
- Faithfulness checker: `skills/paper-explainer/scripts/check_sources.py`
- Worked example: `skills/paper-explainer/examples/`

## Workflow Presets

| Workflow | Use When | Tables |
|---|---|---|
| Skim | Fast explanation | Concept map, 1, 7, 8, 11, 15 |
| Reviewer | Novelty, logic, weakness analysis | Concept map, 3, 4, 7, 8, 12, 15 |
| Reproduce | Implementation or rerun guidance | Concept map, 4, 5, 6, 7, 10, 14, 15 |
| Teach | Explain the paper to others | Concept map, 1, 2, 10, 11 |
| Literature Review | Field positioning | Concept map, 2, 3, 8, 9, 12, 15 |
| Evidence Audit | Check existing AI notes | Claim/quote JSON, checker, 15 |
| Full Dissection | Maximum depth | Concept map, 1-15 |

Default to Skim for a plain "explain this paper" request. Ask before doing Full
Dissection because it is intentionally heavy.

## Workflow

1. **Get the source text.** Paste, `pdftotext paper.pdf paper.txt`, or fetch the
   arXiv page. Save it to a file — the checker needs it later. If you only have
   the abstract, say so; quotes can only be verified against the text you have.

2. **Choose workflow, then concept map.** Select the workflow preset, then read
   `reference/tables.md` and fill ONLY the 概念-定位映射表 (concept-definition
   map) at the end. Emit a short text knowledge tree. Locking terminology first
   reduces downstream errors. For Evidence Audit on existing notes, skip the
   concept map and start from claim/quote JSON instead.

3. **Fill selected tables.** Fill only the tables selected by the workflow
   unless Full Dissection was requested. One sentence per cell; unknown →
   `缺失`. Every evidence-bearing conclusion needs both a 证据来源 type AND a
   verbatim 原文引文 (copied exactly from the source, never paraphrased or
   invented). If a selected table has no quote column, extract important factual
   conclusions into claim/quote JSON before verification.

4. **Verify.** Extract the (claim, quote) pairs to JSON and run:

   ```bash
   python skills/paper-explainer/scripts/check_sources.py \
       --tables filled_tables.json --source paper.txt
   ```

   - Default: L1 checks each quote is long enough to be useful evidence and
     actually exists in the source (offline, deterministic). Fabricated quotes
     → `⚠ unsupported`; tiny non-evidence quotes → `invalid_quote`.
   - `--strict`: adds L2, an LLM judge for whether each quote actually supports
     its claim. Needs `ANTHROPIC_API_KEY`.

   JSON input shape (list of objects):
   ```json
   [{"table": "表1", "cell": "核心问题", "claim": "...", "quote": "verbatim ..."}]
   ```

5. **Report & repair.** Show flagged cells. For each `⚠ unsupported` or
   `invalid_quote`: find a better quote, or mark the cell `缺失`. Never leave a
   fabricated or non-evidence quote. End with Table 15 when selected by the
   workflow; for Teach, omit it unless the user asks for research judgment.

## Hard rules

- One sentence per cell; concrete, few adjectives, high information density.
- Every key conclusion tagged with 证据来源 AND a verbatim 原文引文.
- Fill the concept-definition map before selected workflow tables unless doing
  Evidence Audit on existing notes.
- Never invent a quote to fill the 原文引文 column — write `缺失` instead.
