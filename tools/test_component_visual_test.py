"""Tests for the AskeeDS component visual test helpers and basic flows."""

import asyncio
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Allow running from repo root or from tools/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

try:
    import component_visual_test as cvt
    from parse_components import parse_components, parse_props_meta
except Exception:  # pragma: no cover - import guard
    cvt = None
    parse_components = None
    parse_props_meta = None


@unittest.skipIf(cvt is None, "component_visual_test/Textual not available")
class TestComponentVisualTestHelpers(unittest.TestCase):
    def test_load_components_has_known_names(self) -> None:
        """load_components returns a non-empty list and includes key components."""
        self.assertTrue(
            cvt.COMPONENTS_PATH.exists(), "design/ascii/components.txt must exist"
        )
        components = cvt.load_components()
        self.assertGreater(len(components), 0)
        names = {c["name"] for c in components}
        # A few known components from the library
        self.assertIn("breadcrumb.inline", names)
        self.assertIn("status-bar.default", names)

    def test_approved_component_names_filters_status(self) -> None:
        """approved_component_names only returns names with status=Approved."""
        fake_components = [
            {"name": "a", "meta": {"component-status": "In Review"}},
            {"name": "b", "meta": {"component-status": "Approved"}},
            {"name": "c", "meta": {"component-status": "Cancelled"}},
        ]
        approved = cvt.approved_component_names(fake_components)
        self.assertEqual(approved, ["b"])

    def test_default_props_for_breadcrumb_segments(self) -> None:
        """breadcrumb.inline default props include a segments[] path."""
        content = cvt.COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        bc = next(c for c in components if c["name"] == "breadcrumb.inline")
        props_meta = parse_props_meta(bc.get("meta", {}).get("props", "") or "")
        defaults = cvt.default_props_for_component("breadcrumb.inline", props_meta)
        segments = defaults.get("segments")
        self.assertIsInstance(segments, list)
        self.assertGreaterEqual(len(segments), 3)
        labels = [s.get("label") for s in segments]
        self.assertEqual(labels[0], "Home")
        self.assertEqual(labels[1], "The Clearing")
        self.assertEqual(labels[2], "Guard post")

    def test_randomize_props_for_breadcrumb_segments_shape(self) -> None:
        """Randomized segments for breadcrumb.inline have the expected shape."""
        content = cvt.COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        bc = next(c for c in components if c["name"] == "breadcrumb.inline")
        props_meta = parse_props_meta(bc.get("meta", {}).get("props", "") or "")
        rand_props = cvt.randomize_props_for_component("breadcrumb.inline", props_meta)
        segments = rand_props.get("segments")
        self.assertIsInstance(segments, list)
        self.assertGreaterEqual(len(segments), 2)
        self.assertLessEqual(len(segments), 4)
        # First label should always be Home
        self.assertEqual(segments[0].get("label"), "Home")

    def test_apply_props_to_art_for_breadcrumb_uses_segments_only(self) -> None:
        """apply_props_to_art for breadcrumb.inline renders a single breadcrumb line."""
        content = cvt.COMPONENTS_PATH.read_text(encoding="utf-8")
        components = parse_components(content)
        bc = next(c for c in components if c["name"] == "breadcrumb.inline")
        props_meta = parse_props_meta(bc.get("meta", {}).get("props", "") or "")
        defaults = cvt.default_props_for_component("breadcrumb.inline", props_meta)
        art = bc.get("art", "")
        preview = cvt.apply_props_to_art("breadcrumb.inline", art, defaults)
        # Exact expected line and no generic [ Props: ... ] footer
        self.assertEqual(preview, "Home > The Clearing > Guard post")
        self.assertNotIn("[ Props:", preview)

    def test_apply_props_to_art_for_button_icon(self) -> None:
        """apply_props_to_art for button.icon returns [icon] label with no Props fallback."""
        art = "[☆] Star this"
        defaults = {"icon": "☆", "label": "Star this"}
        preview = cvt.apply_props_to_art("button.icon", art, defaults)
        self.assertEqual(preview, "[☆] Star this")
        self.assertNotIn("[ Props:", preview)
        custom = {"icon": "★", "label": "Other"}
        preview2 = cvt.apply_props_to_art("button.icon", art, custom)
        self.assertEqual(preview2, "[★] Other")

    def test_apply_props_to_art_for_button_text(self) -> None:
        """apply_props_to_art for button.text returns [ label ] with no Props fallback."""
        art = "[ Submit ]"
        preview = cvt.apply_props_to_art("button.text", art, {"label": "Submit"})
        self.assertEqual(preview, "[ Submit ]")
        self.assertNotIn("[ Props:", preview)
        preview2 = cvt.apply_props_to_art("button.text", art, {"label": "Cancel"})
        self.assertEqual(preview2, "[ Cancel ]")

    def test_apply_props_to_art_for_card_simple(self) -> None:
        """apply_props_to_art for card.simple uses title and body_text, no Props fallback."""
        art = "+-- Card title ------------------------+\n| Body text goes here and may wrap     |\n| across multiple lines when needed.   |\n+--------------------------------------+"
        props = {"title": "Card title", "body_text": "Body text goes here and may wrap"}
        preview = cvt.apply_props_to_art("card.simple", art, props)
        self.assertIn("Card title", preview)
        self.assertIn("Body text goes here and may wrap", preview)
        self.assertNotIn("[ Props:", preview)
        props2 = {"title": "Other Title", "body_text": "Short."}
        preview2 = cvt.apply_props_to_art("card.simple", art, props2)
        self.assertIn("Other Title", preview2)
        self.assertIn("Short.", preview2)

    def test_apply_props_to_art_generic_default_as_placeholder(self) -> None:
        """Generic path with parsed_props substitutes default values in art with current props."""
        art = "Prefix Label suffix"
        parsed_props = [{"name": "label", "is_array": False}]
        props = {"label": "Replaced"}
        preview = cvt.apply_props_to_art("generic.fake", art, props, parsed_props)
        self.assertIn("Replaced", preview)
        self.assertNotIn("Label", preview)
        self.assertNotIn("[ Props:", preview)

    def test_append_session_note_writes_expected_line(self) -> None:
        """append_session_note writes a timestamped line into today's notes file."""
        original_notes_dir = cvt.NOTES_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            cvt.NOTES_DIR = tmp_path
            try:
                cvt.append_session_note("room-card.default", "Test note")
                today = datetime.now().strftime("%Y-%m-%d")
                notes_file = tmp_path / f"{today}.md"
                self.assertTrue(notes_file.exists())
                text = notes_file.read_text(encoding="utf-8")
                self.assertIn("Test note", text)
                self.assertIn("[room-card.default]", text)
            finally:
                cvt.NOTES_DIR = original_notes_dir


@unittest.skipIf(cvt is None or not hasattr(cvt.ComponentVisualTestApp, "run_test"), "Textual test harness not available")
class TestComponentVisualTestStartup(unittest.IsolatedAsyncioTestCase):
    async def test_startup_browse_all_does_not_crash(self) -> None:
        """Selecting the first startup option should not crash the app."""
        async with cvt.ComponentVisualTestApp().run_test() as pilot:
            # Ensure startup screen is mounted, then press Enter to choose first option.
            await pilot.pause()
            await pilot.press("enter")
            # Let events process; if there is an unhandled exception, the test will fail.
            await pilot.pause()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

