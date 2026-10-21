# A free swing angle orbits forever, and damping only makes it worse

Date: 2026-10-21 · Tags: `physics` `simulation` `debugging` `parameters`

## Symptom

Replace a stiff radial spring with a rope that constrains **distance only**
(direction free, so a child can swing around its parent). Everything looks
right at first — the branch follows the dragged card, there is no bounce, the
cards sit roughly where they should.

Then you wait. After 15 s the whole wall is still rotating around its anchors at
6–8 px/s, and it is not converging:

```text
speed @15s   6–8 px/s     (expected ~0)
angle        still steadily rotating
```

Raising global damping barely moves it. 0.95 → 0.985 makes it **slower**.

## The wrong assumption

"`damping` is the knob that makes a system settle."

Damping is only *half* of settling. A system settles when every mode has a
**restoring force**. If a mode has zero stiffness, damping controls nothing
except how slowly the free motion continues — a pure exponential decay of a
neutral mode with no centre to decay *toward*.

The arithmetic, which is visible once you write it down. A mass hanging on a
rope of length `r` with tension `F` has tangential stiffness:

```text
k_tangential = F / r
```

At 400 px with a tension of roughly 240: `k ≈ 0.6`. So the pendulum period is
`τ ≈ 27 s`. Global damping only rescales how fast you traverse that orbit; it
cannot create the missing centre. `0.95 → 0.985` doubled the time constant.

This is why the drag "works": the parent *moving* gives the tension a
transverse component, so the rope transmits the drag. It only becomes visible
once you let go and nothing is driving it.

## Spot it in 5 seconds

Compute the stiffness of the mode you think is settled and ask whether it is
zero. For a constraint-based system, ask the two questions separately:

```bash
# 1. does the constraint fix a DISTANCE only? -> one direction is unconstrained
# 2. what supplies a force along that direction? -> if nothing does, it's neutral
```

Cheap empirical tell: **run with damping at two very different values and see
whether the residual motion shrinks proportionally or just gets slower.** A
damped spring's residual falls fast. A neutral mode's residual is a decaying
orbit, and damping turns it into a slower decaying orbit — the tail gets
*longer*, not shorter.

## Fix

Add a separate, deliberately **weak** restoring term for the unconstrained
direction, rather than more damping:

```js
// angle memory: the rope stays the primary constraint; this only restores DIRECTION
if (cfg.anchorStiffness > 0) {
  var mx = card.x - anchor.x, my = card.y - anchor.y;
  card.fx -= mx * cfg.anchorStiffness;
  card.fy -= my * cfg.anchorStiffness;
  if (pcard) { pcard.fx += mx * cfg.anchorStiffness; pcard.fy += my * cfg.anchorStiffness; }
}
```

Two rules that make it behave:

- **Much weaker than the primary constraint** (30 vs 60). Strong enough to give
  the mode a centre, weak enough that the swing is still visible while you drag.
- **Symmetric**: push the reaction into the parent, or the force field becomes
  non-conservative and pumps energy into the system. Same discipline as for any
  internal force.

Note what this is *not*: making the rope stiffer. Stiffening the rope does not
add a tangential component — a rope's tension is purely radial, so no rope
parameter can ever fix a free angle.

## Globalise it

Any simulation where you swapped a spring for a weaker, more "physical"
constraint — rope, distance joint, inequality constraint, hard contact without
tangential friction:

- The neutral-mode trap appears wherever a constraint removes one degree of
  freedom and you assume the remaining ones still have a centre
- Frictionless contact is the same shape: normal force without tangential force
  means sliding forever
- In animation, a "pendulum on a rope" rig that never comes to rest
- Symplectic / energy-conserving integrators: a wrong reaction-force sign shows
  up as exactly this slow orbit, not as an explosion

The general lesson: **before you tune damping, inventory the modes and check
each has a restoring force.** Damping an undamped mode is not tuning, it is
just choosing the orbit size.

## Evidence

Six-card tree, dragged 400 px, then released. Each row is the same code with
one parameter changed.

| Configuration | Residual @15 s | Outcome |
|---|---|---|
| Rope only, `damping 0.95` | 6–8 px/s | rotating, not converging |
| `damping 0.985` (more!) | slower still | τ scaled up, no centre created |
| `swingDamp` 0 / 0.6 / 1 | all orbit | tangential damping alone insufficient |
| Skip parent–child repulsion | still orbits | **and 3 unit tests broke** — reverted |
| Rope + `anchorStiffness 30` | creep < 0.1 px / 5 s | settles, then fully dormant |

Two facts worth keeping: raising damping *lengthened* the tail, and removing a
force entirely changed nothing about the orbit — both signatures of a mode with
no stiffness rather than too little damping.

## Takeaway

Damping cannot settle a mode that has no restoring force. When you loosen a
constraint until a direction is free, compute that direction's stiffness
(`F/r` for a pendulum): if it is ~0, add a weak explicit restoring term rather
than more damping — and push its reaction into the parent so the force field
stays conservative.