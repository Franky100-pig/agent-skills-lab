# Emphasis inside an emphasis wrapper breaks the conversion

Date: 2026-10-15 · Tags: `markdown` `pandoc` `html` `docx` `pdf`

## Symptom

An HTML → Markdown → PDF/DOCX pipeline renders literal `**` in the output. The
document looks fine in the browser; only the exported file is wrong:

```text
All three conditions hold, so V is** a subspace of R3.
...
free variables).**
```

Or the same thing with single asterisks: `Solutions: *solutions.pdf**`.

## The wrong assumption

"The Markdown converter is buggy" — so you go and read its source, or you escape
the asterisks by hand, and it comes back the next time you add a paragraph.

## Spot it in 5 seconds

Ask: **is this paragraph already wrapped in emphasis by the converter?**

Two containers are the usual culprits, because a converter wraps their whole
text and *then* converts the inline tags inside them:

| Container | Wrapped as | So an inner tag collides |
|---|---|---|
| `<p class="ans">` | `**…**` | `<strong>` → another `**` |
| `<div class="meta">` | `*…*` | `<em>` → another `*` |

A dash of Markdown theory explains it: `**a $V$ **is** b**` does not nest. The
closing `**` in front of `is` is preceded by a space, so it is not "right
flanking" and cannot close the first pair — the delimiters pair up wrongly and
whatever is left over is printed literally.

## Fix

**Do not put inline emphasis inside a container that is itself wrapped.**
The wrapper already provides the emphasis, so the inner tag was redundant anyway:

```html
<!-- breaks: .ans is wrapped in ** already -->
<p class="ans">$V$ is <strong>not</strong> a subspace</p>

<!-- fine: <em> becomes *, which does not collide with ** -->
<p class="ans">$V$ is <em>not</em> a subspace</p>

<!-- fine: <code> becomes `…`, also collision-free -->
<div class="meta">Solutions: <code>solutions.pdf</code></div>
```

If you want bold inside a wrapper that emits `**`, use `<em>`/`<code>`; if you
want italic inside a wrapper that emits `*`, use `<strong>`/`<code>`.

## Globalise it

Any layer that generates markup *around* markup you also control. The general
rule: before adding inline formatting, ask what wrapper the surrounding element
already emits, and pick a marker that cannot collide with it.

## Evidence

A 25-question answer key produced **18** literal `**` leaks; a 13-question set
produced **2**; a one-line `<div class="meta">` produced **1** `*` leak. All
disappeared after replacing the inner tags:

```python
# .ans paragraphs are wrapped in ** by the converter -> inner <strong> collides
for ln in html_lines:
    if 'class="ans"' in ln and '<strong>' in ln:
        ln = ln.replace('<strong>', '<em>').replace('</strong>', '</em>')
```

Verification became part of the build: extract text from the produced PDF and
assert `'**' not in text`.

## Takeaway

When a converter wraps an element in `**…**`, every `<strong>` inside it is a
bug — the wrapper already said "bold".
