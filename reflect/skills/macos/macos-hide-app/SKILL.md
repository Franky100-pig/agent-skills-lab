---
name: macos-hide-app
description: "Hide a macOS app from every user-visible surface (Launchpad, /Applications, Spotlight, Dock) without uninstalling it — and bring it back with one command. Use when someone wants an app to stop showing up. Triggers: hide app, hide software, Launchpad, Applications folder, Spotlight, macOS, App Store app, hide vs uninstall."
tags: [macos, launchpad, spotlight, app-management, reversible]
---

# macOS Hide App

Make an app vanish from Launchpad, the Applications folder, Spotlight and the
Dock — while the bundle stays byte-identical, launchable, and one `mv` away
from being restored. Built and verified on macOS 26.5 (Tahoe, Apple Silicon).

## When to use

- "Hide QQ / hide this app, I don't want to see it any more."
- An app should disappear from Launchpad and the Applications folder but must
  not be uninstalled (login state, files, future use).
- You want a quiet way back to an app you have "quit for good".

Do **not** reach for this when the user actually wants it gone permanently —
that is an uninstall (drag to Trash + clean up `~/Library` leftovers).

## Instructions

1. **Identify the app before touching it.** Its owner and signature decide
   which method is safe:

   ```bash
   P="/Applications/<App>.app"
   ls -ld "$P"                                    # root:wheel => admin-protected
   [ -d "$P/Contents/_MASReceipt" ] && echo "Mac App Store build" || echo "standalone"
   codesign -dv --verbose=4 "$P" 2>&1 | head -20 # Authority / TeamIdentifier
   spctl -a -vv "$P" 2>&1                        # accepted? source=Mac App Store?
   ```

2. **Never edit `Info.plist` on a signed or App Store app.** The common
   `LSUIElement = true` trick (removes the Dock icon and menu bar) only works
   on apps you built yourself. On a notarized / MAS app it breaks the
   signature: the app stops launching and loses auto-update for good.

3. **Move the bundle out of `/Applications` instead.** A hidden destination is
   enough:

   ```bash
   osascript -e 'do shell script "/bin/mkdir -p $HOME/.hidden-apps && /bin/mv \"/Applications/<App>.app\" \"$HOME/.hidden-apps/<App>.app\"" with administrator privileges with prompt "Move <App> to a hidden folder (reversible)"'
   ```

   `osascript ... with administrator privileges` raises the native password
   prompt. This is required because of **App Management protection** — a plain
   `mv` is refused even as an admin.

4. **Refresh the shell**

   ```bash
   killall Dock
   ```

5. **Verify all four surfaces are clear**

   ```bash
   ls -ld /Applications/<App>.app 2>&1 || echo "gone from /Applications ✓"
   mdfind "kMDItemCFBundleIdentifier == '<bundle.id>'" | head   # empty = Spotlight can't see it
   codesign --verify --verbose=1 ~/.hidden-apps/<App>.app       # valid on disk
   spctl -a -vv ~/.hidden-apps/<App>.app                        # accepted
   ```

6. **Optional: a launcher that stays out of sight.** Put a `.command` next to
   the app and add a shell alias — never on the Desktop, or you have undone the
   hiding:

   ```bash
   printf '#!/bin/zsh\nopen "$HOME/.hidden-apps/<App>.app"\n' > ~/.hidden-apps/Open<App>.command
   chmod 755 ~/.hidden-apps/Open<App>.command
   echo "alias <app>='open \"\$HOME/.hidden-apps/<App>.app\"'" >> ~/.zshrc
   ```

   Restore is the same move in reverse:

   ```bash
   osascript -e 'do shell script "/bin/mv $HOME/.hidden-apps/<App>.app /Applications/<App>.app" with administrator privileges' && killall Dock
   ```

## Pitfalls

- **A plain `mv` fails with `Permission denied` even as an admin.** App
  Management protection (macOS 14+) requires explicit authorisation for any
  process modifying another app. `sudo -n` is usually unavailable, so the
  `osascript` password prompt is the practical route. Disabling the command
  sandbox does **not** help.
- **Moving an App Store app is safe.** macOS resolves sandbox containers by
  bundle id, not by path, so a MAS app launches fine from anywhere. Data and
  login state survive in `~/Library/Containers/<bundle.id>`.
- **`pgrep -f "Safari"` counts itself.** When scripting checks, use `pgrep -x`
  (exact process name) or anchor the path: `pgrep -f '^/Applications/<App>\.app'`.
- **Hidden ≠ protected.** Anyone who sets Finder to show hidden files will see
  `~/.hidden-apps/`. This is tidiness, not security.
- **Launchpad lags a moment.** `killall Dock` forces the refresh; otherwise the
  icon can linger until the next login.
- **Updates stop.** An App Store app moved out of `/Applications` will not be
  updated. If that matters, move it back first.

## Try it as an experiment

Walk the whole loop in one terminal session, on any app you rarely open:

1. Record `codesign -dv` + `spctl -a` output **before** the move.
2. Move it, run `killall Dock`, then check all four surfaces (Launchpad,
   Finder → Applications, `mdfind`, Dock).
3. Launch it from the hidden path with `open`, quit it again, and confirm it
   did **not** reappear in Launchpad.
4. Move it back and diff the `codesign` / `spctl` output against step 1 — it
   should be identical, proving the bundle was never touched.
