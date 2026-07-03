# Paper Explainer

> A paper-reading skill with workflows for skim, review, reproduce, teach, and audit.

`paper-explainer` is not a generic summary prompt. It is a structured research
workflow for turning an academic paper into a concept map and evidence-backed
tables.

The core asset is a 15-table paper understanding protocol:

- lock terminology first with a concept map
- choose a workflow based on the research task
- fill only the tables that serve that task
- attach verbatim quotes to evidence-bearing claims
- run the checker so fabricated or too-thin evidence is visible

The checker matters, but it is not the whole project. It is the trust layer
under the table workflow.

## Why This Exists

Researchers do not only need "a summary." They need to know:

- what problem the paper claims to solve
- what is actually new
- what assumptions the method depends on
- whether the experiments support the conclusion
- whether the work can be reproduced
- where the paper sits in the literature
- what remains uncertain

`paper-explainer` turns those questions into reusable workflows.

## Workflow Presets

Start by choosing the workflow that matches your reading goal:

| Workflow | Use When | Tables |
|---|---|---|
| Skim | You want a 30-minute understanding | Concept map, 1, 7, 8, 11, 15 |
| Reviewer | You want to judge novelty, logic, and weaknesses | Concept map, 3, 4, 7, 8, 12, 15 |
| Reproduce | You want to implement or rerun the work | Concept map, 4, 5, 6, 7, 10, 14, 15 |
| Teach | You want to explain the paper to someone else | Concept map, 1, 2, 10, 11 |
| Literature Review | You want to position the paper in a field | Concept map, 2, 3, 8, 9, 12, 15 |
| Evidence Audit | You already have AI notes and want to check them | Claim/quote JSON, checker, 15 |
| Full Dissection | You explicitly want maximum depth | Concept map, 1-15 |

The default is not "fill every table." The default is to select the right
workflow, then fill the tables that produce useful research judgment.

## The 15-Table Protocol

| Table | Research Job |
|---|---|
| Concept map | Lock terminology before analysis |
| 1. One-page thesis | Understand the paper in one pass |
| 2. Core concept comparison | Distinguish easily-confused ideas |
| 3. Old vs new | Test novelty against prior approaches |
| 4. Method modules | Decompose what must be built |
| 5. Technical details | Inspect the core technical move |
| 6. Algorithm flow | Trace how the method runs |
| 7. Experiments and results | Check whether evidence supports claims |
| 8. Strengths, limits, fit | Decide where the paper applies |
| 9. Related-work position | Place the paper in the literature |
| 10. Formula lookup | Make notation reusable |
| 11. Three-step memory | Compress the paper for teaching |
| 12. Logic map | Trace claims, evidence, assumptions, alternatives |
| 13. Performance-cost-risk tradeoff | Compare benefits, costs, constraints, and failure risk |
| 14. Reproduction checklist | Turn the paper into runnable work |
| 15. Gaps and confidence | State uncertainty and next evidence needed |

## Output Shape

A useful row is not just a claim. It carries evidence:

| Table | Cell | Claim | Quote |
|---|---|---|---|
| Table 7 | Observed gain | MEAL improves accuracy by 50 percent over single-modality baselines. | "improving accuracy by 50% over single-modality baselines" |

That quote can be checked against the source text. If the quote is fabricated,
too short to be evidence, or attached to the wrong claim in strict mode, the
workflow marks it for review.

## Evidence Checker Demo

Run the failing demo:

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

Run the passing demo:

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

## Manual Checker Usage

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

Run the checker against source text:

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

## Agent Entry Points

| Environment | Entry Point |
|---|---|
| Claude Code / claude.ai / Agent SDK | `skills/paper-explainer/SKILL.md` |
| Codex / Cursor / Copilot / AGENTS.md-aware tools | `AGENTS.md` |
| Plain CLI | `skills/paper-explainer/scripts/check_sources.py` |

## Known Limits

This project verifies the evidence attached to claims. It does not verify
claims that have no quote, source text you did not provide, PDF extraction
quality, or whether every important point in the paper was captured.

That boundary is intentional. The project stays small so the protocol remains
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
