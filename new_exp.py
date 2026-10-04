#!/usr/bin/env python3
"""Scaffold a new daily experiment.

Usage:
    python3 new_exp.py "My cool idea"

Creates experiments/YYYY-MM-DD_slug/ with a runnable main.py template and a
README.md, then appends a row to INDEX.md.
"""
import argparse
import os
import re
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.join(ROOT, "experiments")
INDEX = os.path.join(ROOT, "INDEX.md")

TEMPLATE = '''#!/usr/bin/env python3
"""TITLE

Date: DATE

One or two lines on what this experiment does / what you learned.
Run: python3 main.py
"""


def main() -> None:
    print("Hello from this experiment! Replace me with real code.")


if __name__ == "__main__":
    main()
'''


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "experiment"


def update_index(date: str, title: str, folder: str, tags: str) -> None:
    row = (f"| {date} | {title} | {tags or '—'} "
           f"| [experiments/{folder}](experiments/{folder}) |\n")
    if not os.path.exists(INDEX):
        with open(INDEX, "w") as f:
            f.write("# Experiment Index\n\n")
            f.write("| Date | Experiment | Tags | Path |\n")
            f.write("|------|------------|------|------|\n")
    with open(INDEX, "a") as f:
        f.write(row)


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a runnable experiment.")
    ap.add_argument("title", help="Short title, e.g. 'Bouncing ball with pygame'")
    ap.add_argument("--tags", nargs="+", default=[],
                    help="tags from the INDEX.md vocabulary; commas or spaces "
                         "both work: --tags pygame,games  or  --tags pygame games")
    args = ap.parse_args()

    title = args.title
    flat = [t for chunk in args.tags for t in chunk.split(",")]
    tags = " ".join(f"`{t.strip()}`" for t in flat if t.strip())
    date = datetime.date.today().isoformat()
    folder = f"{date}_{slugify(title)}"
    path = os.path.join(EXP_DIR, folder)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "main.py"), "w") as f:
        f.write(TEMPLATE.format(title=title, date=date))
    with open(os.path.join(path, "README.md"), "w") as f:
        f.write(f"# {title}\n\nDate: {date}\n\nDescribe what you built or learned here.\n")

    update_index(date, title, folder, tags)
    print(f"Created experiments/{folder}")
    if not tags:
        print("  note: no --tags given, index row shows '—' (fill it in when you know)")


if __name__ == "__main__":
    main()
