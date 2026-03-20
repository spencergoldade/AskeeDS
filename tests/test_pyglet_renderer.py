"""Tests for the Pyglet rendering pathway."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock
from pathlib import Path


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
        sys.modules, {"pyglet": pyglet_mock, "pyglet.text": pyglet_mock.text,
                      "pyglet.shapes": pyglet_mock.shapes,
                      "pyglet.clock": pyglet_mock.clock,
                      "pyglet.graphics": pyglet_mock.graphics}
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
        sys.modules, {"pyglet": pyglet_mock, "pyglet.text": pyglet_mock.text,
                      "pyglet.shapes": pyglet_mock.shapes,
                      "pyglet.clock": pyglet_mock.clock,
                      "pyglet.graphics": pyglet_mock.graphics}
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
        result = pr.render_pyglet(
            components["unknown-component.x"], {}, theme, viewport, batch
        )
        assert result is None


def test_render_pyglet_unknown_component_calls_fallback(monkeypatch):
    """Unknown component name dispatches to _draw_fallback."""
    pyglet_mock = _make_pyglet_mock()
    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, {"pyglet": pyglet_mock, "pyglet.text": pyglet_mock.text,
                      "pyglet.shapes": pyglet_mock.shapes,
                      "pyglet.clock": pyglet_mock.clock,
                      "pyglet.graphics": pyglet_mock.graphics}
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
        sys.modules, {"pyglet": pyglet_mock, "pyglet.text": pyglet_mock.text,
                      "pyglet.shapes": pyglet_mock.shapes,
                      "pyglet.clock": pyglet_mock.clock,
                      "pyglet.graphics": pyglet_mock.graphics}
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
            components["my-pane.default"], {}, theme, viewport, batch,
            pane_id="test-pane"
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


def _load_component(name: str) -> "Component":
    from askee_ds import Loader
    from pathlib import Path

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
