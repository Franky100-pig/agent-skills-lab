---
name: debug-frame-drops
description: "Diagnose game performance problems systematically: measure frame times, profile with cProfile, find the real bottleneck before optimizing. Use when the game stutters, drops frames, or feels slow. Triggers: frame drop, stutter, lag, profiling, FPS optimization, cProfile."
---

# Debug Frame Drops

Measure first, optimize second. Most "obvious optimizations" target the wrong
thing.

## When to use

- Frame drops, stutter, or input feels laggy.
- About to optimize something and want to check it is actually the problem.

## Instructions

1. **Frame-time, not FPS.** An FPS average hides spikes (60 fps average can
   still stutter with 3 frames of 100 ms). Log per-frame milliseconds and look
   for spikes.
2. **Find WHEN, not just WHAT.** Does it drop on spawn, on explosion, when
   many enemies are visible? Correlate spikes with game events before
   profiling anything.
3. **Profile with cProfile.** `python3 -m cProfile -s cumulative game.py` —
   read the top of the cumulative column. The top self-time function is your
   target; everything else is noise until that is fixed.
4. **Common pygame bottlenecks, in order of likelihood:** per-pixel work in
   Python loops (move it into surfaces/rects), re-blitting an unchanged
   background, creating Surfaces or fonts every frame (cache them), and
   pygame.draw calls that could be one pre-rendered surface.
5. **Fix one thing, re-measure.** Frame-time log before AND after, or you are
   just vibing.
6. **Budget check.** 60 fps = 16.6 ms per frame for logic + render + flip. If
   it does not fit, cut work — do not micro-optimize.

## Pitfalls

- Optimizing a function that is 2% of frame time because it "looks slow".
- Profiling with debug-only overhead (logging, debug draw) skewing results.
- Treating a vsync-locked 60 as a bug — a locked framerate is not a bottleneck.
- Micro-optimizing Python where the real fix is "draw fewer things".

## Try it as an experiment

Add a frame-time graph overlay (top-right, rolling last 120 frames) to GEOM
AIM or any pygame project — one surface plus a deque of floats. It pays for
itself forever.
