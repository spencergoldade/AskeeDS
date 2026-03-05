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

    def test_render_table(self):
        comp = self.components["table.fourcolumn"]
        output = self.renderer.render(comp, {
            "columns": ["Name", "Level"],
            "rows": [["Hero", "5"], ["Mage", "3"]],
        })
        self.assertIn("Name", output)
        self.assertIn("Hero", output)
        self.assertIn("+", output)
        lines = output.strip().split("\n")
        self.assertEqual(len(lines), 6)

    def test_render_bubble_left(self):
        comp = self.components["speech-bubble.left"]
        output = self.renderer.render(comp, {
            "text": "Hello there.",
            "speaker_id": "npc",
        })
        self.assertIn("/", output)
        self.assertIn("Hello there.", output)

    def test_render_bubble_right(self):
        comp = self.components["speech-bubble.right"]
        output = self.renderer.render(comp, {"text": "Goodbye."})
        self.assertIn("\\", output)
        self.assertIn("Goodbye.", output)

    def test_render_tree(self):
        comp = self.components["tree.compact"]
        output = self.renderer.render(comp, {
            "nodes": [
                {"id": "a", "label": "Root", "children": [
                    {"id": "b", "label": "Child", "children": []},
                ]},
            ],
        })
        self.assertIn("Root", output)
        self.assertIn("Child", output)
        self.assertIn("\u2514", output)

    def test_render_grid(self):
        comp = self.components["inventory.grid"]
        output = self.renderer.render(comp, {
            "slots": [
                {"id": "1", "label": "Sword"},
                {"id": "2", "label": "Shield"},
            ],
            "columns": 2,
        })
        self.assertIn("Sword", output)
        self.assertIn("Shield", output)
        self.assertIn("+", output)

    def test_render_charmap(self):
        comp = self.components["minimap.default"]
        output = self.renderer.render(comp, {
            "grid": [list("..#"), list(".P.")],
            "legend_entries": [{"char": ".", "label": "floor"}],
            "player_position": "1,1",
        })
        self.assertIn("P", output)
        self.assertIn(". floor", output)

    def test_render_art_lookup_fallback(self):
        comp = self.components["decoration.placeholder"]
        output = self.renderer.render(comp, {
            "art_id": "nonexistent.thing", "width": 10, "height": 5,
        })
        self.assertTrue(len(output) > 0)

    def test_render_art_lookup_with_catalog(self):
        from askee_ds import Loader, Theme, Renderer
        loader = Loader()
        decos = loader.load_decorations(ROOT / "decorations" / "catalog.yaml")
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        renderer = Renderer(Theme(tokens), decorations=decos)
        comp = self.components["decoration.placeholder"]
        output = renderer.render(comp, {
            "art_id": "decoration.skull.small", "width": 20, "height": 6,
        })
        self.assertIn(".-", output)
        lines = output.splitlines()
        self.assertEqual(len(lines), 6)
        self.assertTrue(all(len(ln) == 20 for ln in lines))

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

    def test_render_stack(self):
        comp = self.components["layout.stack"]
        output = self.renderer.render(comp, {
            "blocks": ["line one", "line two\nline three"],
        })
        self.assertIn("line one", output)
        self.assertIn("line three", output)
        self.assertIn("+", output)

    def test_render_columns(self):
        comp = self.components["layout.two-column"]
        output = self.renderer.render(comp, {
            "left_content": "left\nstuff",
            "right_content": "right\ncontent",
            "left_width": 10,
        })
        self.assertIn("left", output)
        self.assertIn("right", output)
        lines = output.splitlines()
        self.assertTrue(len(lines) >= 3)

    def test_render_shell(self):
        comp = self.components["layout.app.shell"]
        output = self.renderer.render(comp, {
            "header": "My App",
            "sidebar": "Nav 1\nNav 2",
            "content": "Main content\nhere",
            "sidebar_width": 10,
        })
        self.assertIn("My App", output)
        self.assertIn("Nav 1", output)
        self.assertIn("Main content", output)


