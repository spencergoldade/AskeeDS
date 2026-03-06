"""Tests for theme loading and theme-aware rendering."""

from pathlib import Path

import pytest

from askee_ds import Loader, Renderer, Theme

ROOT = Path(__file__).resolve().parent.parent
TOKENS_DIR = ROOT / "tokens"
THEMES_DIR = ROOT / "themes"
COMPONENTS_DIR = ROOT / "components"

THEME_NAMES = ["dark", "light", "high-contrast", "experimental"]


def test_themes_dir_exists():
    assert THEMES_DIR.is_dir(), "themes/ directory should exist"


def test_each_theme_file_exists():
    for name in THEME_NAMES:
        path = THEMES_DIR / f"{name}.yaml"
        assert path.is_file(), f"themes/{name}.yaml should exist"


def test_load_theme_returns_dict(loader):
    for name in THEME_NAMES:
        data = loader.load_theme(name, THEMES_DIR)
        assert isinstance(data, dict), f"load_theme({name!r}) should return a dict"
        assert "color_roles" in data, f"theme {name!r} should define color_roles"


def test_theme_overlay_merges_into_tokens(loader):
    tokens = loader.load_tokens_dir(TOKENS_DIR)
    assert "color_roles" in tokens
    overlay = loader.load_theme("dark", THEMES_DIR)
    merged = {**tokens, **overlay}
    assert "color_roles" in merged
    assert "neutral" in merged["color_roles"]


def test_theme_resolves_roles_for_each_variant(loader):
    tokens_base = loader.load_tokens_dir(TOKENS_DIR)
    for name in THEME_NAMES:
        overlay = loader.load_theme(name, THEMES_DIR)
        merged = {**tokens_base, **overlay}
        theme = Theme(merged)
        assert theme.colors("neutral") is not None
        assert "fg" in theme.colors("neutral")
        assert "bg" in theme.colors("neutral")


def test_render_one_component_per_theme(loader):
    components = loader.load_components_dir(COMPONENTS_DIR)
    comp = components.get("button.text")
    assert comp is not None
    tokens_base = loader.load_tokens_dir(TOKENS_DIR)
    for name in THEME_NAMES:
        overlay = loader.load_theme(name, THEMES_DIR)
        merged = {**tokens_base, **overlay}
        theme = Theme(merged)
        renderer = Renderer(theme)
        output = renderer.render(comp, {"label": "Test"})
        assert isinstance(output, str)
        assert "Test" in output
        assert len(output.strip()) > 0
