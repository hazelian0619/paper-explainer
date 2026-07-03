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
