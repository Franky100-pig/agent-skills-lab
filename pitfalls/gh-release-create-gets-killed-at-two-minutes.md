# gh release create gets killed at two minutes and leaves a draft with no asset

Date: 2026-10-21 · Tags: `gh` `release` `timeout` `large-asset`

## Symptom

`gh release create v0.2.1 dist/cardwall-0.2.1-arm64.dmg` (123 MB) dies with a
signal, and the *next* command shows a release that looks created but is
empty:

```text
$ gh release create v0.2.1 dist/cardwall-0.2.1-arm64.dmg --title "..." --notes-file notes.md
-rw-r--r-- 1 staff 123M dist/cardwall-0.2.1-arm64.dmg
zsh: terminated  gh release create …

$ gh release view v0.2.1 --json assets,name,url
{"assets":[],"name":"cardwall v0.2.1 — 漂浮卡片墙","url":"…/releases/tag/untagged-fa8844…"}
```

Note the `untagged-…` URL: the draft has a *name* but no tag ref yet, which is
how you can tell it never finished.

## The wrong assumption

"The release failed, so nothing was created — re-run the same command." It did
create a **draft with zero assets**. Re-running `release create` for the same
tag then argues with that draft, and you end up debugging `422 already_exists`
on top of the original timeout.

The other wrong assumption: "the upload must be broken / rate-limited." It is
only slow — 123 MB over a proxy took ~4 minutes, past the 2-minute command
ceiling. The process got SIGTERM'd mid-upload, not rejected.

## Spot it in 5 seconds

```bash
gh release view <tag> --json assets,draft --jq '{draft, n: (.assets|length)}'
# draft:true, n:0  -> the create was cut off, not rejected
```

## Fix

Split create from upload, and put the upload somewhere that will not be killed
at 120s:

```bash
gh release create <tag> --title "..." --notes-file notes.md   # instant, no assets
gh release upload <tag> dist/<file>.dmg --clobber               # background it
gh release edit <tag> --draft=false --latest                    # publish last
```

Then prove the bytes landed instead of trusting the CLI's silence:

```bash
gh release view <tag> --json assets --jq '.assets[] | "\(.name) \(.size) \(.state)"'
stat -f "%z" dist/<file>.dmg          # must be the same number
curl -sIL https://github.com/<owner>/<repo>/releases/download/<tag>/<file>.dmg | grep -i content-length
```

Upload state `uploaded` + identical byte count + a 200 whose `content-length`
matches is three independent confirmations; any single one alone is not
enough (`state` can read `uploaded` while a proxy-truncated body sits there).

## Globalise it

- Any single command carrying a payload measured in minutes: `docker push`,
  `gh release upload`, `rsync` of a big tree, `npm publish` of a fat tarball.
  The CLI has no progress contract, so a kill looks like a silent success.
- "Created but empty" is a distinct state from "failed", and most tooling
  reports both as a non-zero exit. Always re-query the remote object after a
  kill, before re-running anything that creates it.
- Draft releases are the safe staging area: create, upload, verify, *then*
  publish — an unpublished draft can be fixed, a published release with a
  broken asset has already been announced.

## Evidence

```text
gh release create   -> Exit Code: 137 (Signal: SIGTERM)
gh release view     -> Draft, assets: [], url: /releases/tag/untagged-fa88443784b920d519c3
gh release upload   -> Duration: 3m 51s, exit 0
gh release view     -> cardwall-0.2.1-arm64.dmg  128510935 bytes  state=uploaded
stat                -> 128510935 bytes
curl -I             -> HTTP/2 200, content-type: application/octet-stream,
                       content-length: 128510935
after publish       -> draft:false, latest:true, body_len:2649
```

## Takeaway

A killed command is not a failed operation — re-query the remote object before
re-running, and never let a >100 MB upload share a command with anything that
has a two-minute ceiling.
