# Star Wolves — Mouse Fix

**Smooth mouse movement with the original in-game cursor.**

An unofficial mouse fix for the original **Star Wolves** on Steam.
It fixes discarded mouse movement and updates the in-game cursor before each frame.

> Tested on SteamOS with Proton. The additional cursor updates work in
> full-screen mode. Windows has not been tested yet.

## Download

### [⬇ Download the latest release](https://github.com/midnightpatch-hash/star-wolves-mouse-fix/releases/latest)

Under **Assets**, download `StarWolves_MouseFix.zip` and extract it. The archive contains the patched `StarWolves.exe`. Follow the installation instructions below.

## What does it fix?

If the cursor moves in visible steps, stutters, or feels like it drifts when
changing direction, the game's mouse handling may be the cause.

In the examined executable, normal mouse processing runs roughly 30 times per
second, even at much higher frame rates. When the mouse event buffer overflows,
the game also discards movement events that were successfully read.

This patch:

- increases the mouse event buffer and fixes overflow handling;
- updates the cursor position before each rendered frame;
- keeps the original in-game cursor;
- preserves the original game logic timing and normal button and wheel handling.

At 60 FPS, the cursor can update up to 60 times per second; at 120 FPS, up to 120.
A 60 FPS cap is not required for this fix.

## Installation

1. Close the game completely.
2. In Steam, open **Properties → Installed Files → Browse**.
3. Rename the original `StarWolves.exe` to `StarWolves.exe.backup`.
   If a backup already exists, keep it and use a different backup filename.
4. Copy `StarWolves.exe` from the downloaded archive into the game folder.
5. Start the game in **full-screen mode**.

If you previously enabled the Windows cursor, open `Main.ini` and set the
following option in the `[GRAPH]` section:

```ini
NeedWindowsMouses = 0
```

The name ends with an **s**. The supplied original `Main.ini` used
`NeedWindowsMouse`, while the executable reads `NeedWindowsMouses`.

## Compatibility

| Item | Status |
| --- | --- |
| Game | The original Star Wolves on Steam |
| SteamOS / Proton | Confirmed working on the player's machine |
| Full-screen mode | Additional cursor updates enabled |
| Windowed mode | Additional cursor updates disabled |
| Windows | Not tested yet |
| Other executables and sequels | Not tested; the patch was built for the supplied executable of the first game |

## Uninstall

Close the game, remove the patched executable, and rename your backup to
`StarWolves.exe`. Steam's **Verify integrity of game files** option also restores
the original executable and replaces the installed patch.

## How it works

The original input handler continues reading mouse events at its normal interval.
Before each frame, the added handler previews queued movement using
`GetDeviceData` with `DIGDD_PEEK` and updates the original cursor's position.

Previewing leaves events in the queue and does not add movement a second time
to the game's accumulated internal coordinates. Buttons and wheel events remain
available to the normal handler. The game timer code is unchanged.

The archive includes the added handler's source (`preview_cursor.s`), exact patch
offsets and SHA-256 hashes (`changes.json`), and emulator verification results.
The patched executable passed 17 checks of the new handler and 14 checks of the
previous buffer fix. Full-game behavior was then tested by the player on SteamOS.

## Feedback

If you try the patch on another setup, please open an **Issue** and include:

- your operating system and Proton version, if applicable;
- whether you used full-screen or windowed mode;
- whether cursor movement improved and clicks, scrolling, and drag selection work correctly.
