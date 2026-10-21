# Unpinning does nothing because the pointer is still on the card

Date: 2026-10-21 · Tags: `state-machine` `verification` `interaction` `testing`

## Symptom

The key that is supposed to hand a frozen object back to the simulation does
nothing. Press it, wait, nothing moves. Press it again, nothing. The state
clearly changed — the flag flipped — yet the behaviour never does.

The user reports it as "this key is broken". It is not broken. It is
correctly flipping a flag that nothing downstream reads.

## The wrong assumption

"`unpin` and `wake up` are the same action."

They are two different flags, and a third one you forgot existed is still
holding the object. The integrator skips anything **hovered** — the pointer is
on it, so the hover flag is set — and hover is checked with the same guard as
the explicit pin:

```js
// the integrator
if (card.pinned || card.hover || card.dragging) continue;   // ← hover is here

function togglePin(card) {
  card.pinned = !card.pinned;
  wakeBranch(card.id);          // wakes... a card that is still skipped
}
```

So the wake is computed, applied to the branch, and discarded on the next step.
The flag that would have let the card move is the one nobody cleared.

The trap generalises: **any state you set from a handler can be silently
overridden by ambient state the handler cannot see.** The cursor position is
ambient. So is the current time, the network status, which tab is focused, and
whether a modal is open.

## Spot it in 5 seconds

Ask what else the execution path checks. Grep for the skip condition, then
grep for every flag in it:

```bash
grep -n "pinned ||" renderer/physics.js        # the integrator's guard
grep -n "hover = " renderer/*.js              # who sets it, who clears it
```

If a flag appears in the guard but is never cleared by the handler you are
debugging, that is the bug. The tell is in the **mismatch between the flags
you set and the flags the guard reads** — two different names for what the user
thinks is one piece of state.

Second tell, free: **can your test suite even express this?** If the fix only
matters while a pointer is over the object, then any test that drives the
simulator directly (no synthetic pointer) cannot fail before the fix or pass
after it. A green suite here is not evidence.

## Fix

Clear the ambient flag in the same handler that clears the explicit one, then
wake:

```js
// bad: wakes a card the integrator will still skip
function togglePin(card) {
  card.pinned = !card.pinned;
  wakeBranch(card.id);
}

// good: the card is now actually eligible to move again
function togglePin(card) {
  card.pinned = !card.pinned;
  if (!card.pinned) {
    card.hover = false;        // the pointer is on it; that alone was freezing it
    wakeBranch(card.id);
  }
}
```

Then **prove the test can fail**: run the suite once with the fix reverted and
confirm the assertion goes red. A test that never fails proves nothing.

## Globalise it

Any "do the thing" key that is inert while ambient state is present:

- Pointer hover / focus freezing an element while the user is literally
  touching it — the pointer can never leave, because the key is pressed *with*
  the pointer on it
- A `mouseleave` handler that never fires because the element moved out from
  under the cursor (same shape: state tracks a moving target)
- A save button disabled by `isDirty`, where clicking it *is* what sets `isDirty`
- Any "resume / retry / force" action gated behind "is not currently running",
  pressed while it is running

The general shape: **an action whose precondition is satisfied by the same
gesture that triggers it.** Whenever you write a handler, list every guard the
downstream code checks and clear each one the handler invalidates.

## Evidence

Smoke assertion, run against the packaged binary. Before the fix the drag
check reported the card as still frozen and un-unfloating; after, both flip:

```text
# without the fix
"drag":{"ok":false,"pinned":true,"heldStill":true,"floaty":true,"followed":false,"floatsAgain":false}

# with the fix
"drag":{"ok":true,"pinned":true,"heldStill":true,"floaty":true,"followed":true,"floatsAgain":true}
```

And the unit suite — 15 tests over the integrator — passed identically in both
runs. It never had a chance to notice.

## Takeaway

When a "do the thing" action is inert, check whether your handler cleared every
flag the downstream guard reads — not just the one the action is named after.
Then revert the fix and watch the test go red, because a test that cannot fail
is not a test.