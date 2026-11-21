"""Tests for the LUMORA travel poster entry (test-first, per TDD skill).

Run: python3 test_entry.py
Checks: file size, dimensions, PNG validity, main.py stdlib-only,
grader simulation (python3 -P -s, two runs byte-identical), and
image-content probes (title contrast band, golden disc presence).
No OCR is installed on this machine, so legibility of the wordmark is
verified by a contrast probe here PLUS a human visual check of the
rendered poster (see the builder's report).
"""
import ast
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.join(ROOT, "poster.png")
MAIN = os.path.join(ROOT, "main.py")
MAX_BYTES = 1_048_576


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


class TestPosterFile(unittest.TestCase):
    def test_poster_exists_and_within_size_limit(self):
        self.assertTrue(os.path.exists(POSTER), "poster.png missing")
        self.assertLessEqual(
            os.path.getsize(POSTER), MAX_BYTES,
            f"poster.png {os.path.getsize(POSTER)} bytes exceeds {MAX_BYTES}",
        )

    def test_poster_is_valid_png_1024x1024(self):
        from PIL import Image
        with Image.open(POSTER) as im:
            self.assertEqual(im.format, "PNG")
            self.assertEqual(im.size, (1024, 1024))
            im.load()  # proves the file decodes fully

    def test_title_band_has_strong_contrast(self):
        """The wordmark band (top ~12-28% of the image) must contain a
        meaningful share of near-cream pixels (the letters) against the
        darker sky, i.e. the title is actually drawn and legible."""
        from PIL import Image
        with Image.open(POSTER) as im:
            px = im.convert("RGB").load()
            w, h = im.size
            bright = 0
            total = 0
            for y in range(int(h * 0.10), int(h * 0.30)):
                for x in range(0, w, 2):
                    r, g, b = px[x, y]
                    total += 1
                    if r > 225 and g > 215 and b > 180:
                        bright += 1
            frac = bright / total
            self.assertGreater(frac, 0.02, f"title band bright fraction {frac:.3f} too low")
            self.assertLess(frac, 0.45, f"title band bright fraction {frac:.3f} suspiciously high")

    def test_golden_disc_present(self):
        """A strong share of gold pixels must exist in the middle band
        where the half-submerged sun disc sits."""
        from PIL import Image
        with Image.open(POSTER) as im:
            px = im.convert("RGB").load()
            w, h = im.size
            gold = 0
            total = 0
            for y in range(int(h * 0.38), int(h * 0.62)):
                for x in range(int(w * 0.30), int(w * 0.70), 2):
                    r, g, b = px[x, y]
                    total += 1
                    if r > 230 and 170 < g < 230 and b < 170:
                        gold += 1
            frac = gold / total
            self.assertGreater(frac, 0.05, f"gold fraction {frac:.3f} too low — disc missing?")


class TestMainPy(unittest.TestCase):
    def test_main_is_stdlib_only(self):
        with open(MAIN, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        stdlib = sys.stdlib_module_names
        non_stdlib = imported - stdlib
        self.assertEqual(non_stdlib, set(), f"non-stdlib imports: {non_stdlib}")

    def test_grader_simulation_two_runs_byte_identical(self):
        """Simulate the grader: python3 -P -s main.py in a clean dir,
        twice; entry.png must exist, be <=1 MiB, 1024x1024, identical."""
        from PIL import Image
        hashes = []
        for _ in range(2):
            tmp = tempfile.mkdtemp()
            try:
                env = dict(os.environ)
                env["MAKEFUN_OUTPUT_DIR"] = tmp
                proc = subprocess.run(
                    [sys.executable, "-P", "-s", MAIN],
                    cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(proc.returncode, 0, f"main.py failed: {proc.stderr}")
                out = os.path.join(tmp, "entry.png")
                self.assertTrue(os.path.exists(out), "entry.png not created")
                self.assertLessEqual(os.path.getsize(out), MAX_BYTES)
                with Image.open(out) as im:
                    self.assertEqual(im.size, (1024, 1024))
                hashes.append(_sha256(out))
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(hashes[0], hashes[1], "two runs differ — not deterministic")

    def test_env_unset_fallback_writes_beside_main(self):
        """With MAKEFUN_OUTPUT_DIR removed entirely, main.py falls back
        to an output/ directory beside itself (exit 0, bytes match)."""
        tmp = tempfile.mkdtemp()
        try:
            shutil.copy(MAIN, os.path.join(tmp, "main.py"))
            shutil.copy(POSTER, os.path.join(tmp, "poster.png"))
            env = dict(os.environ)
            env.pop("MAKEFUN_OUTPUT_DIR", None)
            proc = subprocess.run(
                [sys.executable, "-P", "-s", os.path.join(tmp, "main.py")],
                cwd=tmp, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(proc.returncode, 0, f"main.py failed: {proc.stderr}")
            out = os.path.join(tmp, "output", "entry.png")
            self.assertTrue(os.path.exists(out), "fallback output/entry.png missing")
            self.assertEqual(_sha256(out), _sha256(POSTER))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_empty_env_value_falls_back(self):
        """MAKEFUN_OUTPUT_DIR='' must fall back, not crash (review I-1)."""
        tmp = tempfile.mkdtemp()
        try:
            env = dict(os.environ)
            env["MAKEFUN_OUTPUT_DIR"] = ""
            proc = subprocess.run(
                [sys.executable, "-P", "-s", MAIN],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(proc.returncode, 0, f"main.py failed: {proc.stderr}")
            out = os.path.join(ROOT, "output", "entry.png")
            self.assertTrue(os.path.exists(out), "fallback output/entry.png missing")
            self.assertEqual(_sha256(out), _sha256(POSTER))
        finally:
            shutil.rmtree(os.path.join(ROOT, "output"), ignore_errors=True)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_missing_poster_fails_cleanly(self):
        """Without poster.png next to main.py, exit nonzero with a clear
        message (no silent wrong output)."""
        tmp = tempfile.mkdtemp()
        try:
            shutil.copy(MAIN, os.path.join(tmp, "main.py"))
            env = dict(os.environ)
            env["MAKEFUN_OUTPUT_DIR"] = tmp
            proc = subprocess.run(
                [sys.executable, "-P", "-s", os.path.join(tmp, "main.py")],
                cwd=tmp, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertNotEqual(proc.returncode, 0, "missing poster must fail")
            self.assertIn("poster.png", proc.stderr + proc.stdout)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
