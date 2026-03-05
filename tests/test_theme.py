"""Tests for the AskeeDS Theme."""


def test_color_roles_available(theme):
    roles = theme.color_roles
    assert "neutral" in roles
    assert "danger" in roles
    assert "arcane" in roles
    assert len(roles) >= 10


def test_color_resolution(theme):
    palette = theme.colors("danger")
    assert "bg" in palette
    assert "fg" in palette
    assert "border" in palette
    assert "accent" in palette


def test_color_fallback_to_neutral(theme):
    palette = theme.colors("nonexistent_role")
    neutral = theme.colors("neutral")
    assert palette == neutral


def test_border_styles(theme):
    styles = theme.border_styles
    assert "single" in styles
    assert "heavy" in styles
    assert "double" in styles


def test_border_resolution(theme):
    bd = theme.border("single")
    for key in ("h", "v", "tl", "tr", "bl", "br"):
        assert key in bd


def test_bar_chars(theme):
    filled, empty = theme.bar_chars()
    assert isinstance(filled, str)
    assert isinstance(empty, str)
    assert len(filled) == 1
    assert len(empty) == 1
