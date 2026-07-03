# Paper Explainer Research Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reposition `paper-explainer` as a research workflow skill built around a concept map plus 15 evidence-backed paper-reading tables, with the checker as the trust layer.

**Architecture:** Keep the existing single skill package. Do not split into multiple skills yet. Update the public README, table protocol, and agent instructions so users first see workflow presets and table value, then see the checker as evidence audit.

**Tech Stack:** Markdown documentation, Codex/Claude skill metadata, existing Python standard-library checker, existing Makefile validation.

---

## Scope Check

This plan changes documentation and skill instructions only. It must not change
checker behavior, add dependencies, add a web UI, add PDF parsing, add RAG, or
split the repository into multiple skills.

## File Structure

- `README.md`: public GitHub narrative. It must lead with research workflows and the 15-table protocol.
- `skills/paper-explainer/reference/tables.md`: source of truth for the concept map, 15 tables, table roles, and workflow presets.
- `skills/paper-explainer/SKILL.md`: Claude/agent skill instructions. It must tell the agent to choose or infer a workflow before filling tables.
- `AGENTS.md`: cross-agent instructions for Codex, Cursor, Copilot, and AGENTS.md-aware tools. It must stay aligned with `SKILL.md`.
- `skills/paper-explainer/scripts/check_sources.py`: unchanged in this plan.
- `tests/test_check_sources.py`: unchanged in this plan.

## Task 1: Rewrite README Around Research Workflows

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md`**

Replace the complete file with:

````markdown
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
````

- [ ] **Step 2: Check README commands**

Run:

```bash
make demo
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected:

- `make demo` exits 0 and prints `VERDICT: REVIEW NEEDED`.
- The passing demo exits 0 and prints `VERDICT: PASS`.

- [ ] **Step 3: Commit README**

```bash
git add README.md
git commit -m "docs: lead with research workflows"
```

## Task 2: Update Table Protocol and Table 13

**Files:**
- Modify: `skills/paper-explainer/reference/tables.md`

- [ ] **Step 1: Replace the opening usage block**

Replace the first heading and usage block through the checker sentence with:

```markdown
# 论文拆解表格模板（概念映射 + 15 表）

> 核心原则：这不是普通论文总结模板，而是一套科研阅读工作流。
>
> 先做「概念-定位映射」，再按阅读目标选择表格：
> - Skim：概念映射 + 表1 + 表7 + 表8 + 表11 + 表15
> - Reviewer：概念映射 + 表3 + 表4 + 表7 + 表8 + 表12 + 表15
> - Reproduce：概念映射 + 表4 + 表5 + 表6 + 表7 + 表10 + 表14 + 表15
> - Teach：概念映射 + 表1 + 表2 + 表10 + 表11
> - Literature Review：概念映射 + 表2 + 表3 + 表8 + 表9 + 表12 + 表15
> - Evidence Audit：claim/quote JSON + checker + 表15
> - Full Dissection：概念映射 + 表1-15
>
> 使用规则（务必遵守）：
> - 每格尽量一句话，能砍就砍；未知填「缺失」。
> - 数值给区间或均值 ± 方差，不用模糊形容词。
> - 关键术语给一句话定义。
> - **凡带「证据来源」或「原文引文」的结论，必须从原文逐字复制引文。** 找不到就填「缺失」，绝不编造。
> - 受众层级（入门 / 熟悉 / Reviewer）决定术语密度：入门只保留核心符号 + 直觉；Reviewer 补推导与复杂度。
> - 默认不要机械填满 15 表；除非用户要求 Full Dissection，否则按工作流选表。

「原文引文」列是 `scripts/check_sources.py` 的校验对象：编造引文、过短引文、严格模式下不支撑 claim 的引文都会被标出。
```

- [ ] **Step 2: Insert table role map after the horizontal rule**

After the first `---`, insert:

