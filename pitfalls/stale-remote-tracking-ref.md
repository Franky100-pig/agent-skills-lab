# Syncing status lies when the remote is unreachable

Date: 2026-10-15 · Tags: `git` `remote` `proxy` `trust`

## Symptom

`git status` insists your branch is far ahead of the remote:

```text
## main...origin/main [ahead 17]
```

Seventeen unpushed commits. So you plan to push them — or worse, you start
"recovering" work you believe never left the machine.

Meanwhile the remote actually has a commit you *don't* have, and you are the one
who is behind.

## The wrong assumption

"`git status` knows the remote state."

It does not. `ahead 17` is computed by comparing your branch with the **local
remote-tracking ref** `origin/main` — a cached snapshot. That ref is only fresh if
a fetch has succeeded. If the network path to that remote is broken (here: an
HTTPS remote behind a proxy that silently drops the connection), the cached ref
never updates, and git keeps reporting the stale comparison as fact.

## Spot it in 5 seconds

Fetch the remote you *can* reach, then compare against its ref explicitly:

```bash
git fetch gh              # the working remote
git rev-list --count HEAD..gh/main    # commits you are behind
git rev-list --count gh/main..HEAD    # commits you are ahead
```

And check what the remote thinks, independently of git:

```bash
gh api repos/<owner>/<repo>/commits/main --jq '.sha'
```

If the API's SHA differs from your tracking ref, the ref is stale — not you.

## Fix

- **Name the remote you trust.** If one remote is unreliable, don't let its
  tracking ref drive your decisions; fetch the working one and compare against
  it by name.
- **Fix or drop the dead remote.** Either repair the transport or stop using it,
  so nobody reads its stale ref again.
- When a sync number matters (before a release, before a force-push), **confirm
  it with a fetch**, never with a cached ref.

## Globalise it

Every "status" that is computed from a **cache** rather than a live query:
stale package indexes, a browser cache making a deploy look unapplied, a
monitoring dashboard showing the last successful poll. Prefer a live probe when
the answer changes what you are about to do.

## Evidence

`origin` was HTTPS (proxied, unreliable); `gh` was SSH (worked). After a fetch of
the working remote:

```text
$ git status -sb
## main...origin/main [ahead 17]

$ git fetch gh
From ssh://github.com/owner/repo
   b7f243d..2684bfc  main -> gh/main

$ echo "behind=$(git rev-list --count HEAD..gh/main) ahead=$(git rev-list --count gh/main..HEAD)"
behind=1 ahead=0
```

The "17 ahead" was entirely an artefact of a stale ref: the true state was
*1 behind, 0 ahead*.

## Takeaway

`ahead/behind` measures your **cache**, not the remote — fetch before you trust
a sync number.
