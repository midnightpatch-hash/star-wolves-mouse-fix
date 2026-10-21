# Reproduce v1.1.0

These tools operate on local files only and never execute the game.
Keep an unmodified original or a backup such as `StarWolves.exe.backup`.

## 1. Apply the explicit byte manifest

Requirements: Python 3.9+ only. No pip packages, admin access, or network
access are needed.

From the repository root:

```bash
python3 patch.py "/path/to/StarWolves.exe.backup" --verify-only
python3 patch.py "/path/to/StarWolves.exe.backup" -o "build/StarWolves.exe"
```

The first command checks the input and complete patch result without writing.
The second creates a separate output. Use a fresh output filename if it already
exists. There is deliberately no force-overwrite option.

On Windows:

```powershell
py -3 patch.py "C:\Games\Star Wolves\StarWolves.exe.backup" -o "build\StarWolves.exe"
```

If the input hash does not match, stop. Check that you selected the unmodified
original rather than an earlier patched version. Do not bypass the hash check.

## 2. Assemble the four code fragments yourself

Requirements: Python 3.9+ and **GNU Binutils** providing `as`, `ld`, `objcopy`.
The assembly uses GNU Intel syntax for 32-bit x86. This path was verified with
the toolchain versions recorded in [VALIDATION.md](VALIDATION.md).

```bash
python3 build.py --check-sources
python3 build.py "/path/to/StarWolves.exe.backup" -o "build/from-source.exe"
```

`--check-sources` needs no game EXE. It assembles, links at the original virtual
addresses, extracts `.text`, and checks every resulting byte against the manifest.
The second command uses those newly assembled fragments, applies the remaining
hook/constant/PE metadata records, and checks the whole output SHA-256.

This reproduction path intentionally rejects source changes that no longer match
v1.1.0. Developing a new patch version requires reviewing and updating the
corresponding manifest records and output hash as well.

The Python patcher works without installing Binutils. SteamOS users do not need
to disable filesystem protection or install system packages just to apply it.

## 3. Verify the output independently

Linux / SteamOS:

```bash
sha256sum build/StarWolves.exe
```

Windows PowerShell:

```powershell
Get-FileHash .\build\StarWolves.exe -Algorithm SHA256
```

Expected v1.1.0 hash:

```text
4b2ceb680fcc6fdf58f5e4bdfec16f4f11eda00511d2c254e7ddef624d5d3d33
```

You can also compare your result directly with the downloaded release asset
using `cmp` on Linux or a file-hash comparison on Windows.

## 4. Run the published tests

```bash
python3 -m unittest discover -s tests -v
```

The assembly check is skipped if GNU Binutils is unavailable. To enable the
integration test against your own original EXE on Linux / SteamOS:

```bash
STAR_WOLVES_ORIGINAL="/path/to/StarWolves.exe.backup" python3 -m unittest discover -s tests -v
```

No copyrighted fixture is bundled. The tests do not launch the game or emulate
the complete game. They cover patcher guards, file preservation, the real
reproduction path when an original is supplied, and source-to-byte agreement.

## Installation after reproduction

Close the game, retain a backup, and copy the generated EXE into the game
folder as `StarWolves.exe`. Use fullscreen for the per-frame cursor preview.
If previously enabled, disable the system cursor in `Main.ini`:

```ini
[GRAPH]
NeedWindowsMouses = 0
```

No game FPS cap is required by this fix. The source release does not change
the behavior of the existing v1.1.0 executable.
