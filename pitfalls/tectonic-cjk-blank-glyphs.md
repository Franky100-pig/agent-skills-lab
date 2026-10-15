# CJK renders as blank boxes in the PDF

Date: 2026-10-15 · Tags: `latex` `tectonic` `pdf` `i18n`

## Symptom

A LaTeX→PDF build succeeds, no error, page count is right — but every Chinese
character is **missing**. The line still occupies space, so the layout looks
like it has gaps where words should be:

```text
Rank = ... dimension of Col(A) ... (      )
```

Extracting the text shows the truth:

```text
'English text. \uffff\uffff\uffff\uffff(\uffff) (\uffff\uffff) ...'
```

`\uffff` is the replacement character: the glyphs were asked for and the font did
not have them.

## The wrong assumption

"Chinese must be fine — it's just text." So you ship a document with invisible
parenthetical terms, or you spend a while blaming the Markdown converter.

## Spot it in 5 seconds

Build a one-line probe and read the PDF back *as text*:

```bash
printf 'English text. 中文测试 (秩) (零度).\n' > /tmp/t.md
pandoc /tmp/t.md -o /tmp/t.pdf --pdf-engine=tectonic
python -c "import fitz; print(repr(fitz.open('/tmp/t.pdf')[0].get_text()))"
```

If you see `\uffff`, the pipeline cannot render CJK. Do not trust a visual glance
at the first page — check the extracted text.

Root cause here: the engine wanted to download its font bundle
(`default_bundle_v33.tar`) and the fetch timed out, so it fell back to a bundle
without CJK coverage — **silently**.

## Fix

Pick one and be consistent:

- **Keep the exported document ASCII.** Replace the glosses with pinyin or
  English: `(秩)` → `(zhi)`, `(零度)` → `(lingdu)`. The browser/HTML view can
  keep the real characters; only the PDF/DOCX constraint forces this.
- Or install/point the engine at a CJK-capable font bundle so the fetch is not
  needed at build time.

Whatever you choose, **assert on it in the build**: after producing the PDF,
fail if `'\uffff' in extracted_text`.

## Globalise it

Any "PDF engine + font" pair. A missing glyph never raises; it renders as
nothing. The dangerous part is not the blank — it is that the build reports
success.

## Evidence

The probe above, run against a working English build:

```text
extracted: 'English text. \uffff\uffff\uffff\uffff(\uffff) (\uffff\uffff) (\uffff\uffff\uffff) (\uffff\uffff\uffff).\n1'
```

Same session, the build log carried only a warning —

```text
[WARNING] warning: failure fetching "kanjix.map" from network (1/3)
caused by: error sending request ... operation timed out
```

— and the PDF still said `pdf done`.

## Takeaway

A PDF build that "succeeds" can be missing every non-Latin glyph; verify by
extracting text, not by looking at page one.
