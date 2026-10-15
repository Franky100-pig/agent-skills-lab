# A closing math `$` must not have a space in front of it

Date: 2026-10-15 · Tags: `pandoc` `latex` `markdown` `math`

## Symptom

One sentence in a PDF shows a literal dollar sign, and the *rest of the line*
after it has been swallowed into a formula:

```text
..., which recovers $A^T e_1 = $ the first column of $A^T = $ the first row of A = [matrix]
```

The source obviously closes its math spans. The rendered output says otherwise.

## The wrong assumption

"The dollar signs are unbalanced somewhere else" — so you go hunting through the
file for a missing `$`, and the count comes back even.

## Spot it in 5 seconds

Search the source for a closing delimiter preceded by a space:

```bash
grep -n ' = \$' solutions.html
```

Writers naturally type `$A^T e_1 = $` — a space before the closing `$`, matching
how the sentence reads. Pandoc's `tex_math_dollars` extension does **not** accept
that as a closing delimiter: the closing `$` must be immediately preceded by
non-whitespace. So it keeps scanning for a later `$`, pairs the delimiters
differently, and the leftovers print literally.

## Fix

Close the span flush against the last non-space character:

```markdown
bad :  which recovers $A^T e_1 = $ the first column of ...
good:  which recovers $A^T e_1 =$ the first column of ...
```

If you want the visual gap, put the space *outside* the math span
(`$A^T e_1 =$ the first column`), never inside it.

## Globalise it

The same rule applies at the opening delimiter: `$ x $` is not mathtext. Any
time a math span looks right in a Markdown preview but wrong after conversion,
check the delimiters' inner edges before touching the formula itself.

## Evidence

```text
$ grep -n ' = \$' solutions.html
215:<li>$\operatorname{Rank}(A) = $ the number of pivots.</li>
312:...$\operatorname{rank}(A) = 5 - 2 = 3 = $ number of rows, ...
```

Two occurrences in one document, each producing one visible stray `$` in a
16-page PDF. After replacing `' = $'` with `' =$'`:

```text
$ python -c "import fitz; d=fitz.open('solutions.pdf'); print(''.join(p.get_text() for p in d).count('$'))"
0
```

## Takeaway

Markdown math delimiters are picky about their inner edges — `$ x $` is not
math, and `x = $` never closes.
