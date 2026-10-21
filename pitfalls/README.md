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

## Index — problem → fix, one line each

Skim this table; open a file only when a line matches what you are looking at.
Each file has the full story: how it fooled me, the 5-second tell, real output.

| The problem | The fix | Entry |
|---|---|---|
| `grep` returns 0 while the file clearly contains the string — either because the pattern used `a\|b` alternation, or because plain `grep` matches nothing in some `web/*.js` files | Re-ask with a **single** pattern, then with a **different tool** (Grep tool / `rg`); never prove a negative with an alternation grep | [grep returns 0 while the file contains it](grep-alternation-false-negative.md) |
| A wrapper element that is already bolded (`p.ans`, `div.meta`) gets **another** emphasis marker inside, and the parser can no longer close it — literal `**` leaks into the PDF | Inside an already-wrapped container use `<em>` only (`.ans` → `<em>`, `.meta` → `<code>`), never `<strong>` | [Emphasis inside an emphasis wrapper breaks the conversion](emphasis-inside-emphasis-wrapper.md) |
| `$x = $` is not recognised as closed math, so the parser swallows the following text into the formula | Close with `=$` — no space before the closing `$` | [A closing math `$` must not have a space in front of it](pandoc-closing-dollar-needs-no-space.md) |
| Chinese text renders as blank boxes in the PDF while the build reports success | Keep CJK out of PDFs (transliterate / use English) or install the font bundle; check extracted text for `\uffff` | [CJK renders as blank boxes in the PDF](tectonic-cjk-blank-glyphs.md) |
| Counting `$` in a `.docx`/`.pdf` shows dozens of hits although the document has none — the bytes sit in the zip container, not the text | Extract the text first (`word/document.xml`, `fitz`), then count | [Counting bytes in a zipped file gives false positives](binary-byte-count-false-positive.md) |
| `git status` says "ahead by 17" while the branch is actually **behind** — the tracking ref points at a dead remote | `git fetch <remote>`, then compare against `<remote>/main`; never trust the tracking ref | [Syncing status lies when the remote is unreachable](stale-remote-tracking-ref.md) |
| Copy-pasted text from a PDF scrambles matrix entries, so you solve numbers that are not on the page | Rebuild rows/columns from word **coordinates** (`get_text("words")`, group by `y`, sort by `x`) | [Plain text extraction scrambles matrices](pdf-text-extraction-scrambles-matrices.md) |
| A rule written at the end of a 70 KB memory file is never read — injection keeps only the first ~6 KB, silently | Put permanent rules at the **top**; move detail into separate files; keep the main file small | [Long-term memory gets truncated on injection](long-term-memory-gets-truncated-on-injection-so.md) |
| `doctest` reports failures but prints none of the failing output, so the report is useless | Capture stdout/stderr per example and print them, or run the examples explicitly | [doctest reports failures but prints none of them](doctest-reports-failures-but-prints-none-of-them.md) |
| Walking modules to enumerate definitions silently misses ones created dynamically or imported indirectly | Enumerate from an explicit registry, then assert the count you expect | [enumerating definitions by walking modules silently under-covers](enumerating-definitions-by-walking-modules.md) |
| A build that worked last week produces no output file and the log looks clean — the binary lived in `/tmp` and was cleaned up; the filter hid the error | Install tools outside `/tmp`; decide success by **the artifact existing**, not by the log | [A tool installed under `/tmp` disappears and the build fails silently](a-tool-installed-under-tmp-disappears-and-the.md) |
| CSS changes go live but readers keep the old styles — the `?v=` hash only covered JS while the styles are inline in the HTML | Include the page sources in the hash input, or ship CSS as its own cache-busted file | [A cache-bust hash that only covers JS leaves new CSS invisible](a-cache-bust-hash-that-only-covers-js-leaves.md) |
| Every "remote" file reads as 0 bytes and every comparison says DIFF — the host was unreachable, not empty | Always print `%{http_code}`; compare `git hash-object` with the API blob sha instead of downloading bodies | [An unreachable file looks exactly like an empty file](an-unreachable-file-looks-exactly-like-an-empty.md) |
| A server started with a trailing `&` answers once, then is gone by the next command (`ERR_CONNECTION_REFUSED`) | Use a managed background runner that owns the process; probe from a *different* command | [A server started with a trailing `&` is gone by the next command](a-server-started-with-a-trailing-ampersand-is.md) |
| A section renders in the browser but the PDF/DOCX has only its heading — the converter silently drops tags it does not know (`h3`, `table`, bare-text `div`) | Teach the converter those shapes, then **assert on counts** (headings / table rows / equations) between source and output | [A section that looks fine in HTML is missing from the PDF](a-section-that-looks-fine-in-html-is-missing.md) |
| curl preflight check shows CORS headers, but the browser still fails with `Failed to fetch` | `Access-Control-Allow-Headers: *` never covers `Authorization` (must be listed explicitly); curl never runs the CORS check, so a "passing" curl preflight proves nothing | [curl says the CORS preflight is fine but the browser still fails with Failed to fetch](curl-says-the-cors-preflight-is-fine-but-the.md) |
| `gh release create` with a 100 MB+ asset is SIGTERM'd at 120 s and leaves a **draft with zero assets** (the `untagged-<id>` URL is the tell) | Split it: create (no asset) → `gh release upload` in the background → `gh release edit --draft=false --latest`; a draft owns **no git tag** until you publish it | [gh release create gets killed at two minutes and leaves a draft with no asset](gh-release-create-gets-killed-at-two-minutes.md) |
| The action that should hand a frozen object back to the simulation does nothing — the flag flips, the behaviour never changes | The integrator skips **hovered** objects, and hover is set by the pointer you are using to press the key; clear every flag the downstream guard reads, then prove the test can fail by reverting the fix | [Unpinning does nothing because the pointer is still on the card](unpinning-a-card-does-nothing-because-the.md) |
| A rope constrains distance but not direction, so the free angle has tangential stiffness of only `F/r` (~0.6 at 400px) — the whole scene orbits for tens of seconds, and *raising damping makes it slower* | Damping cannot settle a mode with no restoring force; add a deliberately weak restoring term for the free direction (30 vs the constraint’s 60) and push its reaction into the parent | [A free swing angle orbits forever, and damping only makes it worse](a-body-with-a-free-swing-angle-orbits-forever.md) |
| `cannot spawn node ENOENT` right after sanitising `PATH`, and then the electron zip download hangs to a 600 s timeout that never says *blocked* | **Prepend** the node directory to the existing `PATH` (never replace it), and set `ELECTRON_MIRROR` — a hang is unreachability, not slowness, so probe with a short `curl -I` instead of waiting | [electron-builder cannot spawn node, and the electron zip download times out](electron-builder-cannot-spawn-node-and-the.md) |
| `capturePage()` returns a frame the compositor has not drawn yet (~1 in 3); on a dark theme it looks like a crash, on a light theme like missing cards — and the DOM is perfectly fine | Wait **two `requestAnimationFrame`s**, then measure the ink ratio and retry when it is too low; a fixed sleep only hides the race | [A screenshot comes back blank or half-drawn even though the page is fine](a-screenshot-comes-back-blank-or-half-drawn.md) |
| `curl https://raw.githubusercontent.com/...` returns `http=000 size=0` and you read that as *the push did not land* — `000` means **no response**, not an empty body | Verify GitHub with `gh api repos/<o>/<r>/contents/<path>` instead, and compare **digests** rather than byte counts when the bytes have to be exact | [raw.githubusercontent.com times out, so you cannot check whether a file was pushed](raw-githubusercontent-com-times-out-so-you.md) |
| A panel reports `visible: true` but `cards: 0`, intermittently — the list is filled inside a `.then()` and the test asserted on the DOM before the promise resolved | Have any async-triggering function **return its promise** and await it at the call site; assert on the model first, then on the pixels | [A test asserts on a list that an async render has not drawn yet](a-test-asserts-on-a-list-that-an-async-render.md) |

Tags in use: `shell` `grep` `markdown` `pandoc` `latex` `pdf` `verification` `git`
`memory` `python` `web` `caching` `network` `processes`.

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
