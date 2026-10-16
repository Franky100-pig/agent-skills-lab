# doctest reports failures but prints none of them

Date: 2026-10-16 · Tags: `python` `doctest` `verification` `streams`

## Symptom

A checker that runs every `>>>` example in a README prints the count of
failures and nothing else — no failing example, no expected-vs-got, no line
number. So you know *how many* things are wrong and nothing about *which*:

```console
$ python tools/check_readme.py
==============================================================
README: 8 blocks, 27 examples, 13 failed
```

Thirteen failures, zero diagnostics. The natural next move is to distrust the
checker and start adding `print`s — which is exactly the wrong move.

## The wrong assumption

"The runner isn't reporting failures" / "I need to add my own reporting."

The runner is reporting them perfectly. The reports are being written into a
buffer that doctest itself has swapped in as `sys.stdout`, and then thrown away
with it.

`DocTestRunner.run()` rebinds the global stream for the duration of the run:

```python
sys.stdout = self._fakeout          # inside run()
try:
    return self.__run(test, compileflags, out)
```

So this, which reads as "print the reports":

```python
runner.run(test, out=lambda s: sys.stdout.write(s))
```

resolves `sys.stdout` **at call time** — i.e. after the swap — and writes every
failure report into the capture buffer doctest is using to compare example
output. Which is then discarded.

## Spot it in 5 seconds

Failure count greater than zero, and the report text exactly empty. Confirm it
without touching the library: bind the stream *before* the call and use the
bound method.

```python
real = sys.stdout
runner.run(test, out=real.write)     # reports appear
```

If that shows the reports, the callback was never the problem.

## Fix

Write into a list. A list is the one sink nothing can steal.

```python
# bad — sys.stdout is rebound by the time the callback fires
result = runner.run(test, out=lambda s: sys.stdout.write(s))

# good — collect, then decide
reports: list[str] = []
result = runner.run(test, out=reports.append)
if result.failed:
    sys.stdout.write("".join(reports))
```

Also worth doing regardless: only echo the buffer when `result.failed`. On a
green run the buffer is empty, so this costs nothing and keeps the success path
free of noise.

## Globalise it

Any callback handed to a library that temporarily replaces `sys.stdout` /
`sys.stderr` — `unittest`, `pytest`'s `capsys`, `contextlib.redirect_stdout`,
`tqdm`, `click.testing.CliRunner`, anything wrapping `subprocess`. The shape is
identical every time: you pass a function that writes to the global stream, the
library redirects the global stream, your function writes into the redirect.

Rule: **if a reporting callback produces nothing, suspect the stream it writes
to, not the reporter.** `out=buffer.append` is never wrong.

Second-order tell: a *count* that is right while the *detail* is missing means
the collecting layer works and the formatting layer is being swallowed.

## Evidence

Real session. The checker had been rewritten minutes earlier specifically so a
missing `# note:` in an expected-output block would be caught — it was catching
things correctly and hiding all of them:

```text
$ python tools/check_readme.py
==============================================================
README: 8 blocks, 27 examples, 13 failed

$ # after out=reports.append
$ python tools/check_readme.py
**********************************************************************
File "README.md", line 1, in README block 4
Failed example:
    zInterval(2, [3, 4, 5, 6, 7], None, 0.95)
Expected:
    StatGroup(CLower, CUpper, x, ME, sx, n, σ, σx)      # note: x
Got:
    StatGroup(CLower, CUpper, x, ME, sx, n, σ, σx)
**********************************************************************
...
README: 8 blocks, 27 examples, 4 failed
```

Two things fell out of the fix immediately: the count dropped 13 → 4 (the other
9 were genuinely the same defect repeating), and every remaining one was a
one-line edit. The blocker was never the failures; it was that the tool that
found them refused to say what they were.

## Takeaway

A verifier that counts without reporting is worse than no verifier: it makes an
unverified artefact look *measured*. If a check can fail, make sure it can also
say why — and when it stays silent, suspect `sys.stdout`.
