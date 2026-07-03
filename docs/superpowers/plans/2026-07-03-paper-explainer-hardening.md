# Paper Explainer Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden `paper-explainer` into a small, credible faithfulness gate for AI-generated paper notes.

**Architecture:** Keep the existing skill package as the agent-facing workflow, and add a thin engineering shell around the checker: tests, examples, Makefile, CI, and a sharper README. The checker remains a single standard-library Python script; strict L2 mode continues to be optional and isolated behind the existing `--strict` flag.

**Tech Stack:** Python 3.11+, standard library `unittest`, GNU Make, GitHub Actions, Codex skill validation script for local validation.

---

## File Structure

- Modify: `skills/paper-explainer/SKILL.md`
  - Responsibility: agent skill instructions and trigger metadata.
  - Change: remove proprietary license metadata and add a short MIT license note outside YAML frontmatter.
- Modify: `skills/paper-explainer/scripts/check_sources.py`
  - Responsibility: deterministic L1 quote-exists check, optional L2 claim-support judge, CLI reporting and exit codes.
  - Change: make strict-mode judge errors first-class review failures.
- Create: `pyproject.toml`
  - Responsibility: project metadata for GitHub/package readers; no runtime dependencies.
- Create: `tests/test_check_sources.py`
  - Responsibility: characterize L1 behavior and protect strict-mode error semantics.
- Create: `Makefile`
  - Responsibility: stable local commands for demo and tests.
- Create: `.github/workflows/test.yml`
  - Responsibility: run tests and demo on GitHub.
- Create: `examples/mini-fake-citation/source.txt`
  - Responsibility: top-level fake-citation demo source text.
- Create: `examples/mini-fake-citation/claims.json`
  - Responsibility: top-level fake-citation demo claims, including one unsupported quote.
- Create: `examples/real-paper-demo/source.txt`
  - Responsibility: realistic source excerpt for a passing demo.
- Create: `examples/real-paper-demo/claims.json`
  - Responsibility: realistic claim/quote pairs with all quotes supported.
- Create: `examples/real-paper-demo/faithfulness_report.txt`
  - Responsibility: saved PASS report for browsing.
- Create: `examples/real-paper-demo/README.md`
  - Responsibility: explain the realistic demo without sending users into `skills/`.
- Modify: `README.md`
  - Responsibility: first-screen project pitch, clone-and-run demo, boundary, workflow.

## Task 1: Metadata And Trust Baseline

**Files:**
- Modify: `skills/paper-explainer/SKILL.md`
- Create: `pyproject.toml`

- [ ] **Step 1: Run the current metadata check and confirm it fails**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

skill = Path("skills/paper-explainer/SKILL.md").read_text(encoding="utf-8")
frontmatter = skill.split("---", 2)[1]

assert "Proprietary" not in skill
assert "license:" not in frontmatter
assert Path("skills/paper-explainer/LICENSE.txt").read_text(encoding="utf-8").startswith("MIT License")
assert 'license = { text = "MIT" }' in Path("pyproject.toml").read_text(encoding="utf-8")
PY
```

Expected: FAIL because `SKILL.md` currently says `license: Proprietary...` and `pyproject.toml` does not exist.

- [ ] **Step 2: Update `skills/paper-explainer/SKILL.md` frontmatter**

Replace the current frontmatter with exactly:

```markdown
---
name: paper-explainer
description: "Use this skill whenever the user wants to deeply understand, dissect, or take structured notes on an academic paper. Triggers include: any mention of 'read this paper', 'explain this paper', 'summarize a paper', 'paper notes', 'literature review', 'lit review', 'dissect a paper', 'help me understand this arXiv/paper', a pasted arXiv link or PDF, or a request to prepare a paper for review, reproduction, or study. This skill produces a set of structured, review-ready tables (core problem, method, experiments, formulas, reproduction checklist, confidence report) where every evidence-bearing claim carries a verbatim quote from the source, so the extraction can be machine-verified for faithfulness. Do NOT use this skill for: writing or drafting a new paper, translating a paper end-to-end, general prose summarization where structure is not wanted, or non-academic documents. Prefer this skill over a freeform summary whenever the user wants to *retain*, *review*, or *reproduce* what a paper says."
---
```

Add this section at the end of the file:

```markdown
## License

