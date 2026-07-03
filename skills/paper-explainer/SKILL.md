---
name: paper-explainer
description: "Use this skill whenever the user wants to deeply understand, dissect, or take structured notes on an academic paper. Triggers include: any mention of 'read this paper', 'explain this paper', 'summarize a paper', 'paper notes', 'literature review', 'lit review', 'dissect a paper', 'help me understand this arXiv/paper', a pasted arXiv link or PDF, or a request to prepare a paper for review, reproduction, or study. This skill produces a set of structured, review-ready tables (core problem, method, experiments, formulas, reproduction checklist, confidence report) where every evidence-bearing claim carries a verbatim quote from the source, so the extraction can be machine-verified for faithfulness. Do NOT use this skill for: writing or drafting a new paper, translating a paper end-to-end, general prose summarization where structure is not wanted, or non-academic documents. Prefer this skill over a freeform summary whenever the user wants to *retain*, *review*, or *reproduce* what a paper says."
---

# Paper Explainer

You now have expertise in turning an academic paper into structured research
workflows. The goal is not a prose summary. The goal is to choose the right
paper-reading workflow, fill a concept map plus selected evidence-backed
tables, and verify that important claims trace back to source text.

## Core principle: every claim carries evidence

The central failure mode of LLM paper summaries is **fabricated evidence** — the
model invents a plausible-sounding "experiment" or "result" that the paper never
states. This skill defends against that with one rule:

> Every cell that asserts a factual claim MUST include a **verbatim quote** from
> the source (copied exactly, not paraphrased) plus a section pointer. If you
> cannot find a supporting quote, write `缺失` (missing) — never invent one.

These quotes are what `scripts/check_sources.py` verifies against the source
text. Fabricated quotes will not match the source and get flagged; quotes that
are too short to be useful evidence are flagged as `invalid_quote`.

## Choose a workflow first

Do not mechanically fill all 15 tables unless the user asks for maximum depth.
Choose or infer one workflow:

| Workflow | Use When | Tables |
|---|---|---|
| Skim | User wants a fast explanation | Concept map, 1, 7, 8, 11, 15 |
| Reviewer | User wants novelty, logic, and weakness analysis | Concept map, 3, 4, 7, 8, 12, 15 |
| Reproduce | User wants implementation or rerun guidance | Concept map, 4, 5, 6, 7, 10, 14, 15 |
| Teach | User wants to explain the paper to others | Concept map, 1, 2, 10, 11 |
| Literature Review | User wants field positioning | Concept map, 2, 3, 8, 9, 12, 15 |
| Evidence Audit | User already has notes to check | Claim/quote JSON, checker, 15 |
| Full Dissection | User explicitly asks for maximum depth | Concept map, 1-15 |

If the user only says "explain this paper", default to Skim. Ask before doing
Full Dissection because it is intentionally heavy.

## Quick Reference

| Step | What to do | File |
|------|-----------|------|
| 1. Choose | Select Skim, Reviewer, Reproduce, Teach, Literature Review, Evidence Audit, or Full Dissection | — |
| 2. Locate | Read the source text (paste, PDF-extracted text, or fetched arXiv) | — |
| 3. Map concepts | Fill the concept-definition map FIRST to lock terminology | `reference/tables.md` |
| 4. Fill selected tables | Fill only the workflow tables unless Full Dissection was requested | `reference/tables.md` |
| 5. Verify | Run the faithfulness checker on evidence-bearing cells | `scripts/check_sources.py` |
| 6. Report | Surface flagged cells; fix or mark them `缺失`; end with Table 15 for research judgment workflows | — |

## Workflow

### Step 1 — Get the source text

You need the paper's actual text to quote from. In order of preference:

- User pasted the text or abstract → use it directly.
- A PDF path → extract with `pdftotext paper.pdf paper.txt` (or PyMuPDF).
- An arXiv link/ID → fetch the HTML/abstract page text.

Save the source text to a file (e.g. `paper.txt`). The checker needs it in
Step 4. If you only have the abstract, say so — quotes can only be verified
against the text you actually have.

### Step 2 — Concept map first (two-pass design)

Do **not** dump all 15 tables at once. First read `reference/tables.md` and fill
only the **概念-定位映射表 (concept-definition map)** at the end. This forces you
to pin down every key term before using it. Then emit a short text knowledge
tree, ensuring every term in the tree also appears in the map.

Rationale: locking terminology first measurably reduces downstream errors — the
model stops silently redefining terms table to table.

### Step 3 — Fill the selected workflow tables

Read `reference/tables.md` and fill the tables selected by the workflow. Fill
all 15 tables only for Full Dissection. Rules:

- One sentence per cell. Cut anything that can be cut. Unknown → `缺失`.
- Numbers get ranges or mean ± variance, not vague adjectives.
- Every evidence-bearing conclusion needs the **证据来源** (type: 理论/实验/消融/可视化/案例) **and** a **原文引文** (verbatim quote) column filled.
- Audience level (入门 / 熟悉 / Reviewer) controls term density: for 入门, keep formula skeletons minimal with intuition; for Reviewer, add derivation and complexity notes.

### Step 4 — Verify faithfulness (the part that matters)

Once tables are filled, extract the (claim, quote) pairs into a JSON file and
run the checker:

```bash
python scripts/check_sources.py --tables filled_tables.json --source paper.txt
```

- **Default (offline, deterministic):** L1 checks that every quote is long
  enough to be useful evidence and actually exists in the source via fuzzy
  matching. Fabricated quotes → `⚠ unsupported`; tiny non-evidence quotes →
  `invalid_quote`.
- **`--strict`:** additionally runs L2 — an LLM judge that checks whether each
  (real) quote actually *supports* the claim it's attached to, catching
  "quote is real but cites the wrong thing" errors.

See `scripts/check_sources.py --help` for the exact JSON shape.

### Step 5 — Report and repair

Show the faithfulness report to the user. For any `⚠ unsupported` or
`invalid_quote` cell: either find a better quote from the source, or mark the
cell `缺失`. Never leave fabricated or non-evidence quotes in place. End with
table 15 (信息缺口与置信报告) quantifying overall confidence.

## Output rules (always)

- One sentence per cell; concrete, few adjectives, high information density.
- Every key conclusion tagged with 证据来源 AND a verbatim 原文引文.
- Fill the concept-definition map before the 15 tables.
- The text must be genuinely easy to read: simple, clear, logical, memorable.

## License

MIT. See `LICENSE.txt`.
