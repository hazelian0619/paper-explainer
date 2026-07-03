# Paper Explainer Faithfulness Gate Design

## Decision

Position `paper-explainer` as a small, hard engineering project: a faithfulness gate for AI-generated paper notes.

The project should not present itself as another paper summarizer. Its memorable promise is:

> Turn AI paper notes into checkable claims.

Chinese supporting copy:

> 让每条 AI 论文笔记都有原文证据。

## Target Audience

Primary audience: developers and researchers who already use AI to read papers, but do not trust generated citations or claims.

Secondary audience: agent and skill builders who want a compact example of a useful skill with real validation logic, not just prompt text.

The first release should optimize for GitHub trust: a visitor should clone the repo, run one command, and see a fake citation get caught.

## Product Boundary

The project should stay narrow:

- Accept source text plus structured claim/quote pairs.
- Verify whether quoted evidence appears in the source.
- Optionally judge whether a real quote supports the attached claim.
- Package the workflow as a skill for agent environments.
- Provide examples that make the failure mode obvious.

The project should not expand into a full paper-reading platform in the first hardening pass.

Out of scope:

- Web UI
- Notion export
- Paper library management
- Embedding search
- Heavy PDF parsing
- Broad RAG workflows
- One-click "read all papers" automation

## Core Flow

```text
paper text + AI paper notes
        |
        v
claim/quote JSON
        |
        v
check_sources.py
        |
        v
PASS / REVIEW NEEDED
```

The important demonstration is negative evidence: the tool must visibly catch a plausible but unsupported quote.

## Repository Shape

Keep the existing skill package, but add a small engineering shell around it:

```text
paper-explainer/
├── README.md
├── pyproject.toml
├── Makefile
├── tests/
├── examples/
│   ├── mini-fake-citation/
│   └── real-paper-demo/
├── skills/paper-explainer/
│   ├── SKILL.md
│   ├── reference/tables.md
│   └── scripts/check_sources.py
└── .github/workflows/test.yml
```

The top-level `examples/` directory should serve humans browsing GitHub. The skill-local examples can remain, but the repo should not make users dig into `skills/` to understand the project.

## Required First-Pass Changes

1. Fix license metadata so `SKILL.md`, plugin metadata, and repository license all say MIT.
2. Add unit tests for quote normalization, exact matches, fuzzy OCR-style matches, missing markers, unsupported quotes, JSON output, and non-zero exit behavior.
3. Fix strict-mode semantics so L2 judge errors are visible and cannot silently produce a misleading pass.
4. Add `make demo` to reproduce the fake-citation example in one command.
5. Add `make test` and GitHub Actions.
6. Add one realistic paper demo with source text, filled claim/quote JSON, and a saved faithfulness report.
7. Rewrite the README first screen around pain, proof, command, and boundary:
   - Pain: AI paper summaries fabricate evidence.
   - Proof: a plausible fake citation is flagged.
   - Command: clone and run the demo.
   - Boundary: this is a faithfulness gate, not a general summarizer.

## Design Principles

- Be stricter than a summarizer. If evidence is missing, say missing.
- Prefer deterministic checks before LLM judgment.
- Keep dependencies minimal.
- Make failure states first-class and visible.
- Preserve the skill format, but do not let skill packaging hide the CLI value.
- Add only features that strengthen trust or make the core demo easier to run.

## Acceptance Criteria

A first hardening release is ready when all of the following are true:

- `make demo` runs from a clean clone and shows one intentionally unsupported quote.
- `make test` passes locally.
- GitHub Actions runs the same tests.
- The README explains the project in under one screen before detailed rationale.
- The strict-mode behavior reports L2 errors honestly.
- The skill still validates with Codex skill validation.
- The repo has no new heavy dependencies.

## Recommended Implementation Order

1. Metadata and trust fixes.
2. Unit tests around the existing checker.
3. Strict-mode error semantics.
4. Makefile and CI.
5. Top-level examples and demo report.
6. README rewrite.
7. Skill validation pass.

This order makes the project more credible before making it louder.
