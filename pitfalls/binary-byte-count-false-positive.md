# Counting bytes in a zipped file gives false positives

Date: 2026-10-15 · Tags: `docx` `pdf` `verification` `false-positive`

## Symptom

You verify that a generated document has no leftover math delimiters, by counting
them the quick way — in the raw bytes:

```python
open('answers.docx','rb').read().count(b'$')   # 56
open('answers.pdf','rb').read().count(b'$')    # 180
```

56 and 180 stray dollar signs! Time to go re-read the converter.

But the rendered document is clean. Every one of those bytes is noise.

## The wrong assumption

"Raw bytes are the file. If the byte count says there are 180 `$`, there are
180 `$`."

`$` is a perfectly ordinary byte value, and it shows up inside *compressed
streams*. A `.docx` is a ZIP archive; a `.pdf` is full of Flate-compressed
objects. Counting bytes counts the archive, not the writing.

## Spot it in 5 seconds

Count the same character in the **decoded content** instead of the container:

```python
import zipfile
xml = zipfile.ZipFile('answers.docx').read('word/document.xml').decode()
xml.count('$')          # 0  <- this is the number that means something
```

If the decoded count is 0 while the byte count is large, the byte count was
measuring the compression.

## Fix

Extract the text and count there:

```python
# PDF
import fitz
text = ''.join(p.get_text() for p in fitz.open('answers.pdf'))
assert text.count('$') == 0

# DOCX
import zipfile
xml = zipfile.ZipFile('answers.docx').read('word/document.xml').decode()
assert xml.count('$') == 0
```

Make that assertion part of the build, so "0 leaks" is checked rather than
eyeballed.

## Globalise it

The general mistake: **verifying a logical property against a physical
representation.** Other instances — grepping a binary for a string, checking a
zip is "valid" by file size, confirming a commit happened by looking at the
working tree instead of `git log`. Always ask: which layer does this number
actually describe?

## Evidence

Same file, same character, two measurement layers:

```text
answers.docx  二进制 b'$' 计数 : 56
answers.docx  正文 XML 里 '$'    : 0
answers.pdf   抽文本 '$'         : 0
answers.pdf   二进制 b'$' 计数   : 180
```

The document had **zero** stray delimiters. The binary counts were 56 and 180×
too high — and both were *pure* false positives, which is the worst ratio.

## Takeaway

Count characters in decoded text, never in the container — compressed streams are
full of ordinary byte values that mean nothing.
