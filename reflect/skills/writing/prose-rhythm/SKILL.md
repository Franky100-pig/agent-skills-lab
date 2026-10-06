---
name: prose-rhythm
description: Editorial sentence-rhythm diagnostic. Measures sentence-length variation (burstiness: coefficient of variation and alternation pattern) in English prose and suggests readability-minded rhythm adjustments. Use when the user asks to assess or improve sentence rhythm, sentence-length variety, or "monotonous" writing. Read-only diagnostic by default; confirm before rewriting.
license: MIT
---

# prose-rhythm

A standalone, read-only editorial diagnostic. Human prose varies in sentence length;
mechanically uniform text reads as machine-written. This skill measures that variation —
called **burstiness** — as a plain readability signal so the user can decide whether to
adjust rhythm.

## What it does
- **Diagnose** — run `scripts/measure.py` to report sentence count, mean length,
  coefficient of variation (CV), alternation index, and a descriptive variation assessment.
- **Calibrate (only after the user opts in)** — suggest or apply greater sentence-length
  variation: merge consecutive short sentences, split over-long ones, and deliberately
  alternate short/long rhythm instead of a steady beat.

## How to run the diagnostic
```bash
<PY> scripts/measure.py "<file-or-stdin>.txt"
```
- `<PY>` = a Python 3.10+ interpreter (standard library only; no install needed).
- Reads a file path argument, or falls back to stdin.

## Calibration moves (apply only after the user explicitly opts in)
1. **Break monotony** — if CV is low (sentences similar in length), merge two shorts into
   one, or split one long into two.
2. **Alternate** — follow a long sentence with a short one; avoid 3+ sentences of the same
   length in a row.
3. **Keep meaning** — calibration must not alter facts, claims, or the user's voice beyond rhythm.

## Limitations
- Pure heuristic; the reported bands are descriptive, not validated thresholds. The CV
  reference range (≈0.45–1.1) is an illustrative editorial reference, **not** a figure derived
  from a specific corpus. Treat it as a hint, not a target.
- Does **not** guarantee any change in how automated tools score the text; it is a
  readability diagnostic, not a detector-targeting tool.
- **English prose only.** Tokenization is ASCII-oriented and assumes whitespace after
  sentence-ending punctuation (`.`, `!`, `?`); non-English text is out of scope for this version.
- Not a substitute for deeper structural editing; use alongside, not instead of.

## Try it as an experiment
```bash
echo "The cat sat. The dog ran fast. We walked slowly to the store." | <PY> scripts/measure.py -
```
Expect a low-CV "uniform" assessment. Rewrite with varied lengths and re-run to watch CV climb.
Tests: `<PY> -m unittest discover -s tests`.
