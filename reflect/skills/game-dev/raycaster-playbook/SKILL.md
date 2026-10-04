---
name: raycaster-playbook
description: "Playbook for building a pseudo-3D raycast FPS (Wolfenstein/Doom style) from scratch. Use when building or debugging a raycaster, porting one, or explaining DDA rendering. Triggers: raycaster, raycasting, pseudo-3D, DDA, wall rendering, FOV, fisheye."
---

# Raycaster Playbook

How to build a Wolfenstein-style pseudo-3D shooter from a 2D grid map. Written
for pygame-first projects (GEOM AIM) but the math is engine-agnostic.

## When to use

- Building a raycaster from scratch or debugging one (walls look wrong, fisheye, jitter).
- Porting a 2D-grid raycaster to another engine (e.g. pygame to UE5).
- Explaining how Doom/Wolf3D-style rendering works.

## Instructions

1. **Map = 2D grid.** Walls live in a matrix (0 = empty, N = wall type).
   Player is a position + direction angle. No true 3D anywhere.
2. **Cast one ray per screen column.** For each column x, compute the ray
   angle from the camera plane, then step the ray through the grid with DDA
   (Digital Differential Analysis) until it hits a wall. DDA steps cell-by-cell
   along the dominant axis — never sample-and-move in tiny increments.
3. **Perpendicular distance, not Euclidean.** Use the distance projected onto
   the camera direction. This kills the fisheye effect in one move.
4. **Column height = constant / perp_dist.** Draw a vertical slice centered on
   the horizon; taller when close, shorter when far. Shade by distance or wall
   side (N/S vs E/W) for depth cues.
5. **Textures (optional).** Compute the exact hit coordinate along the wall,
   sample the texture column, draw it slice by slice.
6. **Sprites.** Transform sprite positions into camera space, sort far to near,
   draw with a per-column z-buffer so walls occlude correctly.
7. **Movement.** Move along the direction vector; for wall sliding, test x and
   y movement separately so players glide along walls instead of sticking.

## Pitfalls

- Fisheye: caused by Euclidean distance. Fix with perpendicular distance.
- Jitter at long range: floating-point drift in DDA — compare cell
  coordinates, not exact hit points.
- Frame drops at high FOV/resolution: per-column work is the classic
  bottleneck. Cache columns, precompute ray angles for the current FOV.
- Collision: checking the player as a point makes corners sticky — use a
  small radius and per-axis movement.

## Try it as an experiment

Render a single-color raycaster of an 8x8 map at 320x200 with no textures in
~100 lines. Then add a fisheye ON/OFF toggle and see the difference with your
own eyes.
