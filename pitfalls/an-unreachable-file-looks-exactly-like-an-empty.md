# An unreachable file looks exactly like an empty file

Date: 2026-10-19 · Tags: `verification` `curl` `network` `github` `shell`

## Symptom

Checking whether a remote repository has the latest files, every file comes back
"empty" and every comparison says DIFF:

```text
web/index.html             bytes=0       focus-visible=0
web/notes.html             bytes=0       focus-visible=0
tools/build_preview.py     bytes=0       pages_html=0

DIFF web/index.html  local=4801e911e885d695 remote=e3b0c44298fc1c14
```

`e3b0c44298fc1c14…` is the SHA-256 of the empty string. Read carelessly, this says
"the remote files are empty / missing / the push failed" — on a repo that was in fact
perfectly in sync.

## The wrong assumption

> "`curl -s` returned nothing, therefore there is nothing there."

`-s` silences the error message *and* the status. A DNS failure, a proxy refusal or a
blocked host all produce **zero bytes on stdout with exit code 0-ish silence**, which is
byte-for-byte indistinguishable from a genuinely empty file. The comparison then reports
DIFF for every path, and the natural conclusion ("the sync failed, re-push") is wrong.

In this case `raw.githubusercontent.com` was simply not reachable from the machine:

```text
raw HTTP=000 size=0        # 000 = connection never established
```

While `api.github.com` answered normally on the same machine.

## Spot it in 5 seconds

Never trust a body without its status code:

```bash
curl -s -o /tmp/x -w "HTTP=%{http_code} size=%{size_download}\n" "$URL"
# 000  -> never connected        (network / DNS / proxy / host blocked)
# 404  -> really not there
# 200 + size>0 -> real content
```

And sanity-check the digest: if every "remote" hash equals
`e3b0c44298fc1c149afbf4c8996fb924…`, you hashed emptiness, not content.

## Fix

Compare **blob hashes** instead of downloading bodies. Git already computes exactly the
identity you want, and the contents API works over the same authenticated channel as the
rest of your work:

```bash
# local blob id of the file as git would store it
local_sha=$(git hash-object web/index.html)
# blob id git reports for the same path on the remote branch
remote_sha=$(gh api repos/OWNER/REPO/contents/web/index.html --jq '.sha')
[ "$local_sha" = "$remote_sha" ] && echo OK || echo DIFF
```

This is a *byte-exact* comparison (not a diff of a rendering, not a size check) and it
never touches a raw CDN host. Result on the same machine, minutes later:

```text
OK   web/index.html
OK   web/notes.html
OK   tools/build_preview.py
```

## Globalise it

- Any pipeline that pipes `curl`/`wget` output into `wc -c`, `shasum`, `diff` or a parser
  without checking the status: a failed fetch becomes "empty input", which many tools
  accept silently.
- `curl -s` + `|| true` in a `set -e` script — the failure is erased twice.
- CI steps that treat "no output" as "nothing to do": a blocked artifact download looks
  like an empty change set, and the job goes green.
- Mirror/CDN hosts (raw.githubusercontent, unpkg, jsdelivr) can be blocked in one region
  while the API host works — reachability is per-host, not per-service.
- Rule of thumb: **empty output is not evidence of an empty thing.** An unreachable
  source, an empty file, and a filtered-away result all look identical from `stdout`;
  only the status code and an independently-derived hash separate them.

## Evidence

The false alarm, then the same comparison done properly:

```text
# naive: body only
$ curl -s "$RAW" | wc -c
0
$ curl -s "$RAW" | shasum -a 256
e3b0c44298fc1c14…        # the empty-string hash

# with status
$ curl -s -o /tmp/raw-index.html -w "raw HTTP=%{http_code} size=%{size_download}\n" "$RAW"
raw HTTP=000 size=0

# blob comparison via API
$ git hash-object web/index.html
ca17533e4f16e7e6d786fb19c52781b8d2d2523f
$ gh api repos/…/contents/web/index.html --jq '.sha'
ca17533e4f16e7e6d786fb19c52781b8d2d2523f
```

## Takeaway

Before concluding that something is missing, prove you actually reached it — a 000 and an
empty file produce the same bytes and very different truths.
