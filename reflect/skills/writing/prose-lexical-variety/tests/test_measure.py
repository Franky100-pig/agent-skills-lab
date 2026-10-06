#!/usr/bin/env python3
"""Deterministic tests for the prose-lexical-variety perplexity-proxy diagnostic.

Covers empty input, single-token insufficient sample, low/moderate/high variety bands,
and valid JSON output from the CLI.
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prose_variety_measure", ROOT / "scripts" / "measure.py")
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)


class LexicalVarietyTests(unittest.TestCase):
    def test_empty_input(self):
        """Empty text yields an empty-text error and english scope."""
        out = measure.analyze("")
        self.assertIn("error", out)
        self.assertEqual(out["language_scope"], "english-prose-only")

    def test_single_token_insufficient(self):
        """A single token cannot measure variety; it returns the insufficient-sample band."""
        out = measure.analyze("Word.")
        self.assertEqual(out["tokens"], 1)
        self.assertIn("insufficient sample", out["band"])

    def test_low_variety(self):
        """Repeated common words read as over-smooth (low variety)."""
        out = measure.analyze("the the the the the the the the the the")
        self.assertEqual(out["ttr"], 0.1)
        self.assertEqual(out["band"], "low lexical variety - may read as over-smooth")

    def test_high_variety(self):
        """Many distinct rare words read as high variety."""
        out = measure.analyze("quartz fjord xylem blip obfuscate walnut zephyr kestrel vellum glib")
        self.assertGreater(out["ttr"], 0.8)
        self.assertEqual(out["band"], "high lexical variety - watch readability")

    def test_moderate_variety(self):
        """A natural mix of common and rare words lands in the moderate band.

        'the cat sat near the mat and the dog ran to the park' -> 13 tokens, rare_ratio
        ~0.46 (>=0.45), ttr ~0.77 (in 0.35..0.8) -> moderate.
        """
        out = measure.analyze("the cat sat near the mat and the dog ran to the park")
        self.assertEqual(out["band"], "moderate lexical variety")
        self.assertGreaterEqual(out["ttr"], 0.35)
        self.assertLessEqual(out["ttr"], 0.8)

    def test_cli_emits_valid_json(self):
        """Running the script as a subprocess over stdin yields parseable JSON with expected keys."""
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "measure.py")],
            input="the cat sat near the mat and the dog ran to the park",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["tokens"], 13)
        self.assertIn("ttr", data)


if __name__ == "__main__":
    unittest.main()
