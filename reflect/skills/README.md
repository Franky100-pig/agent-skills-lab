# skills/

Reusable **skills** for LLM / coding agents — prompt and workflow patterns
worth keeping, organized by category. Each skill lives in its own folder with
a `SKILL.md` (YAML frontmatter + instructions). Copy `_template/` to author
your own, or use the helper:

```bash
python3 new_skill.py "my-skill-name" --category game-dev
```

The format mirrors the WorkBuddy `SKILL.md` convention, so a skill authored
here can be dropped into `~/.workbuddy/skills/` (or any agent-skills loader)
if it proves useful.

## Categories

### 🎮 game-dev — [`game-dev/`](game-dev/)

| Skill | Tags | What it does |
|-------|------|--------------|
| [raycaster-playbook](game-dev/raycaster-playbook/SKILL.md) | `raycasting` `pseudo-3d` `rendering` `pygame` | Build a pseudo-3D raycast FPS: DDA, fisheye fix, sprites, wall sliding |
| [fps-game-feel](game-dev/fps-game-feel/SKILL.md) | `game-feel` `gunplay` `tuning` | Tuning checklist for gunplay: latency, feedback, recoil, TTK, sound |
| [moba-design-primer](game-dev/moba-design-primer/SKILL.md) | `moba` `game-design` `balance` | MOBA anatomy: economy, hero kits, items, snowball control, balance |
| [moba-lite-prototype](game-dev/moba-lite-prototype/SKILL.md) | `moba` `pygame` `prototype` | Build a playable mini-MOBA in pygame, step by step |
| [data-driven-tuning](game-dev/data-driven-tuning/SKILL.md) | `balance` `json` `telemetry` | Balance without code edits: stats in JSON, hot-reload, match logs |
| [debug-frame-drops](game-dev/debug-frame-drops/SKILL.md) | `performance` `profiling` `pygame` | Diagnose stutter systematically: frame-time graph, cProfile, budgets |
| [game-mvp-scoping](game-dev/game-mvp-scoping/SKILL.md) | `planning` `mvp` `scoping` | *(stub)* Vertical-slice scoping method |

### 🧠 llm-context — [`llm-context/`](llm-context/README.md)

Skills for managing LLM context: prompt templates, memory conventions,
output-format contracts. *(Empty — first skill welcome.)*

### 🎵 music-creation — [`music-creation/`](music-creation/README.md)

Skills for making music with code: synthesis, algorithmic composition, MIDI
tooling. *(Empty — first skill welcome.)*

### ✍️ writing — [`writing/`](writing/)

Descriptive prose/style diagnostics and de-AI writing repair. The `prose-*`
skills ship a runnable `scripts/measure.py` + `tests/`, so each "try it as an
experiment" is a real command you can run.

| Skill | Tags | What it does |
|-------|------|--------------|
| [prose-rhythm](writing/prose-rhythm/SKILL.md) | `prose` `readability` `burstiness` `diagnostic` `english-only` | Sentence-length variation (burstiness/CV) diagnostic for English prose; flags uniform vs. choppy rhythm. No detector verdicts. |
| [prose-lexical-variety](writing/prose-lexical-variety/SKILL.md) | `prose` `lexical-variety` `perplexity-proxy` `diagnostic` `english-only` | Lexical variety diagnostic (TTR / rare-word / entropy) for English prose; flags low vs. high variety. No detector verdicts. |
| [sepia](writing/sepia/SKILL.md) | `writing` `de-ai` `fiction` `professional-prose` `narrative` | De-AI writing repair: narrative-architecture fixes for fiction, venue-matched rules for professional prose. Based on StoryScope (arXiv:2604.03136). |

## Contributing a skill (beginner-friendly on purpose)

1. `python3 new_skill.py "your-skill-name" --category <category>` — or copy
   `_template/` by hand if you prefer seeing the mechanics.
2. Fill in the four sections: **When to use / Instructions / Pitfalls /
   Try it as an experiment**. If you can't name a concrete experiment for it,
   the skill is probably too vague — that's the quality bar.
3. Add frontmatter `tags:` so the index stays filterable.
4. Add a row to the category table above, then commit:
   `skill: <name>`.

That's the whole process. No build step, no CI gate for markdown — the
skills live next to runnable experiments so every skill can point at
something you can actually run.
