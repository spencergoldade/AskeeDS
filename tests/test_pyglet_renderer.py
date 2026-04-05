"""Tests for the Pyglet rendering pathway."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from askee_ds.loader import Component

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent


def _make_pyglet_mock() -> MagicMock:
    """Return a MagicMock that stands in for the pyglet package."""
    mock = MagicMock()
    mock.text = MagicMock()
    mock.text.Label = MagicMock()
    mock.shapes = MagicMock()
    mock.shapes.Rectangle = MagicMock()
    mock.clock = MagicMock()
    mock.clock.schedule_interval = MagicMock()
    mock.clock.unschedule = MagicMock()
    mock.graphics = MagicMock()
    mock.graphics.Batch = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# font_size round-trip through Loader
# ---------------------------------------------------------------------------


def test_component_font_size_default():
    """Component.font_size defaults to 'medium' when not specified in YAML."""
    from askee_ds import Loader

    loader = Loader()
    yaml_src = """
test-component.plain:
  category: game/
  description: Test component.
  status: ideated
  render:
    type: inline
    template: "hello"
"""
    components = loader.load_components(yaml_src)
    assert components["test-component.plain"].font_size == "medium"


def test_component_font_size_explicit():
    """Component.font_size is parsed correctly when specified in YAML."""
    from askee_ds import Loader

    loader = Loader()
    yaml_src = """
test-component.large:
  category: game/
  description: Test component.
  status: ideated
  font_size: large
  render:
    type: inline
    template: "hello"
"""
    components = loader.load_components(yaml_src)
    assert components["test-component.large"].font_size == "large"


# ---------------------------------------------------------------------------
# render_pyglet dispatcher
# ---------------------------------------------------------------------------


def test_font_sizes_all_positive_integers():
    """FONT_SIZES maps all four tokens to positive ints."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)
        for token in ("large", "medium", "small", "micro"):
            assert isinstance(pr.FONT_SIZES[token], int)
            assert pr.FONT_SIZES[token] > 0


def test_render_pyglet_returns_none():
    """render_pyglet() must return None (it accumulates into batch, not a string)."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)
        from askee_ds import Loader

        loader = Loader()
        components = loader.load_components("""
unknown-component.x:
  category: game/
  description: Unknown.
  status: ideated
  render:
    type: inline
    template: "x"
""")
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()
        result = pr.render_pyglet(components["unknown-component.x"], {}, theme, viewport, batch)
        assert result is None


def test_render_pyglet_unknown_component_calls_fallback(monkeypatch):
    """Unknown component name dispatches to _draw_fallback."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        called = []
        pr.register("test-sentinel.x", lambda *a, **kw: called.append("registered"))

        from askee_ds import Loader

        loader = Loader()
        components = loader.load_components("""
not-registered.y:
  category: game/
  description: Not registered.
  status: ideated
  render:
    type: inline
    template: "y"
""")
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()
        pr.render_pyglet(components["not-registered.y"], {}, theme, viewport, batch)
        assert called == [], "fallback should NOT call the registered sentinel"
        # Also verify _draw_fallback actually ran (drew something)
        assert pyglet_mock.text.Label.call_count >= 1


def test_render_pyglet_known_component_calls_registered_fn():
    """Known component name dispatches to the registered draw function."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        calls = []

        def _my_draw(component, props, theme_state, viewport, batch, pane_id):
            calls.append((component.name, pane_id))

        pr.register("my-pane.default", _my_draw)

        from askee_ds import Loader

        loader = Loader()
        components = loader.load_components("""
my-pane.default:
  category: game/
  description: Test pane.
  status: ideated
  render:
    type: inline
    template: "x"
""")
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock()
        batch = MagicMock()
        pr.render_pyglet(
            components["my-pane.default"], {}, theme, viewport, batch, pane_id="test-pane"
        )
        assert calls == [("my-pane.default", "test-pane")]


# ---------------------------------------------------------------------------
# Public API export
# ---------------------------------------------------------------------------


def test_render_pyglet_importable_from_package():
    """render_pyglet is importable from the top-level askee_ds package.

    pyglet_renderer.py only imports pyglet lazily inside draw functions,
    so the top-level package import works without Pyglet installed.
    """
    from askee_ds import render_pyglet  # noqa: F401

    assert callable(render_pyglet)


# ---------------------------------------------------------------------------
# history-pane.default
# ---------------------------------------------------------------------------


def _load_component(name: str) -> Component:
    from pathlib import Path

    from askee_ds import Loader

    loader = Loader()
    components_dir = Path(__file__).resolve().parent.parent / "components"
    return loader.load_components_dir(components_dir)[name]


def test_history_pane_component_loads():
    """history-pane.default YAML loads with correct props and font_size."""
    comp = _load_component("history-pane.default")
    assert comp.font_size == "large"
    assert "lines" in comp.props
    assert "max_lines" in comp.props


def test_history_pane_renders_visible_lines():
    """_draw_history_pane creates one Label per visible line."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("history-pane.default")
        props = {"lines": ["line one", "line two", "line three"], "max_lines": 2}
        viewport = MagicMock(x=0, y=500, width=800, height=500)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="history")

        # Only max_lines=2 most recent lines should be drawn
        assert pyglet_mock.text.Label.call_count == 2
        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("line two" in c for c in calls)
        assert any("line three" in c for c in calls)
        assert all("line one" not in c for c in calls)


