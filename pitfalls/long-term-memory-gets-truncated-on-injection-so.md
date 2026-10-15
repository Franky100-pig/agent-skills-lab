# Long-term memory gets truncated on injection, so a rule at the end is never read

Date: 2026-10-15 · Tags: `memory` `context` `agent-workflow` `silent-failure`

## Symptom

You tell your agent: *"remember this rule for every future conversation."* It
appends the rule to the long-term memory file, confirms, and the file on disk
clearly contains it.

Weeks later the rule is silently not being followed. Nothing errors. The agent
behaves as if the rule was never written — because, as far as its context goes,
it never was.

## The wrong assumption

"A file I write to memory is read back in full."

Memory is not a container that is *read*; it is a budget that is **injected** into
the context window at session start. Injection is truncated.

Measured here: a 70 KB memory file was injected only up to roughly **5–7 KB**.
Everything past that point sat on disk, correct and complete, and was never seen
by the model.

The failure is silent and asymmetric, which is what makes it expensive:
**writing succeeds** (so the agent reports success) while **reading is partial**
(so the agent ignores the rule). No step in the loop raises an error.

## Spot it in 5 seconds

Compare *where your rule sits* with *where the injected copy stops*.

1. Find the rule's byte offset:

```bash
python -c "
data = open('MEMORY.md', encoding='utf-8').read()
print(len(data[:data.index('my rule keyword')].encode()))"
```

2. Look at the injected memory block the model actually received, and find the
   last thing in it. It typically ends **mid-sentence**, which is the tell that it
   was cut rather than ended.

If the offset is larger than where the injected copy stopped, the rule is dead
text — the file has it, the model does not.

## Fix

- **Put high-priority rules at the TOP of the file.** In a budgeted file, order
  *is* priority; chronology is worthless there.
- Add a self-warning at very top so the next writer cannot repeat the mistake:

```markdown
> ⚠️ Injection truncates this file (~6 KB). New rules go in THIS region —
> at the end means never read.
```

- Stop the file growing without bound: push stale detail out into dated notes,
  and keep the top region for rules that must always be in scope.

## Globalise it

Any context that is **assembled by concatenation under a budget**: system
prompts, retrieved documents, stuffed file contents, tool output, log excerpts.
In all of them the tail is what disappears first, and the cut is silent — there
is no "context overflow" error at this layer.

So whenever something important is being appended to something bounded, ask
**which end survives** before deciding where to write it.

## Evidence

```text
file size                                    : 70473 bytes
rule offset in file   (before fix)           : 68911   <- final 1.5 KB
rule offset in file   (after moving it)      :   344   <- now first
where the injected copy was cut              : ~5-7 KB (mid-way through "## 本机环境限制")
```

The rule was written, committed to disk, and confirmed to the user — and was
invisible to every subsequent session for the entire time it sat at the end.

## Takeaway

Treat a memory file as a budget, not a container: the important rules go first,
because the end is the first thing cut.
