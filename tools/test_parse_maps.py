"""Tests for AskeeDS ASCII map parser and validator."""

import sys
import unittest
from pathlib import Path

# Allow running from repo root or from tools/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

MAP_TILES_PATH = ROOT / "design" / "ascii" / "map-tiles.yaml"
MAP_INDEX_PATH = ROOT / "design" / "ascii" / "maps" / "index.yaml"


class TestParseMaps(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_map_files_exist(self) -> None:
        self.assertTrue(MAP_TILES_PATH.exists(), "design/ascii/map-tiles.yaml must exist")
        self.assertTrue(MAP_INDEX_PATH.exists(), "design/ascii/maps/index.yaml must exist")

    def test_load_and_validate_maps(self) -> None:
        from parse_maps import load_tilesets, load_map_index, validate_maps

        tilesets = load_tilesets(MAP_TILES_PATH)
        self.assertIn("base_dungeon", tilesets)
        maps = load_map_index(MAP_INDEX_PATH, MAP_INDEX_PATH.parent)
        self.assertGreaterEqual(len(maps), 1)
        errors, warnings, parsed_maps = validate_maps(tilesets, maps)
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
        self.assertIsInstance(parsed_maps, list)
        # The canonical assets should not produce critical validation errors.
        self.assertEqual(
            errors,
            [],
            f"Expected no critical map validation errors, got: {errors}",
        )


if __name__ == "__main__":
    unittest.main()

