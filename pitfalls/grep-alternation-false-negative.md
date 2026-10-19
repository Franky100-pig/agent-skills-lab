# `grep` returns 0 while the file clearly contains it

Date: 2026-10-15 · Tags: `shell` `grep` `verification` `false-negative`

> One symptom, two causes. **Cause A** is the pattern (alternation through a shell quoting
> layer). **Cause B** is the tool itself — plain `grep` in this environment silently matches
> nothing in some files. Both read as "the content is not there", so both are handled by the
> same reflex: re-ask with a differently-shaped command before believing the negative.

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

## Cause B: plain `grep` matches nothing in some files

Not every false negative is about the pattern. In this environment, a **single-pattern**
`grep` through the shell can return nothing at all for files that demonstrably contain the
string — while a dedicated search tool finds it immediately:

```bash
grep -n "<style" web/index.html      # (empty)
grep -c "focus-visible" web/app.js    # 0, while the file has the rule
```

Same file, same moment, different tool:

```text
Grep tool, pattern "style|body|script", path web/index.html
→ line 30: <style>
→ line 60: html, body { min-height: 100%; }
```

Why this happens is not worth chasing (binary-heuristic, wrapper, encoding — it varies by
host). What matters is the *shape* of the failure: **an empty result, no error, exit status
that looks fine.** It has been observed repeatedly on `web/*.js` and `tools/*.js`, so treat
"shell grep says 0" as unproven for those trees.

Fix for cause B: use the agent's Grep tool (or `rg` via a tool that returns real status
codes) when the answer will decide whether you rewrite working code. Keep shell `grep` for
poking around in output you are already looking at.

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

It happened twice more on 2026-10-16, which is the point of writing it down:
knowing the trap is not the same as avoiding it. Both times the pattern was
`grep -n "foo\|bar" file`, and both times the output was empty rather than
wrong — an empty result reads as "nothing there", not as "bad question". The
second occurrence was *while checking this very file's index*, which is the
most re-usable form of the lesson: the trap fires hardest exactly when you are
verifying something you already believe.

2026-10-19, cause B, with no alternation anywhere in sight:

```text
$ grep -n "<style\|<body\|<script" web/index.html
# (empty)                        ← would have said "this file has no <style>"

# Grep tool, same file, same second
web/index.html:30:<style>
web/index.html:60:  html, body { min-height: 100%; }
web/index.html:10:<script src="i18n.js"></script>
```

That check was the *first* step of an edit I was about to make. Believing it would have
meant "adding" a style block that already existed.

## Takeaway

Before believing "it's not in the file", re-ask the question with a single
pattern — and if it is still empty, re-ask it with a different tool. The bug may be
in the question, or in the asking.
