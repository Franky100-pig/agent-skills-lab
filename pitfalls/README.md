# pitfalls/ — traps I've already stepped on

Every entry here is a real trap that cost time, written down at the moment I
stopped being confused. The value is not "wow, tricky" — it is that the *next*
person (usually future me) recognises it in five seconds instead of an hour.

Each entry answers four questions **in the same order**, so you can skim only
the part you need:

| Section | Answers |
|---|---|
| **Symptom** | what you actually see |
| **The wrong assumption** | the conclusion that looks obvious and is wrong |
| **Spot it in 5 seconds** | the tell that gives it away |
| **Fix** | the concrete command / code |

…plus a **Globalise it** line (where else this trap bites) and an **Evidence**
block with real output. Evidence follows the same rule as the
[journal](../reflect/README.md): a pasted transcript is a fact, "it didn't work"
is an opinion.

## Index

| Pitfall | Tags | Date |
|---|---|---|
| [grep alternation returns a false negative](grep-alternation-false-negative.md) | `shell` `grep` `verification` | 2026-10-15 |
| [Emphasis inside an emphasis wrapper breaks the conversion](emphasis-inside-emphasis-wrapper.md) | `markdown` `pandoc` `html` | 2026-10-15 |
| [A closing math `$` must not have a space in front of it](pandoc-closing-dollar-needs-no-space.md) | `pandoc` `latex` `markdown` | 2026-10-15 |
| [CJK renders as blank boxes in the PDF](tectonic-cjk-blank-glyphs.md) | `latex` `tectonic` `pdf` `i18n` | 2026-10-15 |
| [Counting bytes in a zipped file gives false positives](binary-byte-count-false-positive.md) | `docx` `pdf` `verification` | 2026-10-15 |
| [Syncing status lies when the remote is unreachable](stale-remote-tracking-ref.md) | `git` `remote` | 2026-10-15 |
| [Plain text extraction scrambles matrices](pdf-text-extraction-scrambles-matrices.md) | `pdf` `extraction` `math` | 2026-10-15 |
| [Long-term memory gets truncated on injection, so a rule at the end is never read](long-term-memory-gets-truncated-on-injection-so.md) | `memory` `context` `agent-workflow` | 2026-10-15 |
| [doctest reports failures but prints none of them](doctest-reports-failures-but-prints-none-of-them.md) | `python` `doctest` `verification` `streams` | 2026-10-16 |
| [enumerating definitions by walking modules silently under-covers](enumerating-definitions-by-walking-modules.md) | `python` `introspection` `verification` `registries` | 2026-10-16 |
| [A tool installed under `/tmp` disappears and the build fails silently](a-tool-installed-under-tmp-disappears-and-the.md) | `toolchain` `macos` `verification` `pipelines` | 2026-10-19 |

## Add an entry

```bash
python3 new_pitfall.py "grep alternation returns a false negative"
```

This drops `pitfalls/<slug>.md` with the skeleton above and appends a row to the
index.

## Why this is not just the journal

The [journal](../reflect/README.md) is **chronological** — "what happened on
this day", read in order. A pitfall is **looked up**, not read in order, so:

- entries are named by **symptom**, not by date (the date lives inside the file);
- the same trap is never written twice — the second time you hit it you sharpen
  the existing entry instead;
- the index is the only ordered thing, and it is ordered by **tag**, not time.

That is the same split the repo already uses: `experiments/` is dated because
each one is a moment; `reflect/skills/` is topic-named because each one is
reusable knowledge. Pitfalls belong on the topic-named side.
