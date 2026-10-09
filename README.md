# Star Wolves — Mouse Fix & Quality-of-Life Patch

A community patch for the **first Star Wolves from Steam**, with a smoother mouse cursor, finer sensitivity controls and an improved resolution menu.

**[Download the latest release](https://github.com/midnightpatch-hash/star-wolves-mouse-fix/releases/latest)**

Download the attached **StarWolves.exe**. GitHub's automatically generated source-code archives do not contain the patched executable.

## What does it fix?

The original game updates its in-game cursor at roughly 30 Hz, even when the game runs at a much higher frame rate. It can also discard accumulated mouse movement when its input queue overflows. This can make the cursor move in steps, jerk or drift when changing direction.

The patch fixes movement loss and updates the cursor before each rendered frame in fullscreen mode.

- Preserves the original in-game cursor.
- Does not change game speed.
- Does not require a special 60 FPS limit.
- Does not require lowering your mouse's hardware polling rate to use the fix.

## Added in v1.1.0

### Compact resolution menu

The menu shows the following resolutions in **32-bit color only**, when reported as supported by your system:

| Aspect ratio | Resolutions |
| --- | --- |
| 4:3 | 1024×768, 1600×1200 |
| 5:4 | 1280×1024 |
| 16:9 | 1280×720, 1920×1080, 2560×1440, 3840×2160 |

Unsupported modes are not forced. This is a resolution-menu change; it does not redesign the interface for widescreen displays.

### Finer mouse sensitivity

- **20 steps**, from **0.125 to 2.500**.
- Each click changes sensitivity by **0.125**.
- The indicator displays 20 segments within the original menu layout.
- The game's **Defaults** button sets mouse sensitivity to **1.000**, at position **8**.

Existing sensitivity settings are rounded to the nearest new step and limited to the new range when you open the options menu. For example, an old value of 3.000 becomes 2.500.

For a starting point of 1.000 without resetting other options, move sensitivity to its minimum, then click the increase button seven times. Click **Apply** to save.

### Black startup background

Replaces the brief white window background before the 1C intro with black.

## Installation

1. Close the game.
2. In Steam, open **Star Wolves → Properties → Installed Files → Browse**.
3. Rename the original `StarWolves.exe` to `StarWolves.exe.backup`. If you already use an earlier patch, keep a separate backup of that working EXE too.
4. Copy the downloaded `StarWolves.exe` into the game folder.
5. Launch the game in **fullscreen mode**.

Fullscreen is required for the additional per-frame cursor updates.

If you previously enabled the Windows/system cursor while troubleshooting, set the following in `Main.ini`:

```ini
[GRAPH]
NeedWindowsMouses = 0
```

The setting name is `NeedWindowsMouses`, with an **s** at the end.

## Compatibility

Tested on **SteamOS with Proton 10.0-4**. The cursor fix, resolution menu, 20-step sensitivity controls and black startup background have been tested in the game.

**Windows has not been tested yet.**

This patch is for the **first Star Wolves from Steam**, not Star Wolves 2 or Star Wolves 3.

## Uninstall

Close the game, remove the patched EXE and restore your backup as `StarWolves.exe`.

Steam's **Verify integrity of game files** option also restores the original executable. If you return to the original sensitivity menu, adjust sensitivity there if necessary.

## Previous releases

[v1.0.0](https://github.com/midnightpatch-hash/star-wolves-mouse-fix/releases/tag/v1.0.0) contains the original mouse cursor fix without the additional v1.1.0 features.
