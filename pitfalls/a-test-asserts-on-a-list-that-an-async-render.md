# A test asserts on a list that an async render has not drawn yet

Date: 2026-10-21 · Tags: `testing` `async` `race` `javascript`

## Symptom

A smoke test drives the real listeners with synthetic events, then checks the
result. It fails, and it fails *nondeterministically* — the same code, same
events, sometimes green:

```text
[smoke] home-check: {"visible":true,"cards":0,"listAfterCreate":2,...} FAIL
[smoke] home-check: {"visible":true,"cards":1,"listAfterCreate":2,...} PASS
```

`cards: 0` on a panel that is `visible: true`. The overlay is on screen and it
is empty.

## The wrong assumption

"`visible: true` means the render finished."

It means the *panel* exists. The list inside it is populated by a promise:

```js
function renderHome(on) {
  showHome(on);
  return listBoards().then(boards => {   // ← async boundary
    el.innerHTML = boards.map(boardCard).join('');
  });
}
```

The caller asserts immediately after showing the panel, so it reads the DOM
before the `.then` has run. Whether it passes depends on how quickly the IPC
round-trip resolves — which is exactly the kind of thing that is fast on an
idle machine and slow in CI.

## Spot it in 5 seconds

Check whether the thing you assert on is populated by an `await`, a `.then`,
or a callback. Then check whether your test awaits **that**, or only the
synchronous part of the call:

```bash
grep -n "function renderHome" -A6 renderer/app.js   # does it return a promise?
grep -n "renderHome(" renderer/app.js                # do callers await it?
```

The tell is a function that **has** a `return` of a promise (someone thought
about this) while its caller uses it as if it were synchronous.

## Fix

Return the promise from the render function and await it at every call site,
including inside the page-executed test hook:

```js
// bad: shows the panel, asserts on an empty list
showHome(true);
return { visible: true, cards: countCards() };

// good: await the paint, then assert
await renderHome(true);
return { visible: true, cards: countCards() };
```

Two habits that keep this from coming back:

- **Any function that triggers an async update should return that promise**, so
  it is *possible* for callers to wait. A `void` return turns a race into a
  landmine.
- **Assert on data, then on pixels**, in that order. Checking "2 boards were
  created" against the model first and only then "2 cards are in the DOM"
  separates "the write failed" from "the paint was late".

## Globalise it

Every "the list is empty" failure that is actually "the list is not here yet":

- Waiting for a network response, then asserting on the parsed result
- Waiting for a file watcher to fire, then reading the file
- Waiting for a DB migration, then querying the new column
- Waiting for a worker to drain a queue, then counting the output

The general rule: **the assertion should be ordered after the promise, and the
API should make that ordering expressible.** A function that performs an async
side effect but returns nothing is the actual defect — it makes the race
unavoidable for every future caller, not just today's test.

## Evidence

```text
# before — renderHome() was fire-and-forget
[smoke] home-check: {"visible":true,"cards":0,"listAfterCreate":2,"ok":false} FAIL

# after — renderHome() returns a promise and the hook awaits it
[smoke] home-check: {"visible":true,"cards":1,"created":true,"opened":true,
                     "listAfterCreate":2,"hasNew":true,"renamed":true,
                     "renameVisible":true,"deleted":true,"listAfterDelete":1,
                     "ok":true} PASS
```

Note that `listAfterCreate` was correct in *both* runs — the data was always
there. Only the DOM count was late, which is what identified it as a race
rather than a broken feature.

## Takeaway

If a function triggers an async update, return that promise so callers can wait
— and assert on the model before the pixels. A "list is empty" result whose
data count is correct is a race, not a bug.