```markdown
## 表格角色速查

| 表格 | 科研动作 | 常用工作流 |
| --- | --- | --- |
| 概念-定位映射表 | 先锁定术语，防止后续分析漂移 | 全部 |
| 表1 一句话看懂全文 | 抓住论文主轴 | Skim / Teach |
| 表2 三个核心概念对比 | 区分易混概念 | Teach / Literature Review |
| 表3 传统方法 vs 本文 | 判断新意是否成立 | Reviewer / Literature Review |
| 表4 方法模块/功能拆解 | 拆出可实现的模块 | Reviewer / Reproduce |
| 表5 核心技术细节 | 看清技术创新点 | Reproduce |
| 表6 算法流程对比 | 追踪方法如何运行 | Reproduce |
| 表7 实验设计与结果 | 判断证据是否支撑结论 | Skim / Reviewer / Reproduce |
| 表8 优缺点与适用场景 | 判断适用边界 | Skim / Reviewer |
| 表9 相关工作定位 | 放进文献脉络 | Literature Review |
| 表10 公式速查 | 复用符号和数学表达 | Teach / Reproduce |
| 表11 三步记忆法 | 把论文压缩成可讲述结构 | Skim / Teach |
| 表12 论文逻辑地图 | 追踪论点、证据、假设和替代解释 | Reviewer / Literature Review |
| 表13 性能-成本-风险权衡 | 比较收益、成本、约束和失败风险 | 可选 |
| 表14 复现与落地清单 | 转成可执行复现任务 | Reproduce |
| 表15 信息缺口与置信报告 | 给出研究判断和不确定性 | Skim / Reviewer / Reproduce / Literature Review |
```

- [ ] **Step 3: Replace Table 13**

Replace the current Table 13 block:

```markdown
## 表13 置信-性能-数据权衡
| 置信度 λ | 专家轨迹数 N | 违反率 | 奖励/效用 | 风险等级 | 决策建议 |
| --- | --- | --- | --- | --- | --- |
```

with:

```markdown
## 表13 性能-成本-风险权衡
| 权衡维度 | 收益 | 代价 | 约束条件 | 失败风险 | 适用边界 | 证据来源 | 原文引文 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

- [ ] **Step 4: Verify table text**

Run:

```bash
rg -n "Workflow|Skim|Reviewer|Reproduce|性能-成本-风险|置信度 λ|专家轨迹数" skills/paper-explainer/reference/tables.md
```

Expected:

- Matches for `Skim`, `Reviewer`, `Reproduce`, and `性能-成本-风险`.
- No matches for `置信度 λ` or `专家轨迹数`.

- [ ] **Step 5: Commit table protocol**

```bash
git add skills/paper-explainer/reference/tables.md
git commit -m "docs: add research workflow table protocol"
```

## Task 3: Update Skill Instructions With Workflow Selection

**Files:**
- Modify: `skills/paper-explainer/SKILL.md`

- [ ] **Step 1: Replace the opening description paragraph**

Replace the paragraph under `# Paper Explainer` with:

```markdown
You now have expertise in turning an academic paper into structured research
workflows. The goal is not a prose summary. The goal is to choose the right
paper-reading workflow, fill a concept map plus selected evidence-backed
tables, and verify that important claims trace back to source text.
```

- [ ] **Step 2: Add a workflow selection section before Quick Reference**

Insert this section before `## Quick Reference`:

```markdown
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
```

- [ ] **Step 3: Replace Quick Reference table**

Replace the existing Quick Reference table with:

```markdown
| Step | What to do | File |
|------|-----------|------|
| 1. Choose | Select Skim, Reviewer, Reproduce, Teach, Literature Review, Evidence Audit, or Full Dissection | — |
| 2. Locate | Read the source text (paste, PDF-extracted text, or fetched arXiv) | — |
| 3. Map concepts | Fill the concept-definition map FIRST to lock terminology | `reference/tables.md` |
| 4. Fill selected tables | Fill only the workflow tables unless Full Dissection was requested | `reference/tables.md` |
| 5. Verify | Run the faithfulness checker on evidence-bearing cells | `scripts/check_sources.py` |
| 6. Report | Surface flagged cells; fix or mark them `缺失`; end with Table 15 for research judgment workflows | — |
```

- [ ] **Step 4: Update Step 3 heading**

Replace:

```markdown
### Step 3 — Fill tables 1–15
```

with:

```markdown
### Step 3 — Fill the selected workflow tables
```

Replace the sentence:

```markdown
Read the full table set in `reference/tables.md` and fill them. Rules:
```

with:

```markdown
Read `reference/tables.md` and fill the tables selected by the workflow. Fill
all 15 tables only for Full Dissection. Rules:
```