MIT. See `LICENSE.txt`.
```

- [ ] **Step 3: Create `pyproject.toml`**

Create `pyproject.toml` with exactly:

```toml
[project]
name = "paper-explainer"
version = "0.1.0"
description = "Turn AI paper notes into checkable, source-grounded claims."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
  { name = "hazelian0619" }
]
dependencies = []

[project.urls]
Homepage = "https://github.com/hazelian0619/paper-explainer"
Repository = "https://github.com/hazelian0619/paper-explainer"
```

- [ ] **Step 4: Re-run the metadata check**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

skill = Path("skills/paper-explainer/SKILL.md").read_text(encoding="utf-8")
frontmatter = skill.split("---", 2)[1]

assert "Proprietary" not in skill
assert "license:" not in frontmatter
assert Path("skills/paper-explainer/LICENSE.txt").read_text(encoding="utf-8").startswith("MIT License")
assert 'license = { text = "MIT" }' in Path("pyproject.toml").read_text(encoding="utf-8")
PY
```

Expected: PASS with no output.

- [ ] **Step 5: Commit**

```bash
git add skills/paper-explainer/SKILL.md pyproject.toml
git commit -m "chore: align project metadata"
```

## Task 2: L1 Checker Characterization Tests

**Files:**
- Create: `tests/test_check_sources.py`

- [ ] **Step 1: Create the test file**

Create `tests/test_check_sources.py` with exactly:

