# Realistic Passing Demo

This demo shows the positive path: every claim has a quote that appears in the source text.

The source is a realistic synthetic excerpt for demonstrating source-grounded checking, not a full paper artifact.

From the repo root, run:

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

Use this demo when you want to inspect the shape of a clean claim/quote file. The `../mini-fake-citation/` demo intentionally uses the same source excerpt shape, but corrupts one claim so you can see the checker catch a fabricated quote.
