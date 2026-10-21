"""Patcher guards and source reproducibility; no copyrighted EXE fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import patch
import build


def digest(data):
    return hashlib.sha256(data).hexdigest()


class PatcherTests(unittest.TestCase):
    def setUp(self):
        self.original = b"0123456789abcdef"
        self.expected = b"01XY456789abZdef"
        self.manifest = {
            "size": len(self.original), "original_sha256": digest(self.original),
            "patched_sha256": digest(self.expected),
            "changes": [
                {"offset": "0x2", "before": "3233", "after": "5859"},
                {"offset": "0xc", "before": "63", "after": "5a"},
            ],
        }

    def test_exact_patch(self):
        self.assertEqual(patch.apply_bytes(self.original, self.manifest), self.expected)

    def test_wrong_original_same_size(self):
        with self.assertRaisesRegex(patch.PatchError, "SHA-256"):
            patch.apply_bytes(b"x" * 16, self.manifest)

    def test_wrong_original_size(self):
        with self.assertRaisesRegex(patch.PatchError, "size"):
            patch.apply_bytes(self.original[:-1], self.manifest)

    def test_before_byte_guard(self):
        self.manifest["changes"][0]["before"] = "ffff"
        with self.assertRaisesRegex(patch.PatchError, "byte guard"):
            patch.apply_bytes(self.original, self.manifest)

    def test_modified_payload_fails_output_hash(self):
        self.manifest["changes"][0]["after"] = "0000"
        with self.assertRaisesRegex(patch.PatchError, "Patched SHA-256"):
            patch.apply_bytes(self.original, self.manifest)

    def test_overlap(self):
        self.manifest["changes"][1]["offset"] = "0x3"
        with self.assertRaisesRegex(patch.PatchError, "overlap"):
            patch.apply_bytes(self.original, self.manifest)

    def test_out_of_bounds(self):
        self.manifest["changes"][1]["offset"] = "0x10"
        with self.assertRaisesRegex(patch.PatchError, "outside"):
            patch.apply_bytes(self.original, self.manifest)

    def test_length_change(self):
        self.manifest["changes"][0]["after"] = "58"
        with self.assertRaisesRegex(patch.PatchError, "equal-length"):
            patch.apply_bytes(self.original, self.manifest)

    def test_bad_hex(self):
        self.manifest["changes"][0]["after"] = "not hex"
        with self.assertRaisesRegex(patch.PatchError, "Invalid"):
            patch.apply_bytes(self.original, self.manifest)

    def test_empty_patch_rejected(self):
        self.manifest["changes"] = []
        with self.assertRaises(patch.PatchError):
            patch.apply_bytes(self.original, self.manifest)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "existing.exe"
            output.write_bytes(b"do not overwrite")
            with self.assertRaises(FileExistsError):
                patch.write_new(output, b"replacement")
            self.assertEqual(output.read_bytes(), b"do not overwrite")

    def test_same_input_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "original.exe"
            source.write_bytes(self.original)
            with mock.patch.object(patch, "load_manifest", return_value=self.manifest):
                self.assertEqual(patch.main([str(source), "-o", str(source)]), 1)
            self.assertEqual(source.read_bytes(), self.original)

    def test_verify_only_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "original.exe", Path(folder) / "out.exe"
            source.write_bytes(self.original)
            with mock.patch.object(patch, "load_manifest", return_value=self.manifest):
                self.assertEqual(patch.main([str(source), "-o", str(output), "--verify-only"]), 0)
            self.assertFalse(output.exists())

    def test_wrong_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "wrong.exe", Path(folder) / "out.exe"
            source.write_bytes(b"x" * 16)
            with mock.patch.object(patch, "load_manifest", return_value=self.manifest):
                self.assertEqual(patch.main([str(source), "-o", str(output)]), 1)
            self.assertFalse(output.exists())

    def test_failure_during_write_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "partial.exe"
            with mock.patch.object(patch.os, "fsync", side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    patch.write_new(output, b"partial")
            self.assertFalse(output.exists())

    def test_output_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            target, output = Path(folder) / "target.exe", Path(folder) / "link.exe"
            target.write_bytes(b"keep")
            try:
                output.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable")
            with self.assertRaises(FileExistsError):
                patch.write_new(output, b"changed")
            self.assertEqual(target.read_bytes(), b"keep")

    def test_release_manifest_hash_is_pinned(self):
        manifest = patch.load_manifest()
        manifest["patched_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(patch.PatchError, "published"):
                patch.load_manifest(path)


class ReleaseSourcesTests(unittest.TestCase):
    def test_release_ranges_are_ordered_and_source_backed(self):
        manifest = patch.load_manifest()
        previous = 0
        for record in manifest["changes"]:
            offset = int(record["offset"], 16)
            before, after = bytes.fromhex(record["before"]), bytes.fromhex(record["after"])
            self.assertGreaterEqual(offset, previous)
            self.assertEqual(len(before), len(after))
            previous = offset + len(before)
            self.assertLessEqual(previous, patch.EXE_SIZE)
        for fragment in manifest["assembly_fragments"]:
            self.assertTrue((patch.ROOT / fragment["source"]).is_file())

    @unittest.skipUnless(all(shutil.which(t) for t in ("as", "ld", "objcopy")), "GNU Binutils required")
    def test_all_assembly_reproduces_the_released_fragments(self):
        self.assertEqual(len(build.assemble_fragments(patch.load_manifest())), 4)

    @unittest.skipUnless(os.environ.get("STAR_WOLVES_ORIGINAL"), "Set STAR_WOLVES_ORIGINAL for the real-EXE integration test")
    def test_real_original_reproduces_release(self):
        original = Path(os.environ["STAR_WOLVES_ORIGINAL"]).read_bytes()
        result = patch.apply_bytes(original, patch.load_manifest())
        self.assertEqual(digest(result), patch.PATCHED_SHA256)
        self.assertEqual(len(result), patch.EXE_SIZE)


if __name__ == "__main__":
    unittest.main()
