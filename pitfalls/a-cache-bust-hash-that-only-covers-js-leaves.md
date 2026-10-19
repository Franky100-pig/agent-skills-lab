# A cache-bust hash that only covers JS leaves new CSS invisible

Date: 2026-10-19 · Tags: `web` `caching` `build` `deploy` `css`

## Symptom

A stylesheet-only change is committed, pushed and deployed — and the rebuild prints its
usual success line. But the cache-bust token is **exactly the same as before the change**:

```text
built -> .../la-preview
core modules: ...
?v=91c00843          # same value as the previous build, before any CSS was touched
```

Anyone who already visited the site keeps the old inline `<style>` block; the new one
only appears after a hard refresh or when the HTML's cache lifetime expires.

## The wrong assumption

> "The build hashes the content and appends `?v=…`, so a redeploy always busts the cache."

The hash was real, but its **input was incomplete**. The build only hashed the
JavaScript bundles:

```python
blob = core_json + BRIDGE + web_app_js + ai_help_js + i18n_js + notes_js ...
```

In this project every page keeps its CSS **inline in the `<style>` block of the HTML**
(so a single file stays self-contained and no extra request is needed). Inline CSS is
part of the HTML document, and the HTML document was not an input to the hash — so
"change CSS only" produced an identical token. A cache-buster that does not cover the
bytes that changed busts nothing.

## Spot it in 5 seconds

After a build, compare the token against the previous one **when the only change was CSS**:

```bash
grep -o '?v=[a-f0-9]\{8\}' la-preview/index.html | sort -u   # unchanged = broken
```

The general question to ask about any content hash: *does its input set contain every
file I just edited?* If the answer is "well, the JS…", it does not.

## Fix

Add the documents that carry the styles (and any other shipped text) to the hash input:

```python
# before: only JS
blob = core + BRIDGE + js_bundles

# after: pages too — their <style> blocks are part of what ships
pages_html = "".join(read(n) for n in ("index.html", "notes.html", "ai-help.html"))
blob = core + BRIDGE + js_bundles + pages_html
```

Then re-check that the token actually moves:

```text
?v=91c00843   # before
?v=0e15776e   # after — CSS-only change now busts the cache
```

Alternative if you would rather not hash HTML: keep the CSS in its own `.css` file, give
*that* file a `?v=` query, and let the HTML stay cacheable — one URL per asset, one token
per asset, no guessing which container swallowed your change.

## Globalise it

- Inline `<style>` / inline `<script>` blocks: they ride in the HTML, so any per-asset
  cache busting silently misses them.
- SVG sprites or JSON configs pasted into the page template — same blind spot.
- CDN rules that cache HTML but not assets (or the reverse): the token changes while the
  document does not, and the browser keeps resolving the old document.
- A "content hash" computed over a hand-written file list: the day someone adds a file,
  the hash stops describing the build. Derive the list from the directory, not from memory.
- Rule of thumb: **a cache buster must be computed from exactly the set of bytes that
  ships.** If a part of the payload is not in the hash, that part is permanently cached
  at whatever the user first downloaded.

## Evidence

Real build output from this project, before and after the fix:

```text
# CSS-only commit, old build script
$ python tools/build_preview.py && grep -o '?v=…' la-preview/index.html
built -> .../la-preview
?v=91c00843        # identical to the previous deploy

# after adding pages_html to _content_version()
$ python tools/build_preview.py && grep -o '?v=…' la-preview/index.html
built -> .../la-preview
?v=0e15776e        # moves with the CSS
```

## Takeaway

A cache-bust token is only as good as its input set — if the changed bytes are not in the
hash, the deploy reached the server and never reached the reader.
