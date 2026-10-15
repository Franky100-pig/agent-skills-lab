#!/usr/bin/env python3
"""Scaffold a new pitfall entry in pitfalls/.

Usage:
    python3 new_pitfall.py "grep alternation returns a false negative"

Creates pitfalls/<slug>.md from the standard skeleton and appends a row to the
index table in pitfalls/README.md.

Name the entry by SYMPTOM ("what you saw"), not by cause or by fix — that is how
you will search for it next time you are confused. If an entry for the same
symptom already exists, this refuses and tells you to sharpen that one instead:
the same trap is never written down twice.
"""
import sys
import os
import re
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, "pitfalls")
README = os.path.join(DIR, "README.md")

INDEX_HEADER = (
    "| Pitfall | Tags | Date |\n"
    "|---|---|---|\n"
)

SKELETON = """# {title}

Date: {date} · Tags: `tag1` `tag2`

## Symptom

What you actually see. Paste the real output if it is short — a transcript beats
a description.

```text
# the confusing thing, verbatim
```

## The wrong assumption

The conclusion that looks obvious and is wrong. This is the expensive part: name
it, so the next reader recognises *themselves* doing it.

## Spot it in 5 seconds

The tell that gives it away — ideally one command, or one question to ask about
the artefact in front of you.

```bash
# the check
```

## Fix

The concrete change. Show the bad and the good next to each other when the
difference is small.

## Globalise it

Where else this same trap bites. A pitfall that only ever happens once is a
story; a pitfall with relatives is knowledge.

## Evidence

Real output from when it happened.

```text
# before / after
```

## Takeaway

One line someone else could reuse.
"""


# Slugs are filenames people read and type, so keep them short. The link text in
# the index still carries the full title — the slug only has to be findable.
SLUG_MAX = 48


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not s:
        return "pitfall"
    if len(s) > SLUG_MAX:
        s = s[:SLUG_MAX]
        if "-" in s:                       # cut at a word boundary, not mid-word
            s = s[: s.rindex("-")]
        s = s.strip("-")
    return s or "pitfall"


def update_index(date: str, title: str, slug: str) -> None:
    """Append a row to the index table itself.

    Note this inserts at the END OF THE TABLE, not at the end of the file: the
    index is not the last thing in pitfalls/README.md (there is prose after it),
    so blindly appending would leave the row stranded under that prose.
    """
    row = f"| [{title}]({slug}.md) | _(add tags)_ | {date} |"

    if not os.path.exists(README):
        with open(README, "w") as f:
            f.write("# pitfalls/ — traps I've already stepped on\n\n## Index\n\n")
            f.write(INDEX_HEADER)
            f.write(row + "\n")
        return

    lines = open(README).read().split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Index":
            start = i
            break

    if start is None:
        lines += ["", "## Index", "", INDEX_HEADER.rstrip("\n"), row]
        with open(README, "w") as f:
            f.write("\n".join(lines) + "\n")
        return

    # Walk to the table: skip the blank line(s) after the heading, then consume
    # the contiguous block of table rows. `last` ends up on the final row.
    i = start + 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    last = i - 1
    while i < len(lines) and lines[i].startswith("|"):
        last = i
        i += 1
    lines.insert(last + 1, row)

    with open(README, "w") as f:
        f.write("\n".join(lines))


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python3 new_pitfall.py "short symptom, phrased as what you saw"')
        sys.exit(1)
    title = " ".join(sys.argv[1:])
    date = datetime.date.today().isoformat()
    slug = slugify(title)

    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, f"{slug}.md")
    if os.path.exists(path):
        print(f"Already exists: pitfalls/{slug}.md")
        print("The same trap is never written twice — sharpen that entry instead.")
        sys.exit(1)

    with open(path, "w") as f:
        f.write(SKELETON.format(title=title, date=date))
    update_index(date, title, slug)
    print(f"Created pitfalls/{slug}.md")


if __name__ == "__main__":
    main()
