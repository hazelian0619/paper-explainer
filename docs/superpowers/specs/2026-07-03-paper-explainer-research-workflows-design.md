# Paper Explainer Research Workflow Design

## Goal

Reposition `paper-explainer` from "a faithfulness checker for AI paper notes" to
"a paper-reading skill with research workflows." The checker remains important,
but it becomes the trust layer under the main asset: a concept map plus a
15-table paper-understanding protocol.

The project should feel useful to a researcher who needs to skim, review,
reproduce, teach, or audit a paper. It should not feel like a generic summary
prompt or a standalone citation checker.

## Current Mispositioning

The current README leads with fabricated evidence and the checker. That is
technically true but undersells the repository. The unique value is in
`skills/paper-explainer/reference/tables.md`:

- a concept-definition map that must be filled before downstream notes
- 15 tables covering paper thesis, concepts, method, experiments, formulas,
  logic, reproduction, and confidence gaps
- evidence-bearing cells that require verbatim quotes
- a checker that makes those quotes auditable

The README should make the table protocol visible before the checker.

## Researcher Value Model

Researchers do not only want "a summary." They want to answer concrete research
questions:

1. What problem does the paper claim to solve?
2. What is actually new compared with prior work?
3. What assumptions does the method depend on?
4. Do the experiments support the conclusion?
5. Can I reproduce or implement it?
6. Where does it sit in the literature?
7. What are the missing details, weak claims, and next experiments?

Each table should map to one of these research actions.

## Table Roles

| Table | Role | Research Action | Default Use |
|---|---|---|---|
| Concept map | Terminology lock | Prevent term drift before analysis | Always first |
| Table 1: one-page thesis | Mainline | Understand the paper in one pass | Skim, Teach |
| Table 2: core concept comparison | Concept contrast | Distinguish easily-confused ideas | Teach, Literature Review |
| Table 3: old vs new | Novelty test | Judge whether the paper is actually new | Reviewer, Literature Review |
| Table 4: method modules | Mechanism decomposition | Understand what must be built | Reviewer, Reproduce |
| Table 5: technical details | Technical innovation | Inspect the core technical move | Reproduce |
| Table 6: algorithm flow | Execution trace | Know how the method runs step by step | Reproduce |
| Table 7: experiments and results | Evidence test | Check whether results support claims | Skim, Reviewer, Reproduce |
| Table 8: strengths, limits, fit | Boundary judgment | Decide where the paper applies | Skim, Reviewer |
| Table 9: related-work position | Literature placement | Compare with neighboring work | Literature Review |
| Table 10: formula lookup | Mathematical parsing | Make notation reusable | Teach, Reproduce |
| Table 11: three-step memory | Teaching compression | Explain the paper quickly | Skim, Teach |
| Table 12: logic map | Reviewer reasoning | Trace claim, evidence, assumptions, alternatives | Reviewer, Literature Review |
| Table 13: tradeoff surface | Cost-risk-performance judgment | Compare benefits, costs, and constraints | Optional, domain-sensitive |
| Table 14: reproduction checklist | Implementation readiness | Turn paper into runnable work | Reproduce |
| Table 15: gaps and confidence | Research judgment | State what remains uncertain | Always last |

## Workflow Presets

The skill should ask or infer a workflow before filling tables. The default
should not be "fill all 15 tables"; that is often too heavy and may produce
repetitive output.

| Workflow | Use When | Tables |
|---|---|---|
| Skim | User wants a 30-minute understanding | Concept map, 1, 7, 8, 11, 15 |
| Reviewer | User wants to judge novelty and weakness | Concept map, 3, 4, 7, 8, 12, 15 |
| Reproduce | User wants to implement or rerun the work | Concept map, 4, 5, 6, 7, 10, 14, 15 |
| Teach | User wants to explain the paper to others | Concept map, 1, 2, 10, 11 |
| Literature Review | User wants to place the paper in a field | Concept map, 2, 3, 8, 9, 12, 15 |
| Evidence Audit | User wants to check existing AI notes | Claim/quote JSON, checker, 15 |
| Full Dissection | User explicitly asks for maximum depth | Concept map, 1-15 |

## Table 13 Redesign

Current Table 13 is too domain-specific:

`置信度 λ | 专家轨迹数 N | 违反率 | 奖励/效用 | 风险等级 | 决策建议`

This reads like safe imitation learning or control. It should become a more
general table:

`权衡维度 | 收益 | 代价 | 约束条件 | 失败风险 | 适用边界 | 证据来源 | 原文引文`

Name: `表13 性能-成本-风险权衡`.

This keeps the table useful for ML, systems, HCI, biomedical, and theory papers.
If a domain needs specialized fields, the skill can adapt Table 13 after the
generic version is filled.

## README Design

The README should lead with the research workflow asset:

> A paper-reading skill with workflows for skim, review, reproduce, teach, and
> audit.

The first screen should explain:

- this is not a prose summary prompt
- it is a concept map plus 15 evidence-backed tables
- different workflows select different tables
- the checker verifies the evidence attached to table cells

Recommended README order:

1. One-sentence value proposition
2. Why 15 tables matter
3. Workflow matrix
4. Small output sample showing a table row with a quote
5. Evidence checker demo
6. Manual CLI usage
7. Agent entry points
8. Known limits
9. Development

## Skill Design

`SKILL.md` should add a new first step:

1. Choose or infer workflow.
2. Fill concept map.
3. Fill only the selected tables unless the user asks for full dissection.
4. Extract claim/quote pairs from evidence-bearing cells.
5. Run checker.
6. Repair unsupported or invalid evidence.
7. End with Table 15 for all research judgment workflows.

If the user does not specify a workflow, default to `Skim` for "explain this
paper" and ask before doing `Full Dissection`.

## Demo Design

The README should show both:

- a small filled table row, so users see the actual artifact
- the checker output, so users see the trust layer

The existing fake-citation demo should remain. It proves the audit layer works.
But it should be presented after the table workflow, not as the core project.

## Non-Goals

Do not add:

- web UI
- Notion export
- embedding or RAG stack
- PDF parsing platform
- paper library manager
- multiple skills split from this one yet

Do not make every workflow a separate skill until the single-skill workflow
matrix has proved useful.

## Acceptance Criteria

After implementation:

- README headline and first screen present the project as a paper-reading skill
  with workflow presets.
- README shows the 15-table protocol or a concise map of it.
- README includes a workflow matrix.
- README includes at least one table-output example before checker output.
- `SKILL.md` tells the agent to choose or infer a workflow before filling tables.
- `tables.md` names Table 13 generically as a performance-cost-risk tradeoff
  table.
- Checker behavior remains unchanged and all current tests pass.
- `make validate-skill` still passes.