```python
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "skills" / "paper-explainer" / "scripts" / "check_sources.py"

spec = spec_from_file_location("check_sources", CHECKER_PATH)
assert spec is not None
assert spec.loader is not None
check_sources = module_from_spec(spec)
sys.modules[spec.name] = check_sources
spec.loader.exec_module(check_sources)


class L1CheckerTests(unittest.TestCase):
    def test_normalize_unifies_quotes_dashes_and_whitespace(self) -> None:
        text = "  Robots\u2019   claims \u2014 across\nlines  "
        self.assertEqual(check_sources.normalize(text), "robots' claims - across lines")

    def test_exact_quote_match_returns_one(self) -> None:
        source = check_sources.normalize("The method improves accuracy by 50 percent.")
        quote = check_sources.normalize("The method improves accuracy by 50 percent.")
        self.assertEqual(check_sources.best_window_ratio(quote, source), 1.0)

    def test_fuzzy_match_tolerates_small_formatting_drift(self) -> None:
        source = check_sources.normalize(
            "Combining RGB-D and LiDAR mitigates the instability of vision-only systems."
        )
        quote = check_sources.normalize(
            "Combining RGB-D and LiDAR mitigates instability of vision only systems."
        )
        self.assertGreaterEqual(
            check_sources.best_window_ratio(quote, source),
            check_sources.DEFAULT_THRESHOLD,
        )

    def test_run_l1_marks_ok_unsupported_and_skipped(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            },
            {
                "table": "Table 7",
                "cell": "Fake",
                "claim": "The method gets 99 percent on ImageNet.",
                "quote": "The method gets 99 percent on ImageNet.",
            },
            {
                "table": "Table 8",
                "cell": "Limit",
                "claim": "missing",
                "quote": "missing",
            },
        ]
        report = check_sources.run_l1(
            claims,
            "The method improves accuracy by 50 percent.",
            check_sources.DEFAULT_THRESHOLD,
        )
        self.assertEqual([result.status for result in report.results], ["ok", "unsupported", "skipped"])
        self.assertEqual(len(report.checked), 2)
        self.assertEqual(len(report.unsupported), 1)

    def test_main_json_output_and_review_exit_code(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            },
            {
                "table": "Table 7",
                "cell": "Fake",
                "claim": "The method gets 99 percent on ImageNet.",
                "quote": "The method gets 99 percent on ImageNet.",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tables = tmp_path / "claims.json"
            source = tmp_path / "source.txt"
            tables.write_text(json.dumps(claims), encoding="utf-8")
            source.write_text("The method improves accuracy by 50 percent.", encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_sources.main([
                    "--tables",
                    str(tables),
                    "--source",
                    str(source),
                    "--json",
                ])

        self.assertEqual(code, 1)
        data = json.loads(stdout.getvalue())
        self.assertEqual([result["status"] for result in data], ["ok", "unsupported"])

    def test_main_pass_exit_code(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tables = tmp_path / "claims.json"
            source = tmp_path / "source.txt"
            tables.write_text(json.dumps(claims), encoding="utf-8")
            source.write_text("The method improves accuracy by 50 percent.", encoding="utf-8")

            code = check_sources.main([
                "--tables",
                str(tables),
                "--source",
                str(source),
            ])

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the characterization tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS. These tests characterize existing L1 behavior before changing strict mode.

- [ ] **Step 3: Commit**

```bash
git add tests/test_check_sources.py
git commit -m "test: cover l1 faithfulness checker"
```

## Task 3: Strict Mode Judge Error Semantics

**Files:**
- Modify: `tests/test_check_sources.py`
- Modify: `skills/paper-explainer/scripts/check_sources.py`

- [ ] **Step 1: Add the strict-mode failing test**

Insert this test class immediately before the `if __name__ == "__main__":` block in `tests/test_check_sources.py`:

```python
class StrictModeTests(unittest.TestCase):
    def test_l2_judge_errors_make_strict_mode_review_needed(self) -> None:
        class FakeMessage:
            content = [type("Content", (), {"text": "not json"})()]

        class FakeMessages:
            def create(self, **_kwargs):
                return FakeMessage()

        class FakeAnthropic:
            def __init__(self):
                self.messages = FakeMessages()

        original = sys.modules.get("anthropic")
        sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=FakeAnthropic)

        try:
            claims = [
                {
                    "table": "Table 1",
                    "cell": "Core",
                    "claim": "The method improves accuracy.",
                    "quote": "The method improves accuracy by 50 percent.",
                }
            ]
            report = check_sources.run_l1(
                claims,
                "The method improves accuracy by 50 percent.",
                check_sources.DEFAULT_THRESHOLD,
            )
            check_sources.run_l2(report, "fake-model")

            self.assertEqual(len(report.l2_errors), 1)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                check_sources.print_report(report, strict=True)

            self.assertIn("L2 supports    : 0 supported / 0 citation-swap / 1 judge-error", stdout.getvalue())
            self.assertIn("VERDICT: REVIEW NEEDED", stdout.getvalue())
        finally:
            if original is None:
                sys.modules.pop("anthropic", None)
            else:
                sys.modules["anthropic"] = original
```

- [ ] **Step 2: Run the strict test and confirm it fails**

Run:

```bash
python3 -m unittest tests.test_check_sources.StrictModeTests.test_l2_judge_errors_make_strict_mode_review_needed -v
```

Expected: FAIL with an attribute error for `l2_errors`, because the checker does not expose judge errors yet.

- [ ] **Step 3: Update `ClaimResult` in `check_sources.py`**

Change the dataclass to include `l2_error`:

```python
@dataclass
class ClaimResult:
    table: str
    cell: str
    claim: str
    quote: str
    status: str            # "ok" | "unsupported" | "skipped"
    ratio: float = 0.0
    l2_supports: bool | None = None
    l2_reason: str = ""
    l2_error: bool = False