class TestComposer(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Theme, Renderer, Composer
        loader = Loader()
        self.components = loader.load_components_dir(COMPONENTS_DIR)
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        theme = Theme(tokens)
        renderer = Renderer(theme)
        self.composer = Composer(renderer, self.components)

    def test_compose_stack_with_children(self):
        output = self.composer.compose("layout.stack", {
            "blocks": [
                ("status-bar.default", {
                    "hp_current": 10, "hp_max": 10,
                    "location": "Test", "turn_count": 1,
                }),
                "plain string block",
            ],
        })
        self.assertIn("HP: 10/10", output)
        self.assertIn("plain string block", output)

    def test_compose_columns_with_children(self):
        output = self.composer.compose("layout.two-column", {
            "left_content": ("breadcrumb.inline", {
                "segments": [{"label": "A"}, {"label": "B"}],
            }),
            "right_content": "static text",
            "left_width": 15,
        })
        self.assertIn("A", output)
        self.assertIn("static text", output)

    def test_compose_shell_with_children(self):
        output = self.composer.compose("layout.app.shell", {
            "header": ("header.banner", {"title": "Test App"}),
            "sidebar": "Nav",
            "content": "Content",
            "sidebar_width": 10,
        })
        self.assertIn("Test App", output)
        self.assertIn("Nav", output)
        self.assertIn("Content", output)

    def test_compose_unknown_component_raises(self):
        with self.assertRaises(ValueError):
            self.composer.compose("nonexistent.layout", {})

    def test_compose_unknown_child_raises(self):
        with self.assertRaises(ValueError):
            self.composer.compose("layout.stack", {
                "blocks": [("nonexistent.child", {})],
            })


class TestRichAdapter(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Theme, Renderer
        from askee_ds.adapters.rich import RichAdapter
        loader = Loader()
        self.components = loader.load_components_dir(COMPONENTS_DIR)
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        self.theme = Theme(tokens)
        self.renderer = Renderer(self.theme)
        self.adapter = RichAdapter(self.theme)

    def test_colorize_returns_rich_text(self):
        from rich.text import Text
        output = self.renderer.render(self.components["button.text"], {
            "label": "Click",
        })
        result = self.adapter.colorize(output, "neutral")
        self.assertIsInstance(result, Text)
        self.assertIn("Click", result.plain)

    def test_colorize_with_different_roles(self):
        output = "+---+\n| A |\n+---+"
        for role in ("neutral", "danger", "dungeon", "arcane"):
            result = self.adapter.colorize(output, role)
            self.assertEqual(result.plain, output)

    def test_render_component_shortcut(self):
        from rich.text import Text
        comp = self.components["status-bar.default"]
        result = self.adapter.render_component(self.renderer, comp, {
            "hp_current": 5, "hp_max": 10,
            "location": "Test", "turn_count": 1,
        })
        self.assertIsInstance(result, Text)
        self.assertIn("HP:", result.plain)

    def test_colorize_preserves_all_characters(self):
        original = "+-|\n| x |\n+-+"
        result = self.adapter.colorize(original, "neutral")
        self.assertEqual(result.plain, original)


class TestTextualAdapter(unittest.TestCase):

    def setUp(self):
        from askee_ds import Loader, Theme, Renderer
        loader = Loader()
        self.components = loader.load_components_dir(COMPONENTS_DIR)
        tokens = loader.load_tokens_dir(TOKENS_DIR)
        self.theme = Theme(tokens)
        self.renderer = Renderer(self.theme)

    def test_from_component_creates_widget(self):
        from askee_ds.adapters.textual import AskeeWidget
        widget = AskeeWidget.from_component(
            self.renderer, self.components["status-bar.default"],
            props={"hp_current": 5, "hp_max": 10,
                   "location": "Test", "turn_count": 1},
            theme=self.theme, color_role="neutral",
        )
        self.assertIsInstance(widget, AskeeWidget)

    def test_from_text_creates_widget(self):
        from askee_ds.adapters.textual import AskeeWidget
        widget = AskeeWidget.from_text(
            "+---+\n| A |\n+---+", self.theme, "danger",
        )
        self.assertIsInstance(widget, AskeeWidget)


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
