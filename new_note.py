#!/usr/bin/env python3
"""Scaffold a new reflection note in reflect/journal/.

Usage:
    python3 new_note.py "Why I prefer WorkBuddy for writing"

Creates reflect/journal/YYYY-MM-DD_slug.md and appends a row to the journal
index table in reflect/README.md.
"""
import sys
import os
import re
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
JOURNAL_DIR = os.path.join(ROOT, "reflect", "journal")
README = os.path.join(ROOT, "reflect", "README.md")

TABLE_HEADER = (
    "| Date | Note | Path |\n"
    "|------|------|------|\n"
)


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "note"


def update_index(date: str, title: str, folder: str) -> None:
    row = f"| {date} | {title} | [reflect/journal/{folder}](reflect/journal/{folder}) |\n"
    if not os.path.exists(README):
        with open(README, "w") as f:
            f.write("# reflect/ — LLM journal & skills\n\n")
            f.write("## Journal index\n\n")
            f.write(TABLE_HEADER)
    else:
        content = open(README).read()
        if "## Journal index" not in content:
            with open(README, "a") as f:
                f.write("\n## Journal index\n\n")
                f.write(TABLE_HEADER)
    with open(README, "a") as f:
        f.write(row)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python3 new_note.py "Title of reflection"')
        sys.exit(1)
    title = " ".join(sys.argv[1:])
    date = datetime.date.today().isoformat()
    folder = f"{date}_{slugify(title)}"
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    path = os.path.join(JOURNAL_DIR, f"{folder}.md")
    with open(path, "w") as f:
        f.write(
            f"# {title}\n\n"
            f"Date: {date}\n\n"
            f"## What happened\n\nWrite your reflection here.\n\n"
            f"## Evidence\n\n"
            f"Show, don't tell — a screenshot, a paste of the actual "
            f"prompt/output, or a small data table beats a paragraph of "
            f"summary. Drop images in `reflect/journal/assets/` and embed "
            f"with `![alt](assets/<file>.png)`.\n\n"
            f"```text\n# paste real prompt / output / data here\n```\n\n"
            f"## Takeaway\n\nOne line someone else could reuse.\n"
        )
    update_index(date, title, folder)
    print(f"Created reflect/journal/{folder}.md")


if __name__ == "__main__":
    main()