```

- [ ] **Step 4: Add `Report.l2_errors`**

Add this property under `citation_swaps`:

```python
    @property
    def l2_errors(self) -> list[ClaimResult]:
        return [r for r in self.results if r.l2_error]
```

- [ ] **Step 5: Mark L2 exceptions as judge errors**

Replace the `except Exception as e` body in `run_l2` with:

```python
        except Exception as e:  # network / parse — report, don't crash the run
            r.l2_supports = None
            r.l2_error = True
            r.l2_reason = f"judge error: {e}"
```

- [ ] **Step 6: Update strict-mode report output and verdict**

Replace the `if strict:` block in `print_report` with:

```python
    if strict:
        swaps = report.citation_swaps
        errors = report.l2_errors
        supported = [r for r in checked if r.l2_supports is True]
        print(f"L2 supports    : {len(supported)} supported / {len(swaps)} "
              f"citation-swap / {len(errors)} judge-error")
        for r in swaps:
            print(f"  ⚠ [{r.table} · {r.cell}] quote real but does not support claim")
            print(f"      reason: {r.l2_reason}")
        for r in errors:
            print(f"  ⚠ [{r.table} · {r.cell}] L2 judge error")
            print(f"      reason: {r.l2_reason}")
```

Replace the verdict expression with:

```python
    verdict = "PASS" if not unsupported and not (
        strict and (report.citation_swaps or report.l2_errors)
    ) else "REVIEW NEEDED"
```

- [ ] **Step 7: Update CLI exit semantics**

Replace the `needs_review` assignment in `main` with:

```python
    needs_review = report.unsupported or (
        args.strict and (report.citation_swaps or report.l2_errors)
    )
```

- [ ] **Step 8: Run the strict test**

Run:

```bash
python3 -m unittest tests.test_check_sources.StrictModeTests.test_l2_judge_errors_make_strict_mode_review_needed -v
```

Expected: PASS.

- [ ] **Step 9: Run all tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add tests/test_check_sources.py skills/paper-explainer/scripts/check_sources.py
git commit -m "fix: report strict judge errors"
```

## Task 4: Top-Level Demo And Makefile

**Files:**
- Create: `examples/mini-fake-citation/source.txt`
- Create: `examples/mini-fake-citation/claims.json`
- Create: `Makefile`

- [ ] **Step 1: Create `examples/mini-fake-citation/source.txt`**

Create the file with exactly:

```text
Multimodal Perception-Driven Decision-Making for Human-Robot Interaction: a Survey.

This survey studies how robots integrate multimodal perception from vision,
language, and touch to make decisions in human-robot interaction. We review 66
papers published between 2004 and 2024 and analyze fusion frameworks, fusion
strategies (early, intermediate, late, hybrid), and decision-making methods.

Combining RGB-D and LiDAR mitigates the instability of vision-only systems in
dynamic navigation, where a single failing sensor can otherwise cause the
system to fail. In the MEAL framework, the robot learns object properties
through multimodal exploration such as observing, picking up, and shaking,
improving accuracy by 50% over single-modality baselines.

We categorize five integration architectures: pipeline, feedback-loop, modular,
end-to-end, and hybrid, and discuss the trade-off between real-time response and
fusion complexity. Foundation models such as vision-language models are an
emerging paradigm for general task planning in HRI.
```

- [ ] **Step 2: Create `examples/mini-fake-citation/claims.json`**

Create the file with exactly:

