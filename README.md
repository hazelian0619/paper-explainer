# Paper Explainer

> A paper-reading skill that makes AI dissect papers through a concept map and
> 15 research tables, instead of writing loose summaries.

Most AI paper summaries answer one weak question: "What is this paper about?"

That is not enough for research work. A serious reader also needs to know what
the key terms mean, whether the claimed novelty is real, how the method works,
which experiments support which claims, what the limits are, what can be
reproduced, and what remains uncertain.

`paper-explainer` gives an agent a table-by-table reasoning system for doing
that work. The core asset is not the checker. The core asset is the **concept
map + 15-table protocol**.

The checker is the trust layer underneath the protocol: it helps verify that
evidence-bearing claims are anchored to source text.

## What This Skill Gives You

This skill turns a paper into a structured research artifact:

```text
Terms -> Thesis -> Novelty -> Mechanism -> Evidence -> Boundaries -> Reproduction -> Confidence
```

The 15 tables are not a long note-taking template. Each table is a specific
defense against a common failure mode in paper reading:

- concepts drift;
- novelty gets accepted too quickly;
- methods become black boxes;
- experiments are repeated without being judged;
- limitations are hidden behind good results;
- reproduction work is left vague;
- the final answer sounds more certain than the paper allows.

The protocol separates those jobs so the agent cannot collapse everything into
one fluent but uninspectable paragraph.

## The 15 Tables Are A Research Reasoning System

Each table has three parts:

- **Why it exists**: the misunderstanding it prevents.
- **Thinking move**: the reasoning operation the table forces.
- **Mini example**: the kind of row the table should produce.

The examples below use clinical-trial AI papers such as TrialBench and
ClinicalAgent as running examples, but the same table logic works for product
reviews, commercial strategy, competitive analysis, and industry research.

### Concept Map: Lock the Vocabulary

**Why it exists:** Research goes wrong early when the agent treats key terms as
obvious. A term may be a dataset, model, benchmark, workflow, task, or product
surface. If that role is not fixed, later tables drift.

**Thinking move:** Define each term, name its parent category, separate it from
similar terms, and state its role in the paper.

**Mini example:**

| Term | Definition | Parent Category | Distinction | Role |
|---|---|---|---|---|
| TrialBench | AI-ready clinical-trial benchmark with tasks, data, and baselines | Benchmark dataset | Not a model or agent | Main object being introduced |

### Table 1: One-Page Thesis

**Why it exists:** Readers often collect details before they can state the
paper's spine. This table forces the main axis into one page.

**Thinking move:** Compress the paper into problem, method, mechanism, strongest
evidence, and value.

**Mini example:**

| Item | Content |
|---|---|
| Core problem | Raw clinical-trial records are rich but hard to use directly for ML tasks. |
| Method | TrialBench turns multi-source trial records into 8 task families and 23 AI-ready datasets. |
| Main value | It makes clinical-trial prediction research easier to compare and reproduce. |

### Table 2: Core Concept Comparison

**Why it exists:** Many papers rely on concepts that sound interchangeable. If
the agent cannot separate them, every downstream conclusion gets blurry.

**Thinking move:** Compare the goal, input, output, and example for three
easily-confused concepts.

**Mini example:**

| Concept | Goal | Input | Output |
|---|---|---|---|
| ClinicalTrials.gov record | Store trial registration and results | Raw trial fields and text | Source record |
| TrialBench dataset | Train and evaluate ML models | Cleaned task features and labels | AI-ready task table |
| Baseline model | Validate that tasks are learnable | Task table and modalities | Reference metric |

### Table 3: Old vs New

**Why it exists:** Authors often present novelty in their own language. This
table checks whether the difference is structural or just rhetorical.

**Thinking move:** Put old practice, the paper's change, and the consequence in
the same row.

**Mini example:**

| Dimension | Old Practice | This Paper | Impact |
|---|---|---|---|
| Task design | Single-task datasets built ad hoc | Multiple standardized clinical-trial tasks | Easier cross-paper comparison |

### Table 4: Method Modules

**Why it exists:** A method name can hide several moving parts. This table turns
the method into buildable modules.

**Thinking move:** For each module, name the input, process, output,
assumption, risk, and observed benefit.

**Mini example:**

| Module | Input | Process | Output | Risk |
|---|---|---|---|---|
| Label construction | Trial dates, outcomes, text fields | Convert raw records into supervised targets | Task labels | Label noise or time leakage |

### Table 5: Technical Details

**Why it exists:** Some papers wrap ordinary engineering in technical language.
This table asks where the real technical move is.

**Thinking move:** Compare traditional practice with the paper's technical
choice, then explain the expression and intuition.

**Mini example:**

| Technical Point | Traditional Practice | Paper's Move | Intuition |
|---|---|---|---|
| Drug representation | Use drug name or category | Use SMILES as molecular graph input | Structure may affect safety and efficacy |

### Table 6: Algorithm Flow

**Why it exists:** A method description can read well but still be impossible to
run. This table converts prose into execution order.

**Thinking move:** Track each stage, what it does, how it works, the constraint,
the stopping point, and the artifact produced.

**Mini example:**

| Stage | Action | Constraint | Output |
|---|---|---|---|
| Feature preparation | Flatten trial records into model inputs | Avoid post-outcome leakage | Task-level feature table |

