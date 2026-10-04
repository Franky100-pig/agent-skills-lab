---
name: fps-game-feel
description: "Checklist for making an FPS feel good: input latency, hit feedback, recoil, crosshair states, TTK pacing, sound layering. Use when tuning gunplay, adding juice, or diagnosing that the shooting feels off. Triggers: game feel, juice, gunplay, recoil, TTK, hitmarker, screen shake."
tags: [game-dev, game-feel, gunplay, tuning]
---

# FPS Game Feel

What separates "it shoots" from "it feels good". A tuning checklist, not a
rendering guide.

## When to use

- Gunplay feels flat or off and you cannot name why.
- Adding new weapons and wanting consistent feel across them.
- Tuning difficulty pacing in an aim trainer.

## Instructions (tune in this order)

1. **Input latency first.** Fire on key-down, not key-up. Decouple game logic
   from rendering so a frame spike never delays a shot.
2. **Feedback on every shot and every hit.** Minimum set: muzzle flash, sound,
   crosshair kick, and a distinct hitmarker (different color/sound for
   headshots).
3. **Screen shake — small and rare.** 2-4 px, under 100 ms, camera-space, and
   never at full strength on every shot. Shake sells impact; overuse causes
   nausea.
4. **Recoil pattern vs random spread.** Deterministic patterns reward
   learning; small random spread keeps fights honest. Choose deliberately per
   weapon, not by accident.
5. **Crosshair states.** Expand while moving/shooting, tighten when standing
   still. Players read the crosshair more than any HUD number.
6. **TTK pacing.** Time-to-kill defines the whole feel: fast TTK = twitch and
   reflex (aim trainers), slow TTK = positioning and duels. Set it per mode,
   not globally.
7. **Sound layering.** A fire sound is attack transient + body + tail. A weak
   "pew" ruins good visuals; a layered shot sells power for free.

## Pitfalls

- Tuning visuals before latency. If input feels late, nothing else matters.
- Uniform feedback for every event — headshots must sound different.
- Juicing everything at max: contrast is what makes big moments big.
- Copying another game's numbers without its movement speed/FOV context.

## Try it as an experiment

Take one weapon in GEOM AIM and log: input-to-impact delay, shake magnitude,
TTK vs a training dummy. Change ONE variable per playtest session and keep a
note of what changed.
