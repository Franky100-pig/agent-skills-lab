---
name: data-driven-tuning
description: "Workflow for game balance without code edits: externalize stats to JSON/CSV, hot-reload mid-session, log matches, turn logs into one balance decision at a time. Use when tuning weapons/heroes or analyzing match data. Triggers: balance, tuning, stats file, hot reload, match log, winrate, SQLite."
tags: [game-dev, balance, json, telemetry]
---

# Data-Driven Tuning

Stop recompiling (or restarting) to change a damage number. Numbers live in
data; code reads data; matches write logs; logs drive the next change.

## When to use

- Tuning weapons, heroes, or difficulty repeatedly.
- You have match data (GEOM AIM already logs to SQLite) and are not sure what
  to do with it.

## Instructions

1. **Externalize every number.** One `weapons.json` (or CSV): damage, fire
   rate, spread, recoil, TTK targets. Code references names, never literals.
2. **Load once at startup, hot-reload on a keypress.** An `R` key that
   re-reads the file mid-game turns a tuning session from minutes into
   seconds.
3. **Log the match, not the feelings.** Per match: mode, weapon, difficulty,
   result, duration, accuracy. You already have this in SQLite — extend that
   schema, do not replace it.
4. **Turn logs into ONE decision per session.** Query winrate by weapon x
   difficulty, find the worst outlier, change one number, play again.
5. **Version the data file.** Commit per tuning change (or `weapons_v2.json`)
   so a bad change is one `git checkout` away from reverted.

## Pitfalls

- Nesting config three levels deep "for flexibility" — flat tables win.
- Tuning from memory after 10 plays instead of from logged stats.
- Changing 3 numbers at once: now you learn nothing from the result.
- Hot-reload code that leaks state — reset every cached derived stat on reload.

## Try it as an experiment

Extract ONE weapon's stats from GEOM AIM into `weapons.json`, add an R-key
reload, and change its damage mid-session without restarting the game.
