"""Tests for AskeeDS decorative ASCII art catalog parser and validator."""

import sys
import unittest
from pathlib import Path

# Allow running from repo root or from tools/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

DECORATION_PATH = ROOT / "design" / "ascii" / "decoration-catalog.txt"


class TestParseDecorations(unittest.TestCase):
    def test_catalog_file_exists(self) -> None:
        self.assertTrue(
            DECORATION_PATH.exists(), "design/ascii/decoration-catalog.txt must exist"
        )

    def test_parse_decorations_basic(self) -> None:
        from parse_decorations import parse_decorations

        content = DECORATION_PATH.read_text(encoding="utf-8")
        decorations = parse_decorations(content)
        self.assertGreaterEqual(
            len(decorations), 1, "Expected at least one decoration in catalog"
        )
        for d in decorations:
            self.assertIn("id", d)
            self.assertTrue(d["id"])
            self.assertIn("meta", d)
            self.assertIsInstance(d["meta"], dict)
            self.assertIn("art", d)
            self.assertIsInstance(d["art"], str)

    def test_validate_decorations_returns_lists(self) -> None:
        from parse_decorations import parse_decorations, validate_decorations

        content = DECORATION_PATH.read_text(encoding="utf-8")
        decorations = parse_decorations(content)
        errors, warnings = validate_decorations(decorations)
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)


if __name__ == "__main__":
    unittest.main()

