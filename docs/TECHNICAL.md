# Technical notes for v1.1.0

## Scope and address conventions

This is a patch for one exact 32-bit x86 Steam executable. See
[SOURCE_README.md](../SOURCE_README.md) for the input and output hashes.
The preferred PE image base is `0x00400000`.

The manifest uses **file offsets**. The code ranges below happen to have equal
file offsets and RVAs in this EXE's `.text` section. Do not generalize that rule
to the `.reloc` section or other executables. A code offset `0x295070` is a
preferred virtual address of `0x695070` in this image.

All 32 replacements are listed in [PATCH_RANGES.md](PATCH_RANGES.md), with
literal original/replacement bytes in [the manifest](../patches/v1.1.0.json).
There is no compressed or encoded executable hidden in the Python scripts.

## Buffered mouse movement

The DirectInput mouse buffer and read request change from **64 to 128** records.
The local stack frame expands from `0x664` to `0xb64` bytes, with argument
references and epilogues adjusted consistently.

At file offset `0x239b4`, `JE` (`74`) becomes `JNS` (`79`) after the existing
result test. A nonnegative status, including `DI_BUFFEROVERFLOW`, can therefore
retain returned records; genuine failure HRESULTs still follow the error path.

This addresses lost motion on buffer overflow. It does not by itself increase
the regular input/logic update frequency.

## Per-frame cursor preview

The call at `0x8e855` is redirected to the wrapper at `0x295070`.
[`cursor_preview.S`](../src/cursor_preview.S) saves flags and general registers,
previews the cursor, restores state, then tail-jumps to the original render update.

The helper:

1. Checks the existing focus, fullscreen, cursor and input-enable state.
2. Calls `GetDeviceData` with `DIGDD_PEEK`, requesting at most 128 records.
3. Accumulates relative X/Y movement, excluding buttons and wheel events.
4. Applies existing sensitivity and authoritative cursor coordinates.
5. Clamps the preview to the current fullscreen bounds and updates the sprite.

The peek does not consume events. Visible preview coordinates are separate from
the authoritative position used as the next preview baseline. This avoids
integrating the same pending movement repeatedly. The ordinary handler still
consumes movement, buttons and wheel events on its existing schedule.

The preview is tied to render calls in fullscreen. There is no added FPS limiter,
timer change or attempt to change the mouse hardware polling frequency.

## Resolution menu

The inline filter at `0x104755` retains these dimensions when the game's
enumeration reports them:

| Aspect ratio | Modes |
| --- | --- |
| 4:3 | 1024x768, 1600x1200 |
| 5:4 | 1280x1024 |
| 16:9 | 1280x720, 1920x1080, 2560x1440, 3840x2160 |

The original subsequent pixel-format check keeps only 32-bit modes.
Its `JNE` at `0x1047fc` is redirected to the small trampoline at `0x1047d5`,
which rejoins the original advance path at VA `0x504976`. Rejected dimensions
take the path to VA `0x504984`.

This branch correction is part of the final patch and avoids the rejected-depth
path that crashed in an earlier development build. Mode ordering and the rest
of the graphics-menu implementation remain the game's own. This is not a
widescreen UI redesign or a promise that unsupported display modes will appear.

## Sensitivity controls

The source at `0x295230` replaces the increase/decrease handlers, normalizes
saved values when opening the menu, and configures a 20-segment sensitivity bar.

The display index is based on `sensitivity * 8 + 0.5`, the game's original
float-to-integer helper, then a clamp to **1..20**. Adjustment adds or subtracts
one index and stores `index * 0.125`. The resulting range is **0.125..2.500**.

Reset changes the default constant at `0x10321d` from **3.0 to 1.0**; index 8
therefore represents the reset/default sensitivity.

The custom renderer divides the existing bar width into 20 segment positions
and restores the source sprite dimensions after drawing. Other step bars route
through the original renderer. Two obsolete HIGHLOW relocation entries at
`0x34f2b8` and `0x34f2d8` become ABSOLUTE/no-op entries because their old
absolute operands have been replaced by relative hook instructions.

## Startup window background

The five bytes at `0x90ff3` become a jump to `0x2954d0`. The helper preserves
the existing stack store, pushes stock brush **4 (BLACK_BRUSH)** instead of
**0 (WHITE_BRUSH)**, and returns to VA `0x490ff8` in the original setup path.

This targets the brief white window background before the intro. It does not
replace the intro video or game assets.

## PE metadata and limits of validation

The `.text` section's VirtualSize at file offset `0x230` increases from
`0x294062` to `0x2944db`, covering code placed in existing raw-section padding.
The file length and section count are unchanged.

The source-publication tools prove agreement with the saved v1.1.0 executable,
including all bytes outside declared ranges. They do not independently establish
runtime correctness on every machine or prove that the patch is free of bugs.
The in-game confirmation was on SteamOS/Proton; Windows runtime behavior has not
been confirmed. Historical development emulator reports are not a substitute
for the published, rerunnable test suite.