```json
[
  {
    "table": "Table 1",
    "cell": "Core problem",
    "claim": "Robots integrate multimodal perception to make better HRI decisions.",
    "quote": "how robots integrate multimodal perception from vision, language, and touch to make decisions in human-robot interaction"
  },
  {
    "table": "Table 1",
    "cell": "Key mechanism",
    "claim": "RGB-D and LiDAR mitigate instability in vision-only dynamic navigation.",
    "quote": "Combining RGB-D and LiDAR mitigates the instability of vision-only systems in dynamic navigation"
  },
  {
    "table": "Table 7",
    "cell": "Best experiment",
    "claim": "MEAL improves attribute-learning accuracy by about 50 percent over single-modality baselines.",
    "quote": "improving accuracy by 50% over single-modality baselines"
  },
  {
    "table": "Table 7",
    "cell": "Fake citation demo",
    "claim": "The method reaches 99 percent top-1 accuracy on ImageNet.",
    "quote": "our method achieves 99% top-1 accuracy on the ImageNet benchmark"
  }
]
```

- [ ] **Step 3: Create `Makefile`**

Create `Makefile` with exactly:

```makefile
PYTHON ?= python3
CHECKER := skills/paper-explainer/scripts/check_sources.py

.PHONY: demo test validate-skill

demo:
	@set +e; \
	$(PYTHON) $(CHECKER) \
		--tables examples/mini-fake-citation/claims.json \
		--source examples/mini-fake-citation/source.txt; \
	code=$$?; \
	if [ $$code -ne 1 ]; then \
		echo "Expected demo checker to exit 1 because it contains one fake citation; got $$code" >&2; \
		exit 1; \
	fi

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-skill:
	$(PYTHON) "$${CODEX_HOME:-$$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/paper-explainer
```

- [ ] **Step 4: Run the demo**

Run:

```bash
make demo
```

Expected: command exits 0 and prints a faithfulness report containing:

```text
L1 quote-exists: 3 ok / 1 unsupported
VERDICT: REVIEW NEEDED
```

- [ ] **Step 5: Run tests through Make**

Run:

```bash
make test
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add examples/mini-fake-citation/source.txt examples/mini-fake-citation/claims.json Makefile
git commit -m "feat: add runnable fake citation demo"
```

## Task 5: GitHub Actions

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/test.yml` with exactly:

```yaml
name: test

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run unit tests
        run: make test

      - name: Run fake-citation demo
        run: make demo
```

- [ ] **Step 2: Run the CI commands locally**

Run:

```bash
make test
make demo
```

Expected: both commands exit 0.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: run tests and demo"
```

## Task 6: Realistic Passing Demo

**Files:**
- Create: `examples/real-paper-demo/source.txt`
- Create: `examples/real-paper-demo/claims.json`
- Create: `examples/real-paper-demo/faithfulness_report.txt`
- Create: `examples/real-paper-demo/README.md`

- [ ] **Step 1: Create `examples/real-paper-demo/source.txt`**

Create the file with exactly:

```text
Multimodal Perception-Driven Decision-Making for Human-Robot Interaction: a Survey.

This survey studies how robots integrate multimodal perception from vision,
language, and touch to make decisions in human-robot interaction. We review 66
papers published between 2004 and 2024 and analyze fusion frameworks, fusion
strategies (early, intermediate, late, hybrid), and decision-making methods.

Combining RGB-D and LiDAR mitigates the instability of vision-only systems in
dynamic navigation, where a single failing sensor can otherwise cause the
system to fail. In the MEAL framework, the robot learns object properties
through multimodal exploration such as observing, picking up, and shaking,
improving accuracy by 50% over single-modality baselines.

We categorize five integration architectures: pipeline, feedback-loop, modular,
end-to-end, and hybrid, and discuss the trade-off between real-time response and
fusion complexity. Foundation models such as vision-language models are an
emerging paradigm for general task planning in HRI.
```

- [ ] **Step 2: Create `examples/real-paper-demo/claims.json`**

Create the file with exactly:

