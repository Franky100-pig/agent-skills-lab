# Plain text extraction scrambles matrices

Date: 2026-10-15 · Tags: `pdf` `extraction` `math` `verification`

## Symptom

You pull the text out of a maths worksheet to re-solve its problems, and the
matrices come out as a vertical list of numbers:

```text
A =
1
2
0
2
0
3
0
1
2
0
-1
0
0
4
0
2
```

Re-assembling that by eye is guesswork — and the guess is wrong often enough to
matter. Worse, the wrong reading looks *plausible*: the row shapes are right,
only some entries have slid sideways.

## The wrong assumption

"The numbers are listed in reading order, so I just chunk them into rows."

Text extraction returns glyphs in **its own order**, not yours. Worse, minus
signs are often emitted as separate positioned items, so they arrive out of
sequence relative to the digits they belong to.

## Spot it in 5 seconds

Do not chunk the flat list — regroup by **geometry**. Ask for each token's
position and rebuild rows by y, then sort by x:

```python
import fitz
words = fitz.open('sheet.pdf')[page].get_text('words')   # (x0, y0, x1, y1, text, ...)
rows = {}
for x0, y0, x1, y1, w, *_ in words:
    rows.setdefault(round(y0), []).append((x0, w))
for y in sorted(rows):
    print(' '.join(w for _, w in sorted(rows[y])))
```

Now the matrix comes back as rows that line up, including the minus signs.

## Fix

Extract **with coordinates** for anything tabular (matrices, tables, aligned
columns). Use the flat `get_text()` only for prose.

And then close the loop: after rebuilding the matrix, **verify it against
something the worksheet already asserts** before you build on it. A supplied
RREF, a stated rank, or a given determinant is a free checksum.

## Globalise it

Any layout-carrying document flattened to a stream — PDF tables, spreadsheet
cells pasted as text, terminal output that was column-aligned. The data survives;
the *structure* is what you lose. If position matters, extract position too.

## Evidence

A problem supplied both a matrix and its RREF. The flat extraction gave row 3 as
`[0, 0, 0, 1, 3]`, which produced an RREF inconsistent with the given one
(rank 4 vs the stated rank 3) — briefly suggesting the *worksheet* had an error.

Rebuilt from word coordinates, row 3 was `[0, 0, 1, 3, 1]`, and then:

```text
rref(A)      = [[1, 2, 0, -1, 0], [0, 0, 1, 3, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]]
given R      = [[1, 2, 0, -1, 0], [0, 0, 1, 3, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]]
MATCH? True
```

The worksheet was correct; the extractor had moved one entry one column left.

## Takeaway

Never hand-rebuild a matrix from a flat text dump — extract positions, rebuild by
coordinates, and let the problem's own stated result check your reading.
