# A server started with a trailing `&` is gone by the next command

Date: 2026-10-19 · Tags: `shell` `processes` `testing` `servers` `tooling`

## Symptom

Start a static server for a manual test, confirm it answers, then use it in the next
command — and it is not there any more:

```bash
$ python3 -m http.server 8765 &
$ sleep 2 && curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
200                      # it works

# ... next tool call ...
$ agent-browser open http://127.0.0.1:8765/
✗ Navigation failed: net::ERR_CONNECTION_REFUSED
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
000
```

The server started fine, answered once, and vanished. Nothing reported an error, because
nothing failed — the process was simply reaped.

## The wrong assumption

> "`&` means background, so the process keeps running for the rest of the session."

`&` only detaches the job from the *terminal's* foreground. The process is still a child of
that shell, in that shell's process group. When the shell exits (which, for an agent's
`execute` tool, is the moment the command returns), the child goes with it — or is killed
outright when the sandbox tears the process group down. The redirect `>log 2>&1` does not
save it: the file keeps the log, not the process.

Typical second-order effect: the first verification inside the *same* command passes
(`200`), so the setup looks proven; the failure only shows up in the next call, where it
reads as "the app is broken" rather than "the server is gone".

## Spot it in 5 seconds

Re-probe from a **new** command, not the one that started it:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/   # 000 = nothing listening
```

If the port answered in the starting command and refuses in the next one, the process was
never yours to keep.

## Fix

Use a runner that owns the process for you — i.e. the tool's own background execution
(`run_in_background`), which gives the job an id, captures its output, and keeps it alive
until you stop it. Then stop it explicitly when the test is over:

```text
run_in_background: python3 -m http.server 8765   # returns task_id
...test...
stop task_id
```

If you must stay in a plain shell and genuinely need detachment, `setsid` / `nohup …
&` keeps the process alive — but then nobody owns it: it is not tracked, not logged in
any managed way, and it survives the session, which is its own problem. Prefer the managed
runner.

Rule that generalises: **a background process must be owned by something that outlives the
command that started it** — otherwise you have not started a server, you have borrowed one
for a few seconds.

## Globalise it

- Any `cmd &` used for "start a server, then test it in the next step": same death, same
  confusing `ERR_CONNECTION_REFUSED`.
- `nohup … &` in an agent/CI step: survives, but unsupervised — later runs hit `EADDRINUSE`
  on a port nobody remembers occupying.
- Watchers (`npm run dev`, `tsc --watch`) started with `&` — they die silently and the
  next edit "does nothing".
- Pipe chains ending in `&` (`make serve >/dev/null 2>&1 &`): the exit status you never
  read hides the fact that the job is doomed.
- Rule of thumb: **the lifetime of a child is the lifetime of its parent.** If the parent is
  a command that returns immediately, so is the child.

## Evidence

Real sequence from a manual UI test:

```text
$ python3 -m http.server 8765 >/tmp/la-http.log 2>&1 &
$ sleep 2 && curl -s -o /dev/null -w "HTTP=%{http_code}\n" http://127.0.0.1:8765/index.html
HTTP=200

# next tool call
$ agent-browser open "http://127.0.0.1:8765/index.html"
✗ Navigation failed: net::ERR_CONNECTION_REFUSED
```

After switching to a managed background runner, the same probe answered `200` for the whole
test, and the engine loaded normally (`Engine ready · local Python/SymPy`).

## Takeaway

`&` is not "keep running" — it is "don't block this shell". Use a runner that owns the
process, and verify from a *different* command than the one that started it.
