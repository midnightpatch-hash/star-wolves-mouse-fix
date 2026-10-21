#!/usr/bin/env python3
"""Reproduce Star Wolves v1.1.0 from the exact supported original EXE.

Python 3.9+; standard library only. Never executes or overwrites a game EXE.
The manifest contains literal, reviewable before/after bytes, not executable
Python, compressed payloads or downloads.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "patches" / "v1.1.0.json"
ORIGINAL_SHA256 = "5942489ba04d2ab6cce996b21f5e1ea806e439f8d36ec10e7d8b7c8749a44804"
PATCHED_SHA256 = "4b2ceb680fcc6fdf58f5e4bdfec16f4f11eda00511d2c254e7ddef624d5d3d33"
EXE_SIZE = 3661824


class PatchError(ValueError):
    """An input or patch validation failed; no output should be installed."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_manifest(path=MANIFEST):
    with Path(path).open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict) or manifest.get("format") != 1:
        raise PatchError("Unsupported manifest format.")
    if manifest.get("original_sha256") != ORIGINAL_SHA256:
        raise PatchError("Manifest does not describe the supported original EXE.")
    if manifest.get("patched_sha256") != PATCHED_SHA256:
        raise PatchError("Manifest does not describe the published v1.1.0 EXE.")
    if manifest.get("size") != EXE_SIZE:
        raise PatchError("Unexpected executable size in manifest.")
    return manifest


def apply_bytes(original, manifest):
    """Validate every range before producing an independently checked result."""
    if len(original) != manifest["size"]:
        raise PatchError("Original size mismatch.")
    if sha256(original) != manifest["original_sha256"]:
        raise PatchError("Original SHA-256 mismatch. Use the unmodified supported Steam EXE.")
    changes = manifest.get("changes")
    if not isinstance(changes, list) or not changes:
        raise PatchError("Manifest has no patch records.")
    decoded = []
    previous_end = 0
    for record in changes:
        try:
            offset = int(record["offset"], 16)
            before = bytes.fromhex(record["before"])
            after = bytes.fromhex(record["after"])
        except (KeyError, TypeError, ValueError) as error:
            raise PatchError("Invalid patch record.") from error
        if not before or len(before) != len(after):
            raise PatchError("Patch records must be nonempty, equal-length replacements.")
        end = offset + len(before)
        if offset < previous_end or offset < 0 or end > len(original):
            raise PatchError("Patch ranges overlap, are unsorted, or are outside the EXE.")
        if original[offset:end] != before:
            raise PatchError(f"Original byte guard failed at {offset:#x}.")
        decoded.append((offset, end, after))
        previous_end = end
    result = bytearray(original)
    for offset, end, after in decoded:
        result[offset:end] = after
    result = bytes(result)
    if sha256(result) != manifest["patched_sha256"]:
        raise PatchError("Patched SHA-256 mismatch. No output was written.")
    return result


def write_new(path, data):
    """Exclusive creation protects existing outputs, symlinks and the input."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # 'xb' fails if any file or symlink already occupies this name.
    with path.open("xb") as handle:
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            handle.close()
            path.unlink()
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Unmodified StarWolves.exe or original backup")
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "build" / "StarWolves.exe")
    parser.add_argument("--verify-only", action="store_true", help="Validate input and the complete patch without writing")
    args = parser.parse_args(argv)
    try:
        original = args.original.read_bytes()
        result = apply_bytes(original, load_manifest())
        if not args.verify_only:
            write_new(args.output, result)
            print(f"Created: {args.output}")
        print(f"Verified v1.1.0 SHA-256: {sha256(result)}")
        print("The input file was not modified. The game was not launched.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
