# Star Wolves v1.1.0 — patch source and reproducible tooling

This repository supplement makes the existing **v1.1.0** executable patch
inspectable and reproducible. It does not introduce a new game patch version.

The game's original source code is not available here. This is a binary patch:
original x86 assembly for the added cursor and sensitivity routines, reconstructed
assembly for the resolution and startup changes, an explicit byte manifest,
and Python tooling to reproduce the supported patched EXE.

No original or patched game executable is included in this source package.
You need your own unmodified copy of the supported Steam executable.

## Files to inspect

| File | Contents |
| --- | --- |
| [`patch.py`](patch.py) | Portable, offline patcher with input/output hashes and original-byte guards |
| [`build.py`](build.py) | Reassembles all four source fragments with GNU Binutils and rebuilds the EXE |
| [`src/cursor_preview.S`](src/cursor_preview.S) | Recovered original source of the per-frame cursor preview |
| [`src/sensitivity.S`](src/sensitivity.S) | Recovered original source of the 20-step sensitivity controls and renderer |
| [`src/resolution_filter.S`](src/resolution_filter.S) | Readable assembly reconstructed from the released resolution filter |
| [`src/startup_background.S`](src/startup_background.S) | Readable assembly reconstructed from the black-background hook |
| [`patches/v1.1.0.json`](patches/v1.1.0.json) | Every replacement: file offset, before/after bytes and purpose |
| [`docs/PATCH_RANGES.md`](docs/PATCH_RANGES.md) | Index of all 32 replacement ranges |
| [`docs/TECHNICAL.md`](docs/TECHNICAL.md) | Explanation of the hooks, offsets and limitations |
| [`docs/BUILDING.md`](docs/BUILDING.md) | Reproduction and verification instructions |
| [`tests/test_patcher.py`](tests/test_patcher.py) | Patcher guard tests, source checks and optional real-EXE integration test |

## Quick reproduction

Requires **Python 3.9 or later**, with no third-party Python packages.
Run from the repository folder:

```bash
python3 patch.py "/path/to/original/StarWolves.exe" -o "build/StarWolves.exe"
```

On Windows, use `py -3` instead of `python3` if that is your Python launcher.

The script verifies the exact original, checks every original-byte guard,
applies the replacements in memory, and verifies the complete output hash
before writing. It never downloads anything, launches the game, modifies the
input, or overwrites an existing output.

To assemble the source fragments yourself, see [BUILDING.md](docs/BUILDING.md).

## Supported executable and reproducible result

Both executables are **3,661,824 bytes**.

**Original SHA-256:**

```text
5942489ba04d2ab6cce996b21f5e1ea806e439f8d36ec10e7d8b7c8749a44804
```

**Patched v1.1.0 SHA-256:**

```text
4b2ceb680fcc6fdf58f5e4bdfec16f4f11eda00511d2c254e7ddef624d5d3d33
```

A different input is rejected, even if it is another legitimate edition of
the game. These offsets have only been established for this exact executable.

## Provenance and validation

The cursor and sensitivity assembly was recovered from the original development
archives. The resolution and startup assembly was reconstructed from those
archives' exact released byte changes. The Python patcher, build tooling and
tests were prepared later for publication; they are not claimed to be the
original historical build scripts.

Both the manifest-based patcher and the assembly-based build were checked
against the archived final v1.1.0 EXE and reproduced it byte for byte.
All four assembled fragments also match its machine code exactly.
There are **1,085 changed bytes** in **32 declared replacement ranges**.

The existing release was tested in-game on SteamOS with Proton 10.0-4.
This source-publication work does not constitute a new Windows runtime test.
The original development emulator harness is not part of this package; older
test counts are not presented as rerunnable tests here.
