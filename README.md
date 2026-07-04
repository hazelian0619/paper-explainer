# Paper Explainer

> A paper-reading skill that makes AI dissect papers through a concept map and
> 15 research tables, instead of writing loose summaries.

Most AI paper summaries answer one shallow question: "What is this paper
about?"

`paper-explainer` makes an agent ask the fuller set of questions a careful
reader needs before trusting a paper:

- What do the key terms mean in this paper, and where can they drift?
- What is the paper's main claim, and what is merely supporting detail?
- Is the claimed novelty real, or only a rephrasing of prior work?
- How does the method work as modules, details, flow, and formulas?
- Which experiments support which conclusions?
- Where does the method fit, fail, cost too much, or remain risky?
- What would I need to reproduce it?
- What is still missing, uncertain, or unsupported?

The core asset is the **concept map + 15-table protocol**. The checker is the
trust layer underneath it: useful, but secondary to the table design.

## The 15-Table Design

The 15 tables are not a long checklist. They are a complete reading system.
Together, they turn one paper into a structured research artifact:

```text
Terms -> Thesis -> Novelty -> Mechanism -> Evidence -> Boundaries -> Reproduction -> Confidence
```

Each table exists because a common kind of paper misunderstanding needs its own
place to be handled. If everything is forced into a paragraph, the agent blends
terms, claims, evidence, assumptions, and opinions together. The protocol keeps
them separate.

| Layer | Tables | What This Layer Protects Against |
|---|---|---|
| Terminology | Concept map | Silent term drift and fuzzy definitions |
| Thesis | 1, 11 | Forgetting the paper's main axis after reading details |
| Distinction | 2, 3, 9 | Confusing related concepts, novelty claims, or field position |
| Mechanism | 4, 5, 6, 10 | Treating the method as a black box |
| Evidence | 7, 8, 12, 13 | Accepting claims without checking results, limits, tradeoffs, and assumptions |
| Action | 14, 15 | Finishing with no reproduction plan or confidence report |

That is the design idea: the skill does not ask an agent to "write better
notes." It gives the agent a research reading architecture.

## What Each Table Does

The protocol is deliberately broad. A strong paper note should help you skim,
teach, review, reproduce, and audit the same paper without starting over.

| Unit | Role in the System | Research Job |
|---|---|---|
| Concept map | The anchor | Define terms before analysis drifts |
| 1. One-page thesis | The spine | State problem, method, mechanism, strongest evidence, and value |
| 2. Core concept comparison | The separator | Distinguish ideas that sound similar but behave differently |
| 3. Old vs new | The novelty test | Compare the paper against prior or standard approaches |
| 4. Method modules | The build map | Break the method into inputs, steps, assumptions, risks, and gains |
| 5. Technical details | The microscope | Inspect the core technical move and why it matters |
| 6. Algorithm flow | The execution trace | Follow how the method runs from start to finish |
| 7. Experiments and results | The evidence table | Connect tasks, metrics, baselines, numbers, variance, and conclusions |
| 8. Strengths, limits, fit | The boundary map | Decide where the paper applies and where it does not |
| 9. Related-work position | The field map | Place the paper among neighboring methods and assumptions |
| 10. Formula lookup | The notation index | Make formulas and variables reusable |
| 11. Three-step memory | The teaching handle | Compress the paper into problem, solution, and value |
| 12. Logic map | The argument audit | Track claims, evidence, assumptions, turning points, and alternatives |
| 13. Performance-cost-risk tradeoff | The deployment lens | Compare benefit, cost, constraints, failure modes, and fit |
| 14. Reproduction checklist | The action plan | Convert the paper into runnable reproduction work |
| 15. Gaps and confidence | The final judgment | State missing evidence, uncertainty, and next checks |

This is why Full Dissection uses all 15 tables. It is the most complete mode:
terminology, thesis, novelty, mechanism, experiments, limits, reproduction, and
confidence all get their own place.

## How The Skill Reads

The protocol can be understood as five passes through the paper:

| Pass | Tables | Question |
|---|---|---|
| 1. Orient | Concept map, 1, 11 | What is this paper about, and how do I remember it? |
| 2. Distinguish | 2, 3, 9 | What must not be confused? |
| 3. Decompose | 4, 5, 6, 10 | How does the method actually work? |
| 4. Validate | 7, 8, 12, 13 | Does the evidence support the argument, and where are the boundaries? |
| 5. Operationalize | 14, 15 | What can I do next, and how confident should I be? |

This pass structure is what makes the skill useful. It turns AI assistance from
"summarize the paper" into "walk the paper through the same checkpoints a
researcher would use."

## Choose a Reading Workflow

You do not always need all 15 tables. The skill chooses a subset based on what
you are trying to do.

| Reader Intent | Workflow | Tables |
|---|---|---|
| I need to understand it fast | Skim | Concept map, 1, 7, 8, 11, 15 |
| I need to review it critically | Reviewer | Concept map, 3, 4, 7, 8, 12, 15 |
| I need to reproduce it | Reproduce | Concept map, 4, 5, 6, 7, 10, 14, 15 |
| I need to explain it to others | Teach | Concept map, 1, 2, 10, 11 |
| I need to place it in a field | Literature Review | Concept map, 2, 3, 8, 9, 12, 15 |
| I need to check existing AI notes | Evidence Audit | Claim/quote JSON, checker, 15 |
| I need the full system | Full Dissection | Concept map, 1-15 |

For a plain "explain this paper" request, the skill defaults to Skim. Ask for
Full Dissection when you want the complete 15-table analysis.

## What The Output Looks Like

A useful paper note is not just a claim. It says where the claim belongs in the
research structure and what evidence supports it.

| Table | Cell | Claim | Evidence |
|---|---|---|---|
| Table 7 | Observed gain | The method improves accuracy over single-modality baselines. | A short verbatim quote or source pointer from the paper |

If evidence is missing, the skill should mark it as missing instead of filling
the table with confident prose.

## Evidence Makes The Tables Trustworthy

The checker exists to protect the protocol from fabricated evidence. It checks
whether evidence-bearing table cells are actually anchored to the source text.
It does not replace the concept map or the 15 tables.

Run the deliberately failing demo:

```bash
git clone https://github.com/hazelian0619/paper-explainer.git
cd paper-explainer
make demo
```

The demo contains one fake citation. A healthy run catches it:

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

Expected key lines:

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

`--strict` calls an LLM judge and requires the `anthropic` package plus
`ANTHROPIC_API_KEY`.

## How To Use The Skill

| Environment | Entry Point |
|---|---|
| Claude Code / claude.ai / Agent SDK | `skills/paper-explainer/SKILL.md` |
| Codex / Cursor / Copilot / AGENTS.md-aware tools | `AGENTS.md` |
| Plain CLI evidence checking | `skills/paper-explainer/scripts/check_sources.py` |

Example prompts:

```text
Use paper-explainer to skim this paper.
```

```text
Use paper-explainer in Full Dissection mode and include checker results for evidence-bearing claims.
```

## Known Limits

`paper-explainer` produces structured notes and evidence checks. It does not
guarantee truth.

It does not verify:

- claims with no quote or source pointer
- source text you did not provide
- PDF extraction quality
- whether every important point in the paper was captured
- whether a real quote fully supports its claim unless `--strict` is used

Those limits are intentional. The skill gives the agent a rigorous reading
protocol, and the checker verifies the evidence that can be checked.

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
