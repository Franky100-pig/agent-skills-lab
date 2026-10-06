#!/usr/bin/env python3
"""Deterministic tests for the prose-rhythm burstiness diagnostic.

Covers empty / one-sentence input, abbreviation handling (Dr., Mr., U.S.A., U.K.),
two-sentence limited-sample band, mixed-text moderate band, and valid JSON output.
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prose_rhythm_measure", ROOT / "scripts" / "measure.py")
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)


class BurstinessTests(unittest.TestCase):
    def test_empty_input(self):
        """Empty text yields a >=2-sentences error and english scope."""
        out = measure.analyze("")
        self.assertEqual(out["sentences"], 0)
        self.assertIn("error", out)
        self.assertIn(">=2 sentences", out["error"])
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_one_sentence(self):
        """A single sentence cannot measure burstiness."""
        out = measure.analyze("Hello world.")
        self.assertEqual(out["sentences"], 1)
        self.assertIn("error", out)

    def test_two_sentence_extreme_limited_sample(self):
        """With exactly two sentences the band is the limited-sample note, not a CV verdict."""
        out = measure.analyze("Go. Stop.")
        self.assertEqual(out["sentences"], 2)
        self.assertIn("limited sample", out["band"])
        self.assertEqual(out["cv"], 0.0)

    def test_mixed_text_moderate(self):
        """Three varied sentences fall in the moderate-variation band (cv ~0.58)."""
        text = "I went to the store. He bought a very large red balloon that floated away. We laughed."
        out = measure.analyze(text)
        self.assertEqual(out["sentences"], 3)
        self.assertEqual(out["band"], "moderate variation")
        self.assertGreaterEqual(out["cv"], 0.45)
        self.assertLessEqual(out["cv"], 1.1)

    def test_abbreviation_counts_as_one_sentence(self):
        """'Dr. Smith wrote.' is one sentence; the period after Dr. must not create a boundary."""
        out = measure.analyze("Dr. Smith wrote.")
        self.assertEqual(out["sentences"], 1)
        self.assertIn("error", out)

    def test_abbreviation_at_sentence_end_preserves_boundary(self):
        """'I live in the U.S.A. Today I leave.' is two sentences; U.S.A. is in ABBREVIATIONS
        but the segment is >3 words, so the boundary after it is kept."""
        out = measure.analyze("I live in the U.S.A. Today I leave.")
        self.assertEqual(out["sentences"], 2)

    def test_uk_acronym_preserves_boundary(self):
        """'The U.K. is vast. Go.' is two sentences; U.K. merges with 'is vast.' but not past it."""
        out = measure.analyze("The U.K. is vast. Go.")
        self.assertEqual(out["sentences"], 2)

    def test_title_abbreviation_merges_long_segment(self):
        """A title abbreviation (Prof.) attaches to the next word even in a longer segment."""
        out = measure.analyze("Prof. Smith wrote.")
        self.assertEqual(out["sentences"], 1)

    def test_mid_sentence_abbreviation_merges(self):
        """A short segment ending in an abbreviation continues the same sentence (e.g. 'He met Mr. Smith.')."""
        out = measure.analyze("He met Mr. Smith. They left.")
        self.assertEqual(out["sentences"], 2)

    def test_cli_emits_valid_json(self):
        """Running the script as a subprocess over stdin yields parseable JSON with the expected keys."""
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "measure.py")],
            input="I went to the store. He bought a very large red balloon that floated away. We laughed.",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["sentences"], 3)
        self.assertIn("cv", data)


if __name__ == "__main__":
    unittest.main()
