"""Tests for the AskeeDS framework: Loader, Renderer, Theme, Validator."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
TOKENS_DIR = ROOT / "tokens"
SCHEMA_PATH = COMPONENTS_DIR / "_schema.yaml"


class TestLoader(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader
        self.loader = Loader()

    def test_load_components_dir(self):
        components = self.loader.load_components_dir(COMPONENTS_DIR)
        self.assertIsInstance(components, dict)
        self.assertEqual(len(components), 63)

    def test_load_tokens_dir(self):
        tokens = self.loader.load_tokens_dir(TOKENS_DIR)
        self.assertIn("color_roles", tokens)
        self.assertIn("sets", tokens)
        self.assertIn("bar", tokens)
        self.assertIn("conventions", tokens)

    def test_component_fields(self):
        components = self.loader.load_components_dir(COMPONENTS_DIR)
        comp = components["button.icon"]
        self.assertEqual(comp.name, "button.icon")
        self.assertEqual(comp.category, "core/buttons")
        self.assertEqual(comp.status, "approved")
        self.assertIn("label", comp.props)
        self.assertIn("icon", comp.props)
        self.assertEqual(comp.props["label"].type, "string")
        self.assertTrue(comp.props["label"].required)

    def test_load_components_from_string(self):
        yaml_str = """
test.comp:
  category: core/test
  description: A test component.
  status: ideated
  render:
    type: inline
    template: "hello {name}"
  props:
    name:
      type: string
      required: true
