# Validation of the source publication

Date: **2026-10-21**. Environment: Linux, Python **3.12.14**, GNU assembler,
linker and objcopy **2.42** (`x86_64-linux-gnu`, using 32-bit x86 output).

## Results

| Check | Result |
| --- | --- |
| Original input SHA-256 and size | Match the supported original |
| Four assembly fragments versus the archived v1.1.0 code | Exact match |
| Full build using newly assembled code | Exact byte-for-byte match with the archived final EXE |
| Full build using the explicit manifest | Exact byte-for-byte match with the archived final EXE |
| File length | 3,661,824 bytes before and after |
| Actually different bytes | 1,085 |
| Declared replacement ranges | 32, nonoverlapping |
| Published automated tests | 20 passed, including the real-original integration test |

Assembled fragments:

| Source | Length |
| --- | ---: |
| `src/cursor_preview.S` | 439 bytes |
| `src/sensitivity.S` | 656 bytes |
| `src/resolution_filter.S` | 134 bytes |
| `src/startup_background.S` | 11 bytes |

The test suite covers incorrect originals, byte guards, tampered patch payloads,
overlap, out-of-bounds ranges, unequal replacement lengths, invalid hex, empty
patches, existing outputs, identical input/output paths, verification-only mode,
partial-write cleanup, symlink protection, manifest hash pinning, assembly
agreement and a reproduction using the actual original executable.

## Re-run

```bash
python3 build.py --check-sources
STAR_WOLVES_ORIGINAL="/path/to/original/StarWolves.exe" python3 -m unittest discover -s tests -v
python3 patch.py "/path/to/original/StarWolves.exe" -o "build/from-manifest.exe"
python3 build.py "/path/to/original/StarWolves.exe" -o "build/from-source.exe"
sha256sum build/from-manifest.exe build/from-source.exe
```

The original game file is deliberately not included. Without it, the real-EXE
integration test is skipped. GNU Binutils is needed for the assembly check.

These results establish reproducibility against the saved final v1.1.0 EXE.
They do not represent a new full-game runtime test, a Windows compatibility
test, or a comprehensive security audit.