### Table 7: Experiments and Results

**Why it exists:** The most common false confidence comes from repeating the
author's result sentence without auditing the experiment.

**Thinking move:** Split evidence into scenario, task, metric, value, baseline,
relative change, variance, and conclusion.

**Mini example:**

| Task | Metric | Paper Value | Baseline | Conclusion |
|---|---|---|---|---|
| Trial outcome prediction | PR-AUC | ClinicalAgent 0.7908 | GPT-4 prompt 0.4582, HAtten 0.8718 | Better than prompting, not pure SOTA |

### Table 8: Strengths, Limits, Fit

**Why it exists:** Good results do not mean universal usefulness. This table
keeps application boundaries visible.

**Thinking move:** Separate strengths, weaknesses, suitable scenarios,
unsuitable scenarios, and mitigation strategies.

**Mini example:**

| Item | Content | Response |
|---|---|---|
| Limit | Random train/test splits may overstate deployment generalization | Add temporal and location-based splits |

### Table 9: Related-Work Position

**Why it exists:** A paper is easier to judge when you know where it sits in the
field. This table is a map, not a bibliography.

**Thinking move:** Compare method category, representative work, assumption,
difference, and whether the relation is complementary or substitutive.

**Mini example:**

| Category | Representative | Relation |
|---|---|---|
| Benchmark dataset | TrialBench | Provides tasks/data that an agent system could use |
| Agent workflow | ClinicalAgent | Uses tools and reasoning over clinical-trial questions |

### Table 10: Formula Lookup

**Why it exists:** Formulas are often scattered across the paper. If the agent
does not collect them, reproduction and teaching become fragile.

**Thinking move:** Store formula, meaning, use, and variable definitions in one
place.

**Mini example:**

| Formula | Meaning | Use |
|---|---|---|
| dropout_rate = dropout_count / enrolled_count | Fraction of enrolled participants who drop out | Label construction for dropout prediction |

### Table 11: Three-Step Memory

**Why it exists:** Understanding is not the same as recall. This table makes the
paper teachable.

**Thinking move:** Compress the whole paper into problem, solution, and value.

**Mini example:**

| Step | Content |
|---|---|
| Problem | Trial data is rich but hard to use directly. |
| Solution | Convert it into standardized AI-ready tasks. |
| Value | Enables reproducible benchmarking and comparison. |

### Table 12: Logic Map

**Why it exists:** A paper's conclusion depends on claims, evidence,
assumptions, and alternatives. This table audits that argument chain.

**Thinking move:** Trace each key claim to evidence, the assumption that makes
the evidence relevant, the turning point in the argument, and possible
alternative explanations.

**Mini example:**

| Claim | Evidence | Assumption | Alternative Explanation |
|---|---|---|---|
| Baseline performance shows dataset usability | Reported task metrics | Random split reflects meaningful generalization | Metrics may be inflated by split design |

### Table 13: Performance-Cost-Risk Tradeoff

**Why it exists:** Research readers often overfocus on performance. Product and
strategy readers need cost, constraints, and failure modes too.

**Thinking move:** Compare benefit, cost, constraint, failure risk, boundary,
and evidence source.

**Mini example:**

| Benefit | Cost | Risk | Boundary |
|---|---|---|---|
| Agent workflow is more interpretable than direct prompting | More API calls and tool dependencies | Tool outputs may be stale or incomplete | Use for assisted analysis, not autonomous clinical decisions |

### Table 14: Reproduction Checklist

**Why it exists:** A paper can feel understood while still being impossible to
rerun. This table converts understanding into work.

**Thinking move:** List environment, data, hyperparameters, resources, scripts,
randomness controls, and traps.

**Mini example:**

| Item | Requirement | Common Trap |
|---|---|---|
| Data | Fix dataset version, task split, and NCT IDs | Mixing toy GitHub samples with full benchmark data |

### Table 15: Gaps and Confidence

**Why it exists:** The final table prevents the agent from pretending the paper
is fully settled.

**Thinking move:** State the information gap, current assumption, possible
impact, needed evidence, and confidence level.

**Mini example:**

| Gap | Possible Impact | Needed Evidence | Confidence |
|---|---|---|---|
| GPT-derived labels are not fully audited | Failure-reason task may contain systematic noise | Human adjudication sample and agreement rate | Medium-low |

## Choose A Reading Workflow

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
Full Dissection when you want the complete table-by-table analysis.

## Copy-Paste Prompts

Fast read:

```text
Use paper-explainer in Skim mode. Start with the concept map, then fill Tables
1, 7, 8, 11, and 15. Keep each cell to one sentence and mark missing evidence
instead of guessing.
```

Critical review:

```text
Use paper-explainer in Reviewer mode. Focus on novelty, method modules,
experiments, limits, logic, and confidence gaps. Attach source quotes to
evidence-bearing claims.
```

Reproduction:

```text
Use paper-explainer in Reproduce mode. Emphasize method modules, technical
details, algorithm flow, formulas, experimental evidence, and the reproduction
checklist.
```

Full dissection:

```text
Use paper-explainer in Full Dissection mode. Fill the concept map and Tables
1-15. For each evidence-bearing claim, include a quote or mark the evidence as
missing.
```

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