- [ ] **Step 5: Validate skill**

Run:

```bash
make validate-skill
```

Expected: `Skill is valid!`

- [ ] **Step 6: Commit skill instructions**

```bash
git add skills/paper-explainer/SKILL.md
git commit -m "docs: teach skill workflow presets"
```

## Task 4: Sync AGENTS.md With Skill Workflow

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Replace project description**

Replace the `## What this project does` paragraph with:

```markdown
Turn an academic paper into a concept map and selected evidence-backed tables.
The project is a paper-reading skill with workflows for skim, review,
reproduce, teach, literature review, and evidence audit. Every evidence-bearing
cell must carry a verbatim quote from the paper, and those quotes are
machine-verified so fabricated or too-thin evidence gets flagged.
```

- [ ] **Step 2: Add workflow presets after Shared assets**

Insert after the shared assets list:

```markdown
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
```

- [ ] **Step 3: Update workflow steps**

Replace step 2:

```markdown
2. **Concept map first.** Read `reference/tables.md` and fill ONLY the
   概念-定位映射表 (concept-definition map) at the end, then emit a short text
   knowledge tree. Locking terminology first reduces downstream errors.
```

with:

```markdown
2. **Choose workflow, then concept map.** Select the workflow preset, then read
   `reference/tables.md` and fill ONLY the 概念-定位映射表 (concept-definition
   map) at the end. Emit a short text knowledge tree. Locking terminology first
   reduces downstream errors.
```

Replace step 3:

```markdown
3. **Fill tables 1–15.** One sentence per cell; unknown → `缺失`. Every
   evidence-bearing conclusion needs both a 证据来源 type AND a verbatim 原文引文
   (copied exactly from the source, never paraphrased or invented).
```

with:

```markdown
3. **Fill selected tables.** Fill only the tables selected by the workflow
   unless Full Dissection was requested. One sentence per cell; unknown →
   `缺失`. Every evidence-bearing conclusion needs both a 证据来源 type AND a
   verbatim 原文引文 (copied exactly from the source, never paraphrased or
   invented).
```

- [ ] **Step 4: Verify AGENTS wording**

Run:

```bash
rg -n "Workflow Presets|Default to Skim|Fill selected tables|Fill tables 1–15" AGENTS.md
```

Expected:

- Matches for `Workflow Presets`, `Default to Skim`, and `Fill selected tables`.
- No match for `Fill tables 1–15`.

- [ ] **Step 5: Commit AGENTS sync**

```bash
git add AGENTS.md
git commit -m "docs: sync agents workflow presets"
```

## Task 5: Final Validation

**Files:**
- No new files.

- [ ] **Step 1: Run unit tests**

```bash
make test
```

Expected: 14 tests pass.

- [ ] **Step 2: Run fake-citation demo**

```bash
make demo
```

Expected:

- command exits 0
- output includes `L1 quote-exists: 3 ok / 1 unsupported`
- output includes `VERDICT: REVIEW NEEDED`

- [ ] **Step 3: Run passing demo**

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected:

- command exits 0
- output includes `L1 quote-exists: 4 ok / 0 unsupported`
- output includes `VERDICT: PASS`

- [ ] **Step 4: Validate skill**

```bash
make validate-skill
```

Expected: `Skill is valid!`

- [ ] **Step 5: Confirm dependency boundary**

```bash
python3 - <<'PY'
from pathlib import Path
pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
assert "dependencies = []" in pyproject
assert "embedding" not in pyproject.lower()
assert "notion" not in pyproject.lower()
PY
```

Expected: no output.

- [ ] **Step 6: Check git state**

```bash
git status --short --branch
git log --oneline --decorate --max-count=8
```

Expected:

- working tree clean
- latest commits are the README, table protocol, skill, and AGENTS commits

## Self-Review

- Spec coverage: README workflow-first positioning is covered by Task 1. Table
  roles and Table 13 redesign are covered by Task 2. Skill workflow selection is
  covered by Task 3. Cross-agent alignment is covered by Task 4. Verification is
  covered by Task 5.
- Placeholder scan: no placeholder markers or unspecified implementation steps
  are used.
- Scope check: plan changes only Markdown documentation and skill instructions.
  It does not modify checker behavior or add dependencies.
