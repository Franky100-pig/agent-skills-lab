# A screenshot comes back blank or half-drawn even though the page is fine

Date: 2026-10-21 · Tags: `electron` `screenshots` `verification` `timing`

## Symptom

You drive the app with synthetic events, then capture it. The PNG is wrong —
and wrong *differently* depending on the theme:

```text
# dark theme
[smoke] screenshot -> smoke.png  ink 0.000   ← looks like a total crash

# light theme
[smoke] screenshot -> smoke.png               ← "three of the six cards are missing"
```

You go looking for a rendering bug. There isn't one.

## The wrong assumption

"`capturePage()` returns the current frame."

It returns a frame from the compositor, and the compositor may not have caught up
with the DOM you just finished mutating. Roughly **1 in 3** captures came back
before compositing finished. Worse, the failure is *theme-dependent*: on a dark
canvas an uncomposited frame is uniformly black, which reads as "the app
crashed"; on a light theme you keep the background but lose the not-yet-drawn
cards, which reads as "some elements are broken". Same race, two convincing
lies.

The tempting wrong move is to add a delay. A fixed sleep makes it *less*
flaky-looking while still being wrong — you have just traded a visible race for
an invisible one that gets slower on a loaded machine.

## Spot it in 5 seconds

Prove the app is fine by querying the DOM instead of looking at the picture:

```js
// in the page, before capturing
const rects = [...document.querySelectorAll('.card')]
  .map(el => el.getBoundingClientRect());
console.log(cards.length, rects.every(r => r.width > 0 && r.height > 0));
```

If the DOM says six cards with real rectangles and the PNG shows three or none,
it is a capture race, not a render bug. Also measure the background colour
directly (`getComputedStyle`) — if it is the colour you set, the app painted
fine.

Then measure **how much of the frame is non-background**, and treat a low value
as a retry signal:

```js
const ink = countNonBackgroundPixels(png) / (w * h);
```

## Fix

Wait for the compositor instead of sleeping, then verify the result and retry:

```js
async function captureSettled(win, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    // two rAFs: one to schedule the frame, one to be sure it has been produced
    await win.webContents.executeJavaScript(
      'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))'
    );
    const img = await win.webContents.capturePage();
    const ink = await inkRatio(img);
    log(`attempt ${i}  ink ${ink.toFixed(3)}`);
    if (ink > INK_FLOOR) return img;      // it actually drew something
  }
  throw new Error('never composited');     // fail loudly instead of shipping a blank
}
```

The `ink` check is the important half: it turns a silent race into an explicit
retry with a printed reason. After this, captures hit on the first attempt
(`ink 0.046`) and a genuine regression still fails the build.

Related: in a sandboxed environment you may also need `--no-sandbox
--disable-gpu` and software rendering, or Chromium's OS-level sandbox
initialisation is rejected before you ever reach the race. That is a separate
problem with a similar-looking symptom, so check it before blaming timing.

## Globalise it

Any headless/automated capture of something that animates or renders
asynchronously:

- Puppeteer / Playwright `page.screenshot()` before fonts and images settle
- `view_image` on a canvas that draws in a `requestAnimationFrame` callback
- Video frame grabs that return a keyframe from before your state change
- Any "screenshot as a test assertion" — which also has the property that a
  blank frame *passes* unless you measure it

The general rule: **prefer waiting on a condition over waiting a duration**, and
assert on a measured quantity (ink ratio, element count, a checksum) so that
"empty" cannot masquerade as "fine".

## Evidence

```text
# before — the race, visible as a theme-dependent lie
[smoke] screenshot -> smoke.png ink 0.000 attempt 1

# after — two rAFs + ink-ratio gate
[smoke] screenshot -> smoke.png ink 0.046 attempt 1
```

DOM probe during the "broken" captures, confirming the app was fine all along:

```text
cards 6   all rects non-zero: true   background: rgb(0, 0, 0)
```

## Takeaway

An uncomposited frame reads as a render bug, not a timing bug. Wait on two
`requestAnimationFrame`s, measure the ink ratio, retry when it is too low — and
never ship a capture you did not assert on, because a blank frame otherwise
passes silently.