#!/usr/bin/env python3
"""Assemble all four patch fragments, verify their bytes, and rebuild v1.1.0.

Requires Python 3.9+ and GNU Binutils (as, ld, objcopy). No game is executed.
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import patch


def assemble_fragments(manifest):
    for tool in ("as", "ld", "objcopy"):
        if shutil.which(tool) is None:
            raise patch.PatchError(f"GNU Binutils tool not found: {tool}")
    assembled = {}
    records = {record["id"]: record for record in manifest["changes"]}
    with tempfile.TemporaryDirectory(prefix="star-wolves-source-") as directory:
        directory = Path(directory)
        for fragment in manifest["assembly_fragments"]:
            name = fragment["id"]
            source = patch.ROOT / fragment["source"]
            obj, elf, binary = [directory / (name + ext) for ext in (".o", ".elf", ".bin")]
            subprocess.run(["as", "--32", str(source), "-o", str(obj)], check=True)
            subprocess.run(["ld", "-m", "elf_i386", "-Ttext=" + fragment["virtual_address"],
                            "--entry=" + fragment["entry"], str(obj), "-o", str(elf)], check=True)
            subprocess.run(["objcopy", "-O", "binary", "-j", ".text", str(elf), str(binary)], check=True)
            data = binary.read_bytes()
            expected = bytes.fromhex(records[name]["after"])
            if data != expected:
                raise patch.PatchError(f"Assembly does not reproduce the released bytes: {source.name}")
            assembled[name] = data
            print(f"Verified assembly: {fragment['source']} ({len(data)} bytes)")
    return assembled


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, nargs="?", help="Supported original StarWolves.exe")
    parser.add_argument("-o", "--output", type=Path, default=patch.ROOT / "build" / "StarWolves.exe")
    parser.add_argument("--check-sources", action="store_true", help="Verify assembly without needing a game EXE")
    args = parser.parse_args(argv)
    if not args.check_sources and args.original is None:
        parser.error("provide an original EXE, or use --check-sources")
    try:
        manifest = patch.load_manifest()
        fragments = assemble_fragments(manifest)
        if not args.check_sources:
            # Use freshly assembled bytes for every code fragment; the manifest
            # supplies reviewed hook instructions, constants and PE metadata.
            for record in manifest["changes"]:
                if record["id"] in fragments:
                    record["after"] = fragments[record["id"]].hex()
            result = patch.apply_bytes(args.original.read_bytes(), manifest)
            patch.write_new(args.output, result)
            print(f"Created: {args.output}")
            print(f"Verified v1.1.0 SHA-256: {patch.sha256(result)}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