```json
[
  {
    "table": "Table 1",
    "cell": "Core problem",
    "claim": "Robots integrate multimodal perception to make decisions in human-robot interaction.",
    "quote": "how robots integrate multimodal perception from vision, language, and touch to make decisions in human-robot interaction"
  },
  {
    "table": "Table 1",
    "cell": "Survey scope",
    "claim": "The survey reviews 66 papers published between 2004 and 2024.",
    "quote": "We review 66 papers published between 2004 and 2024"
  },
  {
    "table": "Table 7",
    "cell": "Observed gain",
    "claim": "MEAL improves accuracy by 50 percent over single-modality baselines.",
    "quote": "improving accuracy by 50% over single-modality baselines"
  },
  {
    "table": "Table 12",
    "cell": "Architecture taxonomy",
    "claim": "The survey categorizes five integration architectures.",
    "quote": "We categorize five integration architectures: pipeline, feedback-loop, modular, end-to-end, and hybrid"
  }
]
```

- [ ] **Step 3: Generate `faithfulness_report.txt`**

Run:

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt \
  > examples/real-paper-demo/faithfulness_report.txt
```

Expected: command exits 0.

Expected file contents include:

```text
L1 quote-exists: 4 ok / 0 unsupported
VERDICT: PASS
```

- [ ] **Step 4: Create `examples/real-paper-demo/README.md`**

Create the file with exactly:

````markdown
# Realistic Passing Demo

This demo shows the positive path: every claim has a quote that appears in the source text.

Run:

```bash
python3 ../../skills/paper-explainer/scripts/check_sources.py \
  --tables claims.json \
  --source source.txt
```

Expected:

```text
L1 quote-exists: 4 ok / 0 unsupported
VERDICT: PASS
```

Use this demo when you want to inspect the shape of a clean claim/quote file. Use `../mini-fake-citation/` when you want to see the checker catch a fabricated quote.
````

- [ ] **Step 5: Run both demos**

Run:

```bash
make demo
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected: `make demo` exits 0 while showing `REVIEW NEEDED`; the real-paper demo exits 0 while showing `PASS`.

- [ ] **Step 6: Commit**

```bash
git add examples/real-paper-demo/source.txt examples/real-paper-demo/claims.json examples/real-paper-demo/faithfulness_report.txt examples/real-paper-demo/README.md
git commit -m "docs: add passing paper demo"
```

## Task 7: README Repositioning

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md`**

Replace `README.md` with exactly:

````markdown
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
````

- [ ] **Step 2: Run README command checks**

Run:

```bash
make demo
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected: both documented commands work.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: reposition readme around faithfulness gate"
```

## Task 8: Final Validation Pass

**Files:**
- No new files. Validate the complete branch.

- [ ] **Step 1: Run unit tests**

Run:

```bash
make test
```

Expected: PASS.

- [ ] **Step 2: Run fake-citation demo**

Run:

```bash
make demo
```

Expected: command exits 0 and prints:

```text
VERDICT: REVIEW NEEDED
```

- [ ] **Step 3: Run passing demo**

Run:

```bash
python3 skills/paper-explainer/scripts/check_sources.py \
  --tables examples/real-paper-demo/claims.json \
  --source examples/real-paper-demo/source.txt
```

Expected: command exits 0 and prints:

```text
VERDICT: PASS
```

- [ ] **Step 4: Run local skill validation**

Run:

```bash
make validate-skill
```

Expected:

```text
Skill is valid!
```

- [ ] **Step 5: Confirm no heavy dependencies were added**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
assert "dependencies = []" in pyproject
assert "embedding" not in pyproject.lower()
assert "notion" not in pyproject.lower()
PY
```

Expected: PASS with no output.

- [ ] **Step 6: Review changed files**

Run:

```bash
git status --short
git log --oneline --decorate --max-count=10
```

Expected: working tree is clean after all task commits.

- [ ] **Step 7: Final branch summary**

Prepare a summary with:

- The new commands: `make test`, `make demo`, `make validate-skill`.
- The strict-mode fix: L2 judge errors now make strict runs review-needed.
- The demo story: one failing fake-citation demo and one passing realistic demo.
- The README repositioning: faithfulness gate, not general summarizer.
