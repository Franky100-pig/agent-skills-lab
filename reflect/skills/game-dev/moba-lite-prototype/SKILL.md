---
name: moba-lite-prototype
description: "Step-by-step plan to prototype a mini-MOBA in pygame: top-down controller, auto-attacks, cooldown abilities, bot AI state machine, economy ticks, match logging. Use when building a MOBA prototype or any top-down bot arena. Triggers: MOBA prototype, top-down, auto attack, bot AI, state machine."
---

# MOBA-Lite Prototype (pygame)

A concrete build order for a 1v1-lane MOBA slice. Goal: playable in a weekend,
not a full game.

## When to use

- Starting a MOBA prototype and wanting a build order.
- Building any top-down game with ability cooldowns and simple bot AI.

## Instructions (build in this order — each step is playable)

1. **Camera + top-down controller.** Right-click-to-move (MOBAs are
   click-to-move, not WASD). Circle collision vs walls.
2. **Auto-attack.** Nearest enemy in range, with a windup + projectile or
   instant hit. Add attack speed as a stat now, even if trivial.
3. **Two abilities with cooldowns.** One damage nuke (targeted or line
   skillshot), one mobility dash. Draw a cooldown sweep on a HUD bar.
4. **Economy ticks.** Gold per second + gold per minion kill. A "shop" that is
   just 3 buttons raising damage / move speed / HP. Items before content.
5. **One minion wave.** 3 melee + 1 ranged per side every 20 seconds, marching
   down a lane, attacking whatever is in range. Minions ARE the economy.
6. **Bot enemy = state machine.** FARM, ATTACK_IF_KILLABLE,
   RETREAT_BELOW_30%_HP. No pathfinding needed if the lane is a straight line.
7. **Win condition + match log.** First to destroy a core, or first to N
   kills. Log gold/XP/kills per minute to a CSV — that is your balance data.

## Pitfalls

- Building 5 heroes before 1 fun lane. One hero vs one bot first.
- Real pathfinding (A*) too early — straight lanes delay the need for weeks.
- Skillshots without clear hitboxes — use circles and rectangles first.
- Making abilities cost mana before costs feel meaningful.

## Try it as an experiment

Steps 1-3 alone (controller + auto-attack + 2 cooldowns vs a dummy bot) make a
great single `experiments/` entry — about 200 lines and already feels
MOBA-ish.
