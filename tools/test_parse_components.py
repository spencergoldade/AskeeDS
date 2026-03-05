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
        self.assertEqual(
            parser_names,
            manifest_names,
            (
                f"Parser and manifest mismatch: parser has {parser_names - manifest_names!r} extra; "
                f"manifest has {manifest_names - parser_names!r} extra"
            ),
        )

    def test_component_status_present_after_migration(self):
        from parse_components import parse_components, COMPONENT_STATUSES
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        for c in components:
            status = c.get("meta", {}).get("component-status", "").strip()
            self.assertIn(status, COMPONENT_STATUSES, f"{c['name']}: component-status {status!r} not in allowed set")

    def test_validate_invalid_component_status(self):
        from parse_components import validate
        components = [{"name": "test.fake", "meta": {"component-status": "Unknown", "description": "x", "props": "y"}, "art": ""}]
        errors, _ = validate(components)
        self.assertTrue(any("invalid component-status" in e for e in errors), f"Expected invalid status error, got: {errors}")

    def test_validate_deprecated_without_replaced_by(self):
        from parse_components import validate
        components = [{"name": "test.deprecated", "meta": {"component-status": "Deprecated", "description": "x", "props": "y"}, "art": ""}]
        errors, _ = validate(components)
        self.assertTrue(any("replaced-by" in e for e in errors), f"Expected replaced-by error, got: {errors}")

    def test_validate_deprecated_with_replaced_by(self):
        from parse_components import validate
        components = [{"name": "test.deprecated", "meta": {"component-status": "Deprecated", "replaced-by": "some.component", "description": "x", "props": "y"}, "art": ""}]
        errors, _ = validate(components)
        status_errors = [e for e in errors if "component-status" in e or "replaced-by" in e]
        self.assertEqual(len(status_errors), 0, f"Unexpected status/replaced-by errors: {status_errors}")

    def test_json_export_includes_component_status(self):
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        self.assertGreater(len(components), 0)
        with_status = [c for c in components if c.get("meta", {}).get("component-status")]
        self.assertGreater(len(with_status), 0, "At least one component should have component-status in meta")
        self.assertEqual(with_status[0]["meta"].get("component-status"), "In Review")

    def test_reference_art_button_text(self):
        """Parser extracts correct reference art for button.text (no meta or next-component lines)."""
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        by_name = {c["name"]: c for c in components}
        self.assertIn("button.text", by_name, "button.text must be in library")
        art = by_name["button.text"]["art"]
        self.assertEqual(art.strip(), "[ Submit ]", f"button.text art should be '[ Submit ]', got: {art!r}")

    def test_reference_art_character_sheet_compact(self):
        """Parser extracts correct reference art for character-sheet.compact (no meta or next-component lines)."""
        from parse_components import parse_components
        content = COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        by_name = {c["name"]: c for c in components}
        self.assertIn("character-sheet.compact", by_name, "character-sheet.compact must be in library")
        art = by_name["character-sheet.compact"]["art"]
        art_stripped = art.strip()
        self.assertIn("Hero", art_stripped, "character-sheet.compact art should contain 'Hero'")
        self.assertIn("HP:", art_stripped, "character-sheet.compact art should contain 'HP:'")
        self.assertIn("85/100", art_stripped, "character-sheet.compact art should contain '85/100'")
        self.assertIn("Mana:", art_stripped, "character-sheet.compact art should contain 'Mana:'")
        self.assertIn("20/50", art_stripped, "character-sheet.compact art should contain '20/50'")
        self.assertNotIn("COMPONENT:", art_stripped, "Art must not include next component header")


if __name__ == "__main__":
    unittest.main()
