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
