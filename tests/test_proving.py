"""Proving tests for components being promoted to approved status.

Each test renders a component with realistic props and asserts that
the output contains expected content, has correct structure, and
matches the component's stated purpose.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from askee_ds import Loader, Theme, Renderer

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"
TOKENS_DIR = Path(__file__).resolve().parent.parent / "tokens"


@pytest.fixture(scope="module")
def renderer():
    loader = Loader()
    tokens = loader.load_tokens_dir(TOKENS_DIR)
    return Renderer(Theme(tokens))


@pytest.fixture(scope="module")
def components():
    loader = Loader()
    return loader.load_components_dir(COMPONENTS_DIR)


# ── 5a: Layout primitives ──────────────────────────────────────────


class TestLayoutStack:
    def test_renders_blocks(self, renderer, components):
        output = renderer.render(
            components["layout.stack"],
            {"blocks": ["Status bar content", "Main content\nSecond line"]},
        )
        assert "Status bar content" in output
        assert "Main content" in output
        assert "Second line" in output

    def test_shared_borders(self, renderer, components):
        output = renderer.render(
            components["layout.stack"],
            {"blocks": ["Block A", "Block B"]},
        )
        lines = output.splitlines()
        assert lines[0].startswith("+")
        assert lines[0].endswith("+")
        for line in lines[1:-1]:
            has_border = line.startswith("|") or line.startswith("+")
            assert has_border

    def test_responds_to_available_width(self, renderer, components):
        narrow = renderer.render(
            components["layout.stack"],
            {"blocks": ["A"]},
            available_width=30,
        )
        wide = renderer.render(
            components["layout.stack"],
            {"blocks": ["A"]},
            available_width=60,
        )
        narrow_w = max(len(ln) for ln in narrow.splitlines())
        wide_w = max(len(ln) for ln in wide.splitlines())
        assert wide_w >= narrow_w


class TestLayoutTwoColumn:
    def test_renders_both_panes(self, renderer, components):
        output = renderer.render(
            components["layout.two-column"],
            {"left_content": "Nav item 1\nNav item 2",
             "right_content": "Content area\nMore content",
             "left_width": 15},
        )
        assert "Nav item 1" in output
        assert "Content area" in output

    def test_column_structure(self, renderer, components):
        output = renderer.render(
            components["layout.two-column"],
            {"left_content": "Left",
             "right_content": "Right",
             "left_width": 10},
        )
        lines = output.splitlines()
        assert lines[0].count("+") >= 3


# ── 5b: Exploration components ─────────────────────────────────────


class TestNarrativeLog:
    def test_renders_lines(self, renderer, components):
        output = renderer.render(
            components["narrative-log.pane"],
            {"lines": ["You enter the clearing.",
                        "The guard watches silently."],
             "max_visible": 10},
        )
        assert "Narrative log" in output
        assert "You enter the clearing." in output
        assert "The guard watches silently." in output

    def test_has_border(self, renderer, components):
        output = renderer.render(
            components["narrative-log.pane"],
            {"lines": ["Test line."], "max_visible": 5},
        )
        lines = output.splitlines()
        assert lines[0].startswith("+")
        assert lines[-1].startswith("+")


class TestEntityList:
    def test_renders_items_and_npcs(self, renderer, components):
        output = renderer.render(
            components["entity-list.room"],
            {"items": [{"id": "lamp", "label": "Brass lamp"},
                       {"id": "key", "label": "Rusty key"}],
             "npcs": [{"id": "guard", "label": "Guard"}]},
        )
        assert "Brass lamp" in output
        assert "Rusty key" in output
        assert "Guard" in output


class TestMinimap:
    def test_renders_grid(self, renderer, components):
        output = renderer.render(
            components["minimap.default"],
            {"grid": [[".", ".", "#"],
                      [".", "P", "#"],
                      [".", ".", "."]],
             "legend_entries": [
                 {"char": ".", "label": "empty"},
                 {"char": "#", "label": "wall"},
                 {"char": "P", "label": "you"},
             ],
             "player_position": "1,1"},
        )
        assert "P" in output
        assert "#" in output


# ── 5c: Menu components ───────────────────────────────────────────


class TestMenuMain:
    def test_renders_title_and_items(self, renderer, components):
        output = renderer.render(
            components["menu.main"],
            {"title": "Main Menu",
             "items": [{"id": "new", "label": "New Game"},
                       {"id": "load", "label": "Load Game"},
                       {"id": "quit", "label": "Quit"}]},
        )
        assert "Main Menu" in output
        assert "New Game" in output
        assert "Quit" in output

    def test_has_interaction(self, components):
        comp = components["menu.main"]
        assert comp.interaction.get("focusable") is True
        actions = comp.interaction.get("actions", [])
        action_names = {a["name"] for a in actions}
        assert "select_next" in action_names
        assert "confirm" in action_names


class TestNavVertical:
    def test_renders_items(self, renderer, components):
        output = renderer.render(
            components["nav.vertical"],
            {"items": [{"id": "inv", "label": "Inventory"},
                       {"id": "map", "label": "Map"},
                       {"id": "settings", "label": "Settings"}],
             "active_id": "inv"},
        )
        assert "Inventory" in output
        assert "Map" in output
        assert "Settings" in output


class TestInventoryList:
    def test_renders_items(self, renderer, components):
        output = renderer.render(
            components["inventory.list"],
            {"items": [{"id": "sword", "label": "Rusty sword"},
                       {"id": "lamp", "label": "Brass lamp"},
                       {"id": "key", "label": "Key"}]},
        )
        assert "Inventory" in output
        assert "Rusty sword" in output
        assert "Brass lamp" in output


# ── 5d: Dialogue components ───────────────────────────────────────


class TestSpeechBubble:
    def test_left_tail(self, renderer, components):
        output = renderer.render(
            components["speech-bubble"],
            {"text": "Go north, traveler.", "tail": "left"},
        )
        assert "/" in output
        assert "Go north, traveler." in output

    def test_right_tail(self, renderer, components):
        output = renderer.render(
            components["speech-bubble"],
            {"text": "I will go.", "tail": "right"},
        )
        assert "\\" in output
        assert "I will go." in output

    def test_default_tail_is_left(self, renderer, components):
        output = renderer.render(
            components["speech-bubble"],
            {"text": "Hello."},
        )
        assert "/" in output


class TestHintBar:
    def test_renders_hints_with_prefix(self, renderer, components):
        output = renderer.render(
            components["hint-bar.contextual"],
            {"hints": [{"id": "look", "label": "look"},
                       {"id": "go", "label": "go <dir>"},
                       {"id": "take", "label": "take <item>"}],
             "prefix": "Commands: "},
        )
        assert "Commands: " in output
        assert "look" in output
        assert "go <dir>" in output


# ── 5e: Feedback and typography ────────────────────────────────────


class TestFeedbackSuccess:
    def test_renders_message(self, renderer, components):
        output = renderer.render(
            components["feedback.success"],
            {"message": "Taken: rusty sword (+1 weapon)"},
        )
        assert "Taken: rusty sword (+1 weapon)" in output

    def test_default_color_role(self, components):
        assert components["feedback.success"].default_color_role == "success"


class TestFeedbackError:
    def test_renders_message(self, renderer, components):
        output = renderer.render(
            components["feedback.error"],
            {"message": 'You don\'t see "sword" here.'},
        )
        assert 'You don\'t see "sword" here.' in output

    def test_default_color_role(self, components):
        assert components["feedback.error"].default_color_role == "danger"


class TestTypographyBanner:
    def test_renders_text(self, renderer, components):
        output = renderer.render(
            components["typography.banner"],
            {"text": "QUEST"},
        )
        assert len(output) > 0
        assert output.strip() != ""


# ── 5f: Trackers ──────────────────────────────────────────────────


class TestTrackerObjective:
    def test_renders_objectives(self, renderer, components):
        output = renderer.render(
            components["tracker.objective"],
            {"objectives": [
                {"id": "key", "label": "Find the key", "checked": False},
                {"id": "guard", "label": "Talk to the guard", "checked": True},
                {"id": "door", "label": "Open the door", "checked": False},
            ]},
        )
        assert "Find the key" in output
        assert "Talk to the guard" in output
        assert "Open the door" in output

    def test_has_border(self, renderer, components):
        output = renderer.render(
            components["tracker.objective"],
            {"objectives": [
                {"id": "a", "label": "Task A", "checked": False},
            ]},
        )
        lines = output.splitlines()
        assert lines[0].startswith("+")
        assert lines[-1].startswith("+")
