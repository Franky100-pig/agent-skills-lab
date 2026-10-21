# raw.githubusercontent.com times out, so you cannot check whether a file was pushed

Date: 2026-10-21 · Tags: `git` `github` `network` `proxy` `verification`

## Symptom

You push, and then you want to *prove* the new file is really on the remote —
a README, a release asset, a generated config. You reach for the obvious tool
and get nothing back:

```bash
$ curl -sL -o /dev/null -w "http=%{http_code} size=%{size_download}\n" \
    https://raw.githubusercontent.com/owner/repo/main/README.en.md
http=000 size=0
```

Exit code 35. Zero bytes. A `size=0` that looks exactly like "the file is
empty" or "the push did not land" — and you start re-pushing, or worse,
concluding your work was lost.

## The wrong assumption

"`curl` says 0 bytes, so the remote has 0 bytes."

`http=000` means **no HTTP response was received at all** — curl never got a
status line. It is not a 404, not an empty body, not evidence about the remote
in any direction. The tempting inference ("the file isn't there") is
indistinguishable from ("the network path is closed").

The second wrong assumption is about the tool: that raw.githubusercontent is the
only way to read a file from GitHub. It is not — and it is the endpoint most
likely to be blocked, because it serves large uncached content from a CDN that
is commonly unreachable.

## Spot it in 5 seconds

**Always print the status code.** A `0` in the `http_code` field is the whole
diagnosis: no response ≠ empty response. Same rule as
[an unreachable file looks like an empty file](an-unreachable-file-looks-exactly-like-an-empty.md)
— that entry is about reading zero bytes as "empty"; this one is about not
being able to read at all, and the `-w "%{http_code}"` is the same tell.

Then switch endpoints. The API goes through a different host and is usually
reachable when raw is not:

```bash
gh api repos/owner/repo/contents/README.en.md --jq '.size, .sha'
gh api repos/owner/repo/contents/README.en.md -q .content | base64 -d | head
```

If `gh` works, the file exists and your push succeeded — you simply asked
through a door that was locked.

## Fix

Verify remote state through the API, and treat `http=000` as "unreachable",
never as "empty":

```bash
# size + blob sha, no download
gh api repos/<owner>/<repo>/contents/<path> -q '"size=" + (.size|tostring) + "  sha=" + .sha'

# read the content back
gh api repos/<owner>/<repo>/contents/<path> -q .content | base64 -d

# release assets: state + size, again no body
gh release view <tag> --json assets -q '.assets[] | .name + "  " + (.size|tostring) + "  " + .state'
```

For release integrity, go further than size — compare the **digest** the API
reports against a local hash. This catches a truncated or substituted asset
that a byte count alone would not:

```bash
shasum -a 256 dist/app.dmg
gh release view <tag> --json assets -q '.assets[0].digest'
```

```text
local  8dc84481762f4cd8106343b53a7464211eba411be55f5a964b561f0098d15a96
remote sha256:8dc84481762f4cd8106343b53a7464211eba411be55f5a964b561f0098d15a96
```

## Globalise it

Any verification step that runs over a possibly-blocked endpoint:

- "Did my deploy land?" via a raw URL instead of the hosting platform's API
- Checking a file on a CDN, a package registry mirror, or an S3 public URL
- Any assertion of the form "size == 0 therefore absent"

The general rule: **every remote assertion needs a status code and a fallback
endpoint**, and every integrity check should be a hash rather than a length.
When one endpoint is blocked you need a second way to ask, or you cannot
distinguish "my change is missing" from "I cannot see" — and those two lead to
opposite responses.

## Evidence

```text
$ curl -sL -o /dev/null -w "http=%{http_code} size=%{size_download}\n" \
    https://raw.githubusercontent.com/Franky100-pig/TreeNote/main/README.en.md
http=000 size=0
$ echo $?
35

# same question, different endpoint
$ gh api repos/Franky100-pig/TreeNote/contents/README.en.md \
    -q '"README.en.md  size=" + (.size|tostring) + "  sha=" + .sha'
README.en.md  size=9753  sha=ea77323ce23cac8da2d65fdab0e88f750ad35526

$ gh api repos/Franky100-pig/TreeNote/contents/README.en.md -q .content | base64 -d | head -3
# cardwall (TreeNote)

**[中文](README.md)** · English | [中文](README.md)
```

The push had succeeded. `raw.githubusercontent.com` simply was not an option.

## Takeaway

`http=000` is "no response", not "empty body" — never infer a remote's state
from it. Verify GitHub through `gh api .../contents/...` instead of
`raw.githubusercontent.com`, and compare digests rather than byte counts when
the thing being checked has to be exactly right.