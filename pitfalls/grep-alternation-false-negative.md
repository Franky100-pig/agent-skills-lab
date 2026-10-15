# `grep -c 'a\|b'` returns 0 while the file clearly contains both

Date: 2026-10-15 · Tags: `shell` `grep` `verification` `false-negative`

## Symptom

You check that a file really contains what you just wrote:

```bash
grep -c 'backToCats\|sideTitle' notes.html
# 0
```

Zero. But you *just* wrote both strings into that file, and opening it shows
them.

## The wrong assumption

"We never wrote it / the edit silently failed / the build is stale."

This is the expensive part. The signal is wrong, so it sends you off redoing —
or "fixing" — work that already succeeded.

## Spot it in 5 seconds

Re-run it as **two single-pattern greps**:

```bash
grep -c 'backToCats' notes.html   # 2
grep -c 'sideTitle'  notes.html   # 1
```

If the single patterns match and the alternation did not, it was never a content
problem.

## Fix

Never use `\|` alternation for a **verification** grep. Two safe options:

- run one single-pattern grep per thing you want to confirm;
- or use a tool that takes a real regex and does not depend on the shell handing
  the pattern through literally (an editor / agent's own Grep tool).

The bit that actually matters: **an alternation grep is fine for exploring,
never for proving.** When a check comes back "nothing found", that is a claim
about your command as much as about the file.

## Globalise it

Any check whose *pattern syntax* is passed through a shell quoting layer can
fail this way — `find -name 'a|b'`, `rg 'a|b'` inside a wrapper, `grep -E` vs
`grep` differences. In general: if a negative result would cause you to redo
work, confirm the negative with a second, *differently-shaped* command before
acting on it.

## Evidence

Real session, verbatim, in that order:

```text
$ grep -c 'backToCats\|sideTitle' web/notes.html
0
$ grep -c 'backToCats' web/notes.html
2
$ grep -c 'sideTitle'  web/notes.html
1
```

The same pattern produced a false negative **three times in one day**, each time
briefly suggesting a file was missing content that was in fact present.

## Takeaway

Before believing "it's not in the file", re-ask the question with a single
pattern — the bug may be in the question.