"""
        components = self.loader.load_components(yaml_str)
        self.assertIn("test.comp", components)
        self.assertEqual(components["test.comp"].description, "A test component.")

    def test_load_components_skips_schema(self):
        components = self.loader.load_components_dir(COMPONENTS_DIR)
        for name in components:
            self.assertFalse(name.startswith("_"), f"Loaded schema file as component: {name}")

    def test_loader_with_schema_validation(self):
        from askee_ds import Loader
        loader = Loader(schema_path=SCHEMA_PATH)
        components = loader.load_components_dir(COMPONENTS_DIR)
        self.assertEqual(len(components), 63)


class TestTheme(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Theme
        loader = Loader()
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        self.theme = Theme(tokens)

    def test_color_roles_available(self):
        roles = self.theme.color_roles
        self.assertIn("neutral", roles)
        self.assertIn("danger", roles)
        self.assertIn("arcane", roles)
        self.assertGreaterEqual(len(roles), 10)

    def test_color_resolution(self):
        palette = self.theme.colors("danger")
        self.assertIn("bg", palette)
        self.assertIn("fg", palette)
        self.assertIn("border", palette)
        self.assertIn("accent", palette)

    def test_color_fallback_to_neutral(self):
        palette = self.theme.colors("nonexistent_role")
        neutral = self.theme.colors("neutral")
        self.assertEqual(palette, neutral)

    def test_border_styles(self):
        styles = self.theme.border_styles
        self.assertIn("single", styles)
        self.assertIn("heavy", styles)
        self.assertIn("double", styles)

    def test_border_resolution(self):
        bd = self.theme.border("single")
        for key in ("h", "v", "tl", "tr", "bl", "br"):
            self.assertIn(key, bd)

    def test_bar_chars(self):
        filled, empty = self.theme.bar_chars()
        self.assertIsInstance(filled, str)
        self.assertIsInstance(empty, str)
        self.assertEqual(len(filled), 1)
        self.assertEqual(len(empty), 1)


class TestRenderer(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Theme, Renderer
        loader = Loader()
        self.components = loader.load_components_dir(COMPONENTS_DIR)
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        theme = Theme(tokens)
        self.renderer = Renderer(theme)

    def test_render_inline(self):
        comp = self.components["button.icon"]
        output = self.renderer.render(comp, {"icon": "☆", "label": "Star"})
        self.assertIn("☆", output)
        self.assertIn("Star", output)

    def test_render_join(self):
        comp = self.components["breadcrumb.inline"]
        output = self.renderer.render(comp, {
            "segments": [{"label": "Home"}, {"label": "Room"}]
        })
        self.assertIn("Home", output)
        self.assertIn("Room", output)

    def test_render_box(self):
        comp = self.components["status-bar.default"]
        output = self.renderer.render(comp, {
            "hp_current": 85, "hp_max": 100,
            "location": "The Clearing", "turn_count": 12,
        })
        self.assertIn("85", output)
        self.assertIn("The Clearing", output)
        lines = output.strip().split("\n")
        self.assertGreaterEqual(len(lines), 3)

    def test_render_box_with_list_section(self):
        comp = self.components["room-card.default"]
        output = self.renderer.render(comp, {
            "title": "Cavern",
            "description_text": "A dark cavern.",
            "items": [{"label": "torch"}],
            "npcs": [],
            "exits": [{"id": "n", "label": "north"}],
        })
        self.assertIn("Cavern", output)
        self.assertIn("torch", output)
        self.assertIn("north", output)

    def test_render_reference_returns_art(self):
        comp = self.components["layout.app.shell"]
        output = self.renderer.render(comp, {})
        self.assertTrue(len(output) > 0)

    def test_render_all_non_reference_components(self):
        """Every component with a render spec should render without exceptions."""
        errors = []
        for name, comp in sorted(self.components.items()):
            rtype = comp.render.get("type", "reference")
            if rtype == "reference":
                continue
            try:
                self.renderer.render(comp, {})
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        self.assertEqual(errors, [], f"Render failures:\n" + "\n".join(errors))

    def test_render_checked_list(self):
        comp = self.components["tracker.objective"]
        output = self.renderer.render(comp, {
            "objectives": [
                {"label": "Find key", "checked": True},
                {"label": "Open door", "checked": False},
            ]
        })
        self.assertIn("[x]", output)
        self.assertIn("[ ]", output)
        self.assertIn("Find key", output)

    def test_render_active_list(self):
        comp = self.components["nav.vertical"]
        output = self.renderer.render(comp, {
            "items": [
                {"id": "inv", "label": "Inventory"},
                {"id": "map", "label": "Map"},
                {"id": "settings", "label": "Settings"},
            ],
            "active_id": "settings",
        })
        self.assertIn("> Settings", output)
        self.assertNotIn("> Inventory", output)
        self.assertIn("Inventory", output)

    def test_render_clock(self):
        comp = self.components["tracker.clock"]
        output = self.renderer.render(comp, {
            "label": "Quest",
            "segments": 4,
            "filled": 2,
        })
        self.assertIn("Quest", output)
        self.assertIn("●●○○", output)
        self.assertIn("2 / 4", output)

    def test_render_stage_track(self):
        comp = self.components["tracker.front"]
        output = self.renderer.render(comp, {
            "label": "Invasion",
            "stages": [
                {"id": "safe", "label": "Safe"},
                {"id": "war", "label": "War"},
            ],
            "current_stage_index": 0,
        })
        self.assertIn("Invasion:", output)
        self.assertIn("[ Safe ]", output)
        self.assertIn("[ War ]", output)
        self.assertIn("^", output)

    def test_render_banner_fallback(self):
        comp = self.components["typography.banner"]
        output = self.renderer.render(comp, {"text": "TEST"})
        self.assertTrue(len(output) > 0)

    def test_render_frames(self):
        comp = self.components["spinner.loading"]
        output = self.renderer.render(comp, {
            "frames": ["|", "/", "-", "\\"],
        })
        self.assertEqual(output, "|")

    def test_render_frames_empty(self):
        comp = self.components["spinner.loading"]
        output = self.renderer.render(comp, {"frames": []})
        self.assertEqual(output, "")

    def test_render_bars(self):
        comp = self.components["character-sheet.compact"]
        output = self.renderer.render(comp, {
            "name": "Hero",
            "stats": [
                {"label": "HP", "current": 8, "max": 10},
                {"label": "MP", "current": 3, "max": 5},
            ],
        })
        self.assertIn("Hero", output)


class TestValidator(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Validator
        self.loader = Loader()
        self.validator = Validator.from_schema_file(SCHEMA_PATH)

    def test_validate_all_components(self):
        components = self.loader.load_components_dir(COMPONENTS_DIR)
        errors = self.validator.validate_all(components)
        self.assertEqual(errors, [], f"Validation errors:\n" + "\n".join(
            f"  {n}: {m}" for n, m in errors
        ))

    def test_validate_catches_bad_status(self):
        from askee_ds.loader import Component
        bad = Component(
            name="test.bad", category="core/test",
            description="Bad", status="nonexistent",
            props={}, render={"type": "inline", "template": "hi"},
        )
        errors = self.validator.validate(bad)
        statuses = [msg for _, msg in errors if "status" in msg]
        self.assertGreaterEqual(len(statuses), 1)

    def test_validate_catches_bad_category(self):
        from askee_ds.loader import Component
        bad = Component(
            name="test.bad", category="invalid/prefix",
            description="Bad", status="ideated",
            props={}, render={"type": "inline", "template": "hi"},
        )
        errors = self.validator.validate(bad)
        cats = [msg for _, msg in errors if "category" in msg]
        self.assertGreaterEqual(len(cats), 1)

    def test_validate_catches_bad_render_type(self):
        from askee_ds.loader import Component
        bad = Component(
            name="test.bad", category="core/test",
            description="Bad", status="ideated",
            props={}, render={"type": "nonexistent"},
        )
        errors = self.validator.validate(bad)
        renders = [msg for _, msg in errors if "render type" in msg]
        self.assertGreaterEqual(len(renders), 1)

    def test_validate_catches_bad_section_type(self):
        from askee_ds.loader import Component
        bad = Component(
            name="test.bad", category="core/test",
            description="Bad", status="ideated",
            props={}, render={
                "type": "box", "width": 40, "border": "single",
                "sections": [{"type": "nonexistent"}],
            },
        )
        errors = self.validator.validate(bad)
        sects = [msg for _, msg in errors if "section" in msg]
        self.assertGreaterEqual(len(sects), 1)


if __name__ == "__main__":
    unittest.main()
