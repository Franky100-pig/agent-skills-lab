---
name: prose-lexical-variety
description: Editorial lexical-variety diagnostic. Estimates a perplexity proxy (lexical surprise via type-token ratio, rare-word ratio, self-entropy) for English prose and suggests readability-minded variety adjustments. Use when the user asks to assess or improve lexical variety, reduce over-smooth wording, or check "predictable" writing. Read-only diagnostic by default; confirm before rewriting.
license: MIT
---

# prose-lexical-variety

Prose that is over-smooth and predictable tends to read as machine-written. Human writing
usually shows more lexical surprise. This skill estimates a **perplexity proxy** with no
external model and reports it as an editorial lexical-variety signal.

> **Note:** a true perplexity score needs an LLM API. This skill uses lightweight stylometric
> proxies — type-token ratio, rare-word ratio against a common-word list, and character-bigram
> self-entropy. Treat the numbers as *directional*, not exact.

## What it does
- **Diagnose** — run `scripts/measure.py` for TTR, rare-word ratio, self-entropy, and a variation assessment.
- **Calibrate (only after the user opts in)** — raise lexical variety without breaking clarity:
  replace vague common words with precise/concrete ones, vary syntax, add specifics.

## How to run the diagnostic
```bash
<PY> scripts/measure.py "<file-or-stdin>.txt"
```
- `<PY>` = a Python 3.10+ interpreter (standard library only; no install needed).

## Calibration moves (apply only after the user explicitly opts in)
1. Swap generic verbs/nouns for specific ones (e.g., "utilize" → "wield", "thing" → a named entity).
2. Vary sentence openers and clause order.
3. Add concrete detail where the text is abstract — but never invent facts.

## Limitations
- Proxy only; real perplexity requires an LM.
- The reported bands are descriptive, not validated thresholds. The TTR and rare-word
  cutoffs are illustrative editorial references, **not** figures derived from a specific corpus.
- More "surprise" is not always better — over-rare words hurt readability.
- **English prose only.** Tokenization accepts only `[a-z']+`; non-English text is out of scope for this version.
- Does **not** guarantee any change in how automated tools score the text; it is a readability diagnostic, not a detector-targeting tool.

## Try it as an experiment
```bash
echo "The thing is good. We use it. It is a big thing." | <PY> scripts/measure.py -
```
Expect a low TTR / low rare-word "low variety" assessment. Swap generic words for concrete ones and re-run to see variety rise.
Tests: `<PY> -m unittest discover -s tests`.
