"""Tests for AskeeDS component library parser and validator."""
import json
import sys
import unittest
from pathlib import Path

# Allow running from repo root or from tools/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
COMPONENTS_PATH = ROOT / "design" / "ascii" / "components.txt"


class TestParseComponents(unittest.TestCase):
    def test_components_file_exists(self):
        self.assertTrue(COMPONENTS_PATH.exists(), "design/ascii/components.txt must exist")

    def test_parse_components(self):
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        self.assertGreaterEqual(len(components), 47, "Expected at least 47 components from library")
        names = [c["name"] for c in components]
        self.assertIn("layout.app.shell", names)
        self.assertIn("room-card.default", names)
        self.assertIn("status-bar.default", names)
        self.assertIn("decoration.placeholder", names)

    def test_component_has_meta_and_art(self):
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        for c in components:
            self.assertIn("name", c)
            self.assertTrue(c["name"])
            self.assertIn("meta", c)
            self.assertIsInstance(c["meta"], dict)
            self.assertIn("art", c)
            self.assertIsInstance(c["art"], str)

    def test_no_delimiter_in_art(self):
        from parse_components import parse_components, DELIMITER
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        for c in components:
            self.assertNotIn(DELIMITER, c["art"], f"{c['name']}: ASCII art must not contain delimiter U+241F")

    def test_validate_returns_errors_and_warnings(self):
        from parse_components import parse_components, validate
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        errors, warnings = validate(components)
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
        self.assertEqual(len(errors), 0, f"Expected no critical errors: {errors}")

    def test_json_export_roundtrip(self):
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        out = {"components": [{"name": c["name"], "meta": c["meta"], "art": c["art"]} for c in components]}
        json_str = json.dumps(out, indent=2)
        loaded = json.loads(json_str)
        self.assertEqual(len(loaded["components"]), len(components))
        self.assertEqual(loaded["components"][0]["name"], components[0]["name"])

    def test_manifest_matches_parser(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        manifest_path = ROOT / "design" / "ascii" / "manifest.yaml"
        if not manifest_path.exists():
            self.skipTest("manifest.yaml not found")
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest_names = set(manifest.get("components", []))
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        parser_names = {c["name"] for c in components}
        self.assertEqual(parser_names, manifest_names, (
            f"Parser and manifest mismatch: parser has {parser_names - manifest_names!r} extra; "
            f"manifest has {manifest_names - parser_names!r} extra"
        ))


if __name__ == "__main__":
    unittest.main()
