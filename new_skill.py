#!/usr/bin/env python3
"""Scaffold a new categorized skill under reflect/skills/.

Usage:
    python3 new_skill.py "my-skill-name" --category game-dev
    python3 new_skill.py "my-skill-name"                # -> asks nothing, uses 'misc'

Creates reflect/skills/<category>/<name>/SKILL.md from _template/ (or a
built-in skeleton when _template is missing), with frontmatter prefilled.
You still write the content — the tool only kills the blank-page step.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(ROOT, "reflect", "skills")
TEMPLATE = os.path.join(SKILLS_DIR, "_template", "SKILL.md")

SKELETON = """---
name: {name}
description: "One line: what this skill does and when an agent should load it. Triggers: keyword1, keyword2."
tags: [{tags}]
---

# {title}

## When to use

- ...

## Instructions

1. ...

## Pitfalls

- ...

## Try it as an experiment

Point at a concrete `experiments/` mini-build that proves this skill works.
"""


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s).strip("-")
    return s or "new-skill"


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a categorized skill.")
    ap.add_argument("name", help="Skill name, e.g. 'binaural-focus'")
    ap.add_argument("--category", default="misc",
                    help="Category folder under reflect/skills/ (game-dev, llm-context, music-creation, ...)")
    args = ap.parse_args()

    slug = slugify(args.name)
    category = slugify(args.category)
    cat_dir = os.path.join(SKILLS_DIR, category)
    skill_dir = os.path.join(cat_dir, slug)
    if os.path.exists(skill_dir):
        print(f"Already exists: {os.path.relpath(skill_dir, ROOT)}")
        sys.exit(1)

    os.makedirs(cat_dir, exist_ok=True)
    os.makedirs(skill_dir, exist_ok=True)

    title = slug.replace("-", " ").title()
    if os.path.exists(TEMPLATE):
        body = open(TEMPLATE, encoding="utf-8").read()
        body = body.replace("name: _template", f"name: {slug}", 1)
    else:
        body = SKELETON.format(name=slug, title=title,
                               tags=category.replace("-", ", "))

    out = os.path.join(skill_dir, "SKILL.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(body)

    rel = os.path.relpath(out, ROOT)
    print(f"Created {rel}")
    print("Next steps:")
    print(f"  1. Fill in {rel}")
    print(f"  2. Add a row under the '{category}' table in reflect/skills/README.md")
    print(f"  3. git add {os.path.relpath(skill_dir, ROOT)} && git commit -m 'skill: {slug}'")


if __name__ == "__main__":
    main()