def test_history_pane_draws_background_rectangle():
    """_draw_history_pane draws a background Rectangle for the palette colour."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("history-pane.default")
        props = {"lines": ["a"], "max_lines": 10}
        viewport = MagicMock(x=0, y=0, width=800, height=500)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="history")

        assert pyglet_mock.shapes.Rectangle.call_count >= 1


# ---------------------------------------------------------------------------
# input-pane.default
# ---------------------------------------------------------------------------


def test_input_pane_component_loads():
    """input-pane.default YAML loads with correct props and font_size."""
    comp = _load_component("input-pane.default")
    assert comp.font_size == "large"
    assert "value" in comp.props
    assert "placeholder" in comp.props


def test_input_pane_renders_value():
    """_draw_input_pane renders '> {value}' text."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("input-pane.default")
        props = {"value": "look around", "placeholder": ""}
        viewport = MagicMock(x=0, y=0, width=800, height=60)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="input")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("look around" in c for c in calls)


def test_input_pane_renders_placeholder_when_empty():
    """_draw_input_pane renders placeholder when value is empty."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("input-pane.default")
        props = {"value": "", "placeholder": "What do you do?"}
        viewport = MagicMock(x=0, y=0, width=800, height=60)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="input-ph")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        # Must include the "> " prompt prefix per spec ("> {placeholder}")
        assert any("> What do you do?" in c for c in calls)


def test_input_pane_schedules_cursor_blink_once():
    """Cursor blink interval is scheduled exactly once per pane_id."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("input-pane.default")
        props = {"value": "hello", "placeholder": ""}
        viewport = MagicMock(x=0, y=0, width=800, height=60)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        # Call render twice with the same pane_id
        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="input-once")
        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="input-once")

        # schedule_interval must be called exactly once (not once per frame)
        assert pyglet_mock.clock.schedule_interval.call_count == 1


# ---------------------------------------------------------------------------
# character-pane.default
# ---------------------------------------------------------------------------


def test_character_pane_component_loads():
    """character-pane.default YAML loads with correct props and font_size."""
    comp = _load_component("character-pane.default")
    assert comp.font_size == "micro"
    assert "portrait_lines" in comp.props
    assert "portrait_id" in comp.props


def test_character_pane_renders_portrait_lines():
    """_draw_character_pane creates one Label per portrait line."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("character-pane.default")
        portrait = [" o ", "/|\\", "/ \\"]
        props = {"portrait_lines": portrait, "portrait_id": "hero"}
        viewport = MagicMock(x=520, y=300, width=280, height=300)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="char")

        assert pyglet_mock.text.Label.call_count == len(portrait)


def test_character_pane_vignette_draws_four_rectangles():
    """_draw_character_pane draws 4 edge Rectangles when vignette=True.

    No background Rectangle is drawn by this pane — exactly 4 calls for vignette strips.
    """
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("character-pane.default")
        props = {"portrait_lines": [" o "], "portrait_id": "hero"}
        viewport = MagicMock(x=520, y=300, width=280, height=300)
        theme = MagicMock(palette="neutral", tint="", vignette=True)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="char-v")

        assert pyglet_mock.shapes.Rectangle.call_count == 4


# ---------------------------------------------------------------------------
# stats-pane.default
# ---------------------------------------------------------------------------


def test_stats_pane_component_loads():
    """stats-pane.default YAML loads with correct props and font_size."""
    comp = _load_component("stats-pane.default")
    assert comp.font_size == "small"
    assert "stats" in comp.props


def test_stats_pane_renders_all_stat_entries():
    """_draw_stats_pane creates Labels for each stat entry."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("stats-pane.default")
        props = {
            "stats": [
                {"label": "HP", "value": "85/100"},
                {"label": "MP", "value": "40/40"},
            ],
            "enemy_stats": None,
        }
        viewport = MagicMock(x=520, y=0, width=280, height=300)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="stats")

        # At minimum one Label per stat entry (label + value can be one or two calls)
        assert pyglet_mock.text.Label.call_count >= 2


