# A tool installed under `/tmp` disappears and the build fails silently

Date: 2026-10-19 · Tags: `toolchain` `macos` `pandoc` `verification` `pipelines`

## Symptom

A document build that produced a PDF four days ago now produces **no PDF**, and the
console output looks like a normal success:

```text
docx done
=== VERIFY ===
...
FileNotFoundError: no such file: 'answers.pdf'
```

The build command itself was never reported as failed. `ls` afterwards showed only
the `.docx` and `.html` — the `.pdf` line was simply missing.

## The wrong assumption

> "The PDF engine is still installed — I used it last week at the same absolute path."

The path was `/tmp/tectonic-dl/tectonic`. `/tmp` on macOS is periodically cleaned
(often on reboot, and more aggressively than people expect), so a binary that lives
there is **on loan, not installed**. The next time the project is picked up, the
dependency is simply gone.

Second wrong assumption, the one that hid the failure:

> "The command printed `docx done` and I didn't see an error, so both artifacts are fine."

The build was piped through a filter that strips noise —

```bash
pandoc ... 2>&1 | grep -viE "warning|caused by|kanjix" | tail -2
```

That filter removed the one line that mattered, and the pipeline's exit status is
`tail`'s, not the build's. Nothing in the chain could report a failure.

## Spot it in 5 seconds

Ask the filesystem, not the log:

```bash
ls -la answers.pdf 2>/dev/null || echo "NO PDF"
```

If the artifact you promised is not there, the build failed — regardless of what the
console said. The one-line version:

```bash
ls answers.pdf || echo BUILD_FAILED
```

## Fix

Install tools somewhere that survives; treat `/tmp` as scratch space only.

```bash
# bad — gone after the next cleanup
cd /tmp && mkdir -p tectonic-dl && cd tectonic-dl && tar xzf tec.tar.gz

# good — a stable home, referenced by absolute path afterwards
DEST=~/.workbuddy/binaries/tectonic
mkdir -p "$DEST" && cd "$DEST"
curl -sL -o tec.tar.gz "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-aarch64-apple-darwin.tar.gz"
tar xzf tec.tar.gz && rm tec.tar.gz && ./tectonic --version
```

And never let a filter be the only witness. Check the artifact, not the log:

```bash
python - <<'EOF'
import os, sys
missing = [f for f in ("answers.pdf", "answers.docx") if not os.path.exists(f)]
if missing:
    sys.exit(f"MISSING: {missing}")
EOF
```

If the output genuinely must be filtered, use `PIPESTATUS` (bash) / `pipestatus` (zsh)
so the build's own exit code is still visible.

## Globalise it

- Any downloaded binary parked in `/tmp` or `~/Downloads` and then referenced by path —
  same disappearance, usually discovered mid-deadline.
- CI steps that pipe a compiler through `grep`/`head` to "keep the log readable": the
  failing line is exactly the one being filtered out.
- `| tail -n` on a build command: the exit status becomes `tail`'s zero.
- Long gaps between sessions. Anything installed "temporarily" during one session will
  be gone when the next session starts — the project then looks like it broke on its own.
- Rules of thumb that generalise: **artifacts are the source of truth, logs are a
  convenience**; **anything under `/tmp` has a half-life**.

## Evidence

Real output from the failed run (the PDF step's message was swallowed by the filter):

```text
$ ls -la answers.*
-rw-r--r--  1 franky100  staff  15367  answers.docx
-rw-r--r--  1 franky100  staff  11450  answers.html
# answers.pdf is absent; the command that created it reported nothing

$ ls -la /tmp/tectonic-dl/tectonic
TECTONIC MISSING (被 /tmp 清掉了)
```

After reinstalling to a stable path, the same build:

```text
pages: 4 | $ leak: 0 | ** leak: 0 | 缺字形: 0
16 题齐全: True
fonts: LMRoman10-Regular, LMRoman10-Bold, LatinModernMath-Regular
```

## Takeaway

A build is only done when the file exists; and a tool that lives in `/tmp` is a
dependency you have not actually installed.
