---
name: moba-design-primer
description: "Core design concepts of MOBA games: laning, economy, hero kits, itemization, snowball control, balance process. Use when designing a MOBA hero/mode, analyzing a match, or prototyping. Triggers: MOBA, lane, hero kit, farming, itemization, snowball, balance."
---

# MOBA Design Primer

What makes a MOBA tick, compressed. For when you want to design or analyze,
not just play.

## When to use

- Designing a hero kit, a mode, or a mini-MOBA.
- Analyzing why a match felt snowbally or stalemated.
- Deciding what to cut from a MOBA prototype.

## Instructions (the anatomy)

1. **The core loop is risk-vs-reward over time.** Farming = safe small
   income; fighting/roaming = risky big income. Every system (gold, XP,
   objectives) just tunes this dial.
2. **Hero kit anatomy:** passive + 3-4 actives. Budget each with cooldown +
   mana + cast time. A kit needs a damage tool, a mobility/escape, and one
   signature mechanic that defines its identity.
3. **Economy = gold + XP, and they diverge.** Gold comes from last-hits and
   kills; XP is shared by proximity. That split is what creates the support
   role.
4. **Items are the comeback lever.** The losing team farms safer ground and
   buys cheaper power spikes; itemization is how skill re-enters a lost game.
5. **Snowball control.** Kill gold should scale DOWN with how far ahead the
   killer already is (bounty/shutdown gold) — otherwise first blood ends
   games.
6. **Objectives beat kills.** Towers and dragons force fights at predictable
   times, which turns chaos into strategy.
7. **Balance is data, not opinion.** Track winrate BY SKILL BRACKET — a hero
   at 45% in low elo and 55% in high elo is a different problem than 50%
   flat.

## Pitfalls

- Designing kits around a cool idea instead of role + budget.
- Ignoring XP sharing — it silently defines every role.
- Buffing raw damage to fix an underpowered hero (usually the real problem is
  mobility or uptime).
- Symmetric maps with no asymmetric pressure — the game becomes a staring
  contest.

## Try it as an experiment

Take any hero you know and rebuild their kit on paper with a budget table
(cooldown / mana / damage per ability). Then explain to yourself why the real
kit spends its budget differently than yours.