def test_stats_pane_no_enemy_stats_when_none():
    """When enemy_stats is None, only stat-row Labels are rendered (no divider/enemy block)."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("stats-pane.default")
        stats = [{"label": "HP", "value": "10"}, {"label": "MP", "value": "5"}]
        props = {"stats": stats, "enemy_stats": None}
        viewport = MagicMock(x=0, y=0, width=200, height=200)
        theme = MagicMock(palette="dark", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="stats")

        # 2 stats × 2 Labels (label + value) = 4 Labels exactly
        assert pyglet_mock.text.Label.call_count == 4


# ---------------------------------------------------------------------------
# location-header.default
# ---------------------------------------------------------------------------


def test_location_header_component_loads():
    """location-header.default YAML loads with correct props and font_size."""
    comp = _load_component("location-header.default")
    assert comp.font_size == "medium"
    assert "location_name" in comp.props


def test_location_header_renders_location_name():
    """_draw_location_header creates a Label containing the location name."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("location-header.default")
        props = {"location_name": "The Dark Forest"}
        viewport = MagicMock(x=0, y=550, width=520, height=50)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="loc-header")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("The Dark Forest" in c for c in calls)


# ---------------------------------------------------------------------------
# character-pane.default — tint
# ---------------------------------------------------------------------------


def test_character_pane_tint_applies_to_labels():
    """Hex tint is parsed and passed as color to Labels."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("character-pane.default")
        props = {"portrait_lines": ["line1", "line2"], "portrait_id": "hero"}
        theme = MagicMock(palette="dark", tint="#ff8800", vignette=False)
        viewport = MagicMock(x=0, y=0, width=200, height=300)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="char")

        # Each Label call should have color=(255, 136, 0, 255)
        for call in pyglet_mock.text.Label.call_args_list:
            assert call.kwargs.get("color") == (0xFF, 0x88, 0x00, 255)


# ---------------------------------------------------------------------------
# input-pane.default — cursor toggle
# ---------------------------------------------------------------------------


def test_input_pane_cursor_toggle_alternates():
    """The cursor toggle callback flips _CURSOR_STATE for the pane."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("input-pane.default")
        props = {"value": "hello", "placeholder": ""}
        theme = MagicMock(palette="dark", tint="", vignette=False)
        viewport = MagicMock(x=0, y=0, width=400, height=60)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="inp")

        # Retrieve the toggle callback that was passed to schedule_interval
        schedule_call = pyglet_mock.clock.schedule_interval.call_args
        toggle_fn = schedule_call.args[0]
        initial = pr._CURSOR_STATE.get("inp", True)
        toggle_fn(0)  # simulate clock tick
        assert pr._CURSOR_STATE["inp"] == (not initial)
        toggle_fn(0)  # simulate second tick
        assert pr._CURSOR_STATE["inp"] == initial


# ---------------------------------------------------------------------------
# menu.main
# ---------------------------------------------------------------------------


def test_menu_main_component_loads():
    """menu.main YAML loads with correct props."""
    comp = _load_component("menu.main")
    assert "title" in comp.props
    assert "items" in comp.props


def test_menu_main_draws_items():
    """_draw_menu_main creates at least 3 Labels: title + 2 items."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("menu.main")
        props = {
            "title": "AskeeDS",
            "items": [
                {"id": "new_game", "label": "New Game"},
                {"id": "quit", "label": "Quit"},
            ],
            "selected_index": 0,
        }
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="menu")

        # At minimum: 1 title label + 2 item labels
        assert pyglet_mock.text.Label.call_count >= 3
        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("AskeeDS" in c for c in calls)
        assert any("New Game" in c for c in calls)
        assert any("Quit" in c for c in calls)


def test_menu_main_selected_item_is_white():
    """Selected menu item is rendered in white; non-selected items are grey."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("menu.main")
        props = {
            "title": "Menu",
            "items": [
                {"id": "a", "label": "Alpha"},
                {"id": "b", "label": "Beta"},
            ],
            "selected_index": 1,
        }
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="menu2")

        # Collect all Label calls that carry a color kwarg
        item_calls = [c for c in pyglet_mock.text.Label.call_args_list if "color" in c.kwargs]
        colors = {str(c.args[0]): c.kwargs["color"] for c in item_calls if c.args}
        # "Beta" is selected (index 1) — white
        assert colors.get("> Beta") == (255, 255, 255, 255)
        # "Alpha" is not selected — grey
        assert colors.get("Alpha")[0] < 200  # some shade of grey


