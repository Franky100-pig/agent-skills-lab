# agent-skills-lab

> A beginner-friendly **playground + toolkit**: small runnable code
> experiments, and a categorized, tagged collection of reusable
> [skills](reflect/skills/) for working with LLMs / coding agents.

This started as a personal daily-commit habit. It's becoming a tool any
beginner developer can browse, copy from, and contribute to:

- **[Skills](reflect/skills/README.md)** — organized by category
  (🎮 game-dev · 🧠 llm-context · 🎵 music-creation), tagged for filtering,
  each ending with a "try it as an experiment" pointer.
- **[Experiments](INDEX.md)** — small runnable programs (zero/few
  dependencies), tagged, all verified by CI on every push.
- **[Journal](reflect/README.md)** — LLM-usage notes with real evidence:
  screenshots, transcripts, data — not vibes.

## Quick start (2 minutes)

```bash
git clone https://github.com/Franky100-pig/agent-skills-lab.git
cd agent-skills-lab

# run any experiment — no install step
python3 experiments/2026-09-29_sieve_of_eratosthenes/main.py

# author your own skill
python3 new_skill.py "my-skill" --category game-dev
```

## The three daily flavors

| Tool | Creates | Where |
|------|---------|-------|
| `python3 new_exp.py "idea"` | runnable code experiment | `experiments/` |
| `python3 new_note.py "thought"` | reflection note (with Evidence section) | `reflect/journal/` |
| `python3 new_skill.py "name" --category game-dev` | categorized skill skeleton | `reflect/skills/<category>/` |

## Contributing

Beginner-friendly on purpose — no CLA, no formal gate:

1. Fork / branch.
2. Add an experiment, note, or skill (the tools above scaffold it; the
   [skills guide](reflect/skills/README.md#contributing-a-skill-beginner-friendly-on-purpose)
   explains the quality bar).
3. PR with a one-line description. CI runs all experiments to keep them
   runnable.

## Layout

```
agent-skills-lab/
├── new_exp.py           # scaffold a code experiment
├── new_note.py          # scaffold a reflection note (evidence-first)
├── new_skill.py         # scaffold a categorized skill
├── INDEX.md             # tagged table of code experiments
├── experiments/         # runnable, CI-verified
└── reflect/
    ├── README.md        # journal index
    ├── journal/         # dated notes + assets/ for screenshots
    └── skills/          # categorized, tagged SKILL.md collection
```

## Index

- Code experiments (tagged): [INDEX.md](INDEX.md)
- Skills by category: [reflect/skills/README.md](reflect/skills/README.md)
- Reflection journal: [reflect/README.md](reflect/README.md)
