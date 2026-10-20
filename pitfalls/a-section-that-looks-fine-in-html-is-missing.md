# A section that looks fine in HTML is missing from the PDF

Date: 2026-10-20 · Tags: `html` `pandoc` `pdf` `docx` `pipelines` `verification`

## Symptom

The source page renders correctly in a browser — heading, five warning boxes, a summary
table, all visible. The generated PDF has the heading **and nothing underneath it**, and
the DOCX has the same hole:

```text
10. Traps to keep in mind
11. Quick reference
```

No error from the converter. The build "succeeded", the file exists, the page count is
plausible.

## The wrong assumption

> "If the HTML looks right, the PDF has the content."

An HTML→Markdown→PDF pipeline is a **whitelist**: every converter handles the tags it
knows and silently drops the rest. The PDF never sees your HTML — it sees the Markdown,
and the Markdown was built by a function with a fixed `if tag == …` ladder:

```python
if tag == "p":  ...
elif tag == "ul": ...
elif tag == "ol": ...
elif tag in ("div", "section"): out.extend(block_nodes(ch))   # recurse into children
# anything else: dropped without a word
```

Two shapes fell through that ladder on the same day:

- `<h3>` — not in the ladder, so every subsection title vanished (content under it stayed,
  which makes the loss harder to notice);
- `<div class="trap">bare text</div>` — a div **with no block children**, so the recursive
  branch iterated over nothing and emitted nothing.

A whitelist converter is not buggy in the "crash" sense. It is lossy by design, and the loss
is silent.

## Spot it in 5 seconds

Do not compare the PDF's *look*; compare its **text** against the source's headings:

```python
import fitz, re
pdf = "".join(p.get_text() for p in fitz.open("notes.pdf"))
for h in ["Traps to keep in mind", "Quick reference"]:
    print(h, "->", h in pdf)
```

Better: check the intermediate Markdown, which is where the loss happens:

```bash
wc -c out.md            # 12083 → 13192 after the fix: the missing 1 KB was the lost section
grep -c '^### ' out.md  # 0 while the HTML clearly had <h3>s
```

A byte count that drops when you *add* nothing is the tell; so is a section whose body is
empty while its heading survived.

## Fix

Teach the converter the shapes you actually use, and make the fallback explicit rather than
silent. For a `div` holding bare text:

```python
elif tag in ("div", "section"):
    block_kids = [c for c in ch if isinstance(c.tag, str)
                  and c.tag.lower() in ("p", "ul", "ol", "div", "section", "h3", "table")]
    if block_kids:
        out.extend(block_nodes(ch))
    else:
        txt = inline(ch).strip()        # bare-text card: emit it, don't recurse into nothing
        if txt:
            out.append(txt)
```

…plus a `h3` branch, and a table→pipe-table branch so `<table>` stops disappearing too.
Then verify by **counting what came out**, not by looking at the result:

```text
before: md 12083 bytes, 0 h3, 0 table rows, "Quick reference" body empty
after : md 13192 bytes, 5 h3, 9 table rows, every trap present
```

## Globalise it

- Any converter with a tag/type whitelist: HTML→MD, MD→AST, JSON→model, YAML→config,
  ORM→SQL. Unlisted input disappears; nothing warns.
- A recursive branch (`recurse into children`) applied to an element whose payload is its
  **own text node** — the recursion finds zero children and returns zero output.
- `git diff --stat` on a round-trip conversion: a suspiciously small diff usually means
  content was dropped, not that the conversion was clean.
- Docx/PDF QA done by eye: a missing 1 KB section inside a 6-page document is invisible
  unless you grep for its headings.
- Rule of thumb: **round-trip pipelines are lossy unless proven otherwise.** Assert on
  counts (headings, list items, table rows, equations) between source and output; treat a
  converter's silence as guilt, not innocence.

## Evidence

Same document, same day, before and after the converter fix:

```text
# before — heading survived, body did not
$ python html2md.py notes.html out.md && wc -c out.md
12083
$ grep -c "A basis must be ordered" out.md
0

# after
$ python html2md.py notes.html out.md && wc -c out.md
13192
$ grep -c "A basis must be ordered" out.md
1
```

And the regression check that made the fix safe — three unrelated documents still convert
to the same problem counts (25 / 16 / 13):

```text
hw5:   problems=25 size=40674
exam2: problems=16 size=25071
set5:  problems=13 size=27455
```

## Takeaway

The PDF knows only what the converter handed it. When a section goes missing, do not debug
the layout — read the Markdown in the middle, and count what survived.