# ---------------------------------------------------------------------------
# typography.banner
# ---------------------------------------------------------------------------


def test_typography_banner_component_loads():
    """typography.banner YAML loads with correct props."""
    comp = _load_component("typography.banner")
    assert "text" in comp.props


def test_typography_banner_draws_text():
    """_draw_typography_banner draws at least one Label containing the banner text."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("typography.banner")
        props = {"text": "ASKEE"}
        viewport = MagicMock(x=0, y=0, width=800, height=200)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch)

        assert pyglet_mock.text.Label.call_count >= 1
        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("ASKEE" in c for c in calls)


def test_typography_banner_draws_multiline():
    """Each newline-separated line in text is drawn as a separate Label."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("typography.banner")
        props = {"text": "line1\nline2\nline3"}
        viewport = MagicMock(x=0, y=0, width=800, height=200)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch)

        assert pyglet_mock.text.Label.call_count == 3


# ---------------------------------------------------------------------------
# modal.overlay
# ---------------------------------------------------------------------------


def test_modal_overlay_component_loads():
    """modal.overlay YAML loads with correct props."""
    comp = _load_component("modal.overlay")
    assert "title" in comp.props


def test_modal_overlay_draws_title():
    """_draw_modal_overlay draws at least one Label containing the title."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("modal.overlay")
        props = {
            "title": "Confirm Quit",
            "body": "Are you sure?",
            "actions": [{"label": "Yes"}, {"label": "No"}],
        }
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="modal")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("Confirm Quit" in c for c in calls)


def test_modal_overlay_draws_dimmed_background():
    """_draw_modal_overlay draws at least 2 Rectangles: dim overlay + modal box."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("modal.overlay")
        props = {
            "title": "Alert",
            "body": "Something happened.",
            "actions": [],
        }
        viewport = MagicMock(x=0, y=0, width=800, height=600)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="modal2")

        assert pyglet_mock.shapes.Rectangle.call_count >= 2


# ---------------------------------------------------------------------------
# _hp_bar_color helper
# ---------------------------------------------------------------------------


def test_hp_bar_color_green_above_50_percent():
    """_hp_bar_color returns green (high green channel) when HP > 50%."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        color = pr._hp_bar_color(80, 100)
        # Green channel must be dominant over red channel
        assert color[1] > color[0]


def test_hp_bar_color_red_below_25_percent():
    """_hp_bar_color returns red (high red channel) when HP < 25%."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        color = pr._hp_bar_color(10, 100)
        # Red channel must be dominant over green channel
        assert color[0] > color[1]


# ---------------------------------------------------------------------------
# combat-card.enemy
# ---------------------------------------------------------------------------


def test_combat_card_enemy_renders_name_and_hp():
    """_draw_combat_card_enemy draws Labels containing enemy name and HP fraction."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("combat-card.enemy")
        props = {"enemy_name": "Forest Wolf", "enemy_hp": 45, "enemy_hp_max": 80}
        viewport = MagicMock(x=0, y=0, width=400, height=300)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="enemy-card")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("Forest Wolf" in c for c in calls)
        assert any("Flesh" in c for c in calls)
        assert any("45/80" in c for c in calls)


# ---------------------------------------------------------------------------
# combat-card.actions
# ---------------------------------------------------------------------------


def test_combat_card_actions_renders_hp_and_round():
    """_draw_combat_card_actions draws Labels containing player HP and round number."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules,
        {
            "pyglet": pyglet_mock,
            "pyglet.text": pyglet_mock.text,
            "pyglet.shapes": pyglet_mock.shapes,
            "pyglet.clock": pyglet_mock.clock,
            "pyglet.graphics": pyglet_mock.graphics,
        },
    ):
        from importlib import reload

        import askee_ds.pyglet_renderer as pr

        reload(pr)

        comp = _load_component("combat-card.actions")
        props = {"player_hp": 70, "player_hp_max": 100, "round": 3}
        viewport = MagicMock(x=0, y=0, width=400, height=300)
        theme = MagicMock(palette="neutral", tint="", vignette=False)
        batch = MagicMock()

        pr.render_pyglet(comp, props, theme, viewport, batch, pane_id="actions-card")

        calls = [str(c) for c in pyglet_mock.text.Label.call_args_list]
        assert any("Flesh" in c for c in calls)
        assert any("70/100" in c for c in calls)
        assert any("Round 3" in c for c in calls)
