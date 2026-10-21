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

The `untagged-…` URL only means "this draft has no tag ref yet" — which is the
normal state of *any* fresh `--draft` create, including a fully successful one
(2026-10-21: `gh release create v0.3.3 --draft` exited 0 and still printed
`untagged-54ce0b…`). It is **not** evidence of a timeout. See "Spot it" below
for what actually distinguishes the two.

## The wrong assumption

"The release failed, so nothing was created — re-run the same command." It did
create a **draft with zero assets**. Re-running `release create` for the same
tag then argues with that draft, and you end up debugging `422 already_exists`
on top of the original timeout.

The other wrong assumption: "the upload must be broken / rate-limited." It is
only slow — 123 MB over a proxy took ~4 minutes, past the 2-minute command
ceiling. The process got SIGTERM'd mid-upload, not rejected.

## Spot it in 5 seconds

Two facts, both needed, because the URL lies:

```bash
gh release create <tag> --draft --title "..." --notes-file notes.md; echo "exit=$?"
# exit=137 / "terminated"  -> the process was killed; the remote object may still exist
gh release view <tag> --json draft,assets --jq '{draft, n: (.assets|length), names:[.assets[].name]}'
# killed mid-upload WITH an asset argument -> draft:true, n:0  (asset is missing)
# healthy draft                            -> draft:true, n:0  (no asset was requested)
```

So `n:0` alone proves nothing. The discriminator is **exit status**: if
`release create` exited 0, the draft is fine no matter how `untagged-` it looks
— proceed to upload. Only a killed (non-zero) create whose requested asset is
absent is a half-made draft.

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
- **A draft also owns no git tag.** `git ls-remote --tags` and `git fetch
  --tags` both come up empty for `v0.3.3` until you publish; the tag ref is
  minted at `--draft=false` time. So the `untagged-<id>` URL is normal output
  for a *successful* `--draft` create — it is not proof of a timeout. Do not
  "fix" a healthy draft by re-running `release create`; check
  `gh release view <tag> --json draft,assets` instead, then go publish.

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

The same-looking state, but healthy (2026-10-21, v0.3.3) — nothing was wrong,
the URL was just the untagged-draft slug:

```text
gh release create v0.3.3 --draft --notes-file notes.md
  -> https://github.com/…/releases/tag/untagged-54ce0b672597bde0e57b
  -> exit 0
gh release list     -> cardwall v0.3.3 …  Draft  v0.3.3        # tag name is right
gh release upload   -> 48s, "Successfully uploaded 2 assets"
git ls-remote --tags -> (empty for v0.3.3, before publish)
gh release edit --draft=false --latest
  -> https://github.com/…/releases/tag/v0.3.3
git rev-parse v0.3.3 -> ba18a0e301eeb6d9c7212cb9bce64702bf4cb82a
gh release view     -> draft:false, 2 assets, bodyLen:1145
```

## Takeaway

A killed command is not a failed operation — re-query the remote object before
re-running, and never let a >100 MB upload share a command with anything that
has a two-minute ceiling.
