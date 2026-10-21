## Source code and reproducible patching

The patch source and offline build tools are available in this repository.
See [the source overview](SOURCE_README.md), [technical notes](docs/TECHNICAL.md)
and [build instructions](docs/BUILDING.md).

The added cursor and sensitivity routines are included as x86 assembly source.
The resolution and startup changes also have readable assembly, and every byte
replacement is documented in [the patch manifest](patches/v1.1.0.json).

You can reproduce v1.1.0 from your own supported, unmodified Steam EXE:

```bash
python3 patch.py "/path/to/original/StarWolves.exe" -o "build/StarWolves.exe"
```

The patcher validates the original and the completed result by SHA-256. A second
build path reassembles the source fragments with GNU Binutils. Both paths were
verified to reproduce the archived v1.1.0 EXE byte for byte. No original game
source code or game executable is included in the source package.
