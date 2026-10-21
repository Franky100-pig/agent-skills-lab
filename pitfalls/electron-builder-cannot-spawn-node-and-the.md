# electron-builder cannot spawn node, and the electron zip download times out

Date: 2026-10-21 · Tags: `electron` `packaging` `network` `proxy` `sandbox`

## Symptom

Two failures from the same build command, on the same machine, in one session.

First, instant and cryptic:

```text
⨯ cannot spawn node  ENOENT  env: node: No such file or directory
```

Second, hanging with no useful output:

```text
• packaging  platform=darwin arch=arm64 electron=44.9.1
  ⨯ Timeout awaiting 'request'  (600000 ms)
```

The build never reaches `building target=DMG`.

## The wrong assumption

Two assumptions, one per failure.

**One: "I'll clean the PATH to make the build deterministic."** Setting a
minimal PATH looks like good hygiene. But electron-builder shells out to `node`
to resolve the dependency tree, and a sanitised PATH does not contain it. The
tool you use to remove ambiguity is what removed the thing the build needed.

**Two: "the download is slow because the network is slow."** It is not slow, it
is *blocked*. GitHub release CDN is unreachable from here; the request hangs
until the timeout rather than failing fast, so the log reads like slowness
rather than unreachability. Nothing distinguishes the two from the message.

## Spot it in 5 seconds

For the spawn failure — ask whether `node` is reachable with the **same
environment the build will use**, not with your interactive one:

```bash
env -i PATH=/usr/bin:/bin node --version    # does it even exist?
which node                                  # where is it, really
```

If the first fails and the second works, PATH is the whole story.

For the download — measure instead of waiting:

```bash
time curl -sI https://github.com/electron/electron/releases/download/v44.9.1/electron-v44.9.1-darwin-arm64.zip
```

A request that returns instantly with an error is blocked-and-failing. A
request that hangs for the full timeout is blocked-and-hanging. Both need a
mirror; neither is fixed by waiting longer.

## Fix

Keep the real toolchain on PATH, and point the downloader at a reachable
mirror:

```bash
# bad: deterministic-looking PATH, no node in it
env PATH=/usr/bin:/bin npm run dist

# good: prepend the node directory to the *existing* PATH
PATH="$PATH:/path/to/node/bin" npm run dist

# good: mirror for both the electron binary and electron-builder's own tools
ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" \
ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/" \
npm run dist
```

With the mirror the same build that had been hanging finished in **21 seconds**.

Related trap in the same family: an injected `NODE_OPTIONS` (a file-proxy
wrapper, say) can block electron-builder's unzip step in a way that surfaces as
an unrelated-looking error. Clear the injected variables for the build:

```bash
env -u NODE_OPTIONS -u BASH_ENV npm run dist
```

## Globalise it

Any build that shells out to a runtime you did not put on PATH:

- Bundlers that spawn `node` or `python` (esbuild, swc, webpack loaders,
  electron-builder, pyinstaller)
- Docker builds with a deliberately minimal `PATH` that omits the runtime
- Cross-compiles that assume the host toolchain is inherited

And the network half is the more transferable lesson: **a hang is not
slowness.** When a download times out, test reachability with a short explicit
`curl -I` before you conclude anything about bandwidth. A mirror is a
configuration fix; patience is not.

## Evidence

```text
# spawn failure — PATH sanitised
$ env PATH=/usr/bin:/bin npm run dist
  ⨯ cannot spawn node  ENOENT  env: node: No such file or directory

# same build, node dir prepended, mirror set
$ PATH="$PATH:.../node/22.22.2-6/bin" \
  ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" \
  ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/" \
  npm run dist
  • packaging  platform=darwin arch=arm64 electron=44.9.1
  • downloaded  electron progress=100%
  • building     target=DMG arch=arm64 file=dist/cardwall-0.4.0-arm64.dmg
  ⎔  done in 21s
```

## Takeaway

Never sanitise `PATH` for a build that shells out to a runtime — prepend the
toolchain instead. And treat a download timeout as *unreachable*, not *slow*:
probe with a short `curl -I` and set a mirror, because waiting longer never
changes the answer.