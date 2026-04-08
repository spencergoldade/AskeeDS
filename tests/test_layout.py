"""Tests for the LayoutEngine — spec interpreter producing StyledLines."""

from __future__ import annotations

import pytest

from askee_ds.layout import StyledLine, layout
from askee_ds.loader import Component, PropDef
from askee_ds.render_types.layout import _stack_lines, _columns_lines, _shell_lines
from askee_ds.theme import Theme


def _make_theme() -> Theme:
    return Theme({
        "color_roles": {
            "neutral": {"bg": "#000", "fg": "#fff"},
        },
        "sets": {
            "single": {
                "h": "─",
                "v": "│",
                "tl": "┌",
                "tr": "┐",
                "bl": "└",
                "br": "┘",
                "tj_right": "├",
                "tj_left": "┤",
            },
        },
        "bar": {"filled": "█", "empty": "░"},
    })


def _make_component(
    name: str = "test.default",
    render: dict | None = None,
) -> Component:
    return Component(
        name=name,
        category="test",
        description="test component",
        status="stable",
        props={},
        render=render or {},
    )


def _make_full_theme() -> Theme:
    """Theme with all border keys including tj_down/tj_up for layout types."""
    return Theme({
        "color_roles": {
            "neutral": {"bg": "#000", "fg": "#fff"},
        },
        "sets": {
            "single": {
                "h": "─", "v": "│",
                "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
                "tj_right": "├", "tj_left": "┤",
                "tj_down": "┬", "tj_up": "┴", "cross": "┼",
            },
        },
        "bar": {"filled": "█", "empty": "░"},
    })


THEME = _make_theme()
FULL_THEME = _make_full_theme()


class TestStyledLine:
    def test_dataclass_fields(self):
        line = StyledLine(text="hello", role="header", indent=2)
        assert line.text == "hello"
        assert line.role == "header"
        assert line.indent == 2

    def test_default_indent(self):
        line = StyledLine(text="hello", role="body")
        assert line.indent == 0


class TestBoxLayout:
    def test_header_and_list_sections(self):
        comp = _make_component(render={
            "type": "box",
            "border": "single",
            "width": 30,
            "sections": [
                {"type": "header", "text": "{title}"},
                {"type": "divider"},
                {
                    "type": "list",
                    "over": "items",
                    "template": "  {label}",
                },
            ],
        })
        props = {
            "title": "My Box",
            "items": [
                {"label": "Apple"},
                {"label": "Banana"},
            ],
        }
        lines = layout(comp, props, THEME)

        assert isinstance(lines, list)
        assert all(isinstance(ln, StyledLine) for ln in lines)

        # First and last lines are borders
        assert lines[0].role == "border"
        assert lines[-1].role == "border"

        # Header line
        header_lines = [ln for ln in lines if ln.role == "header"]
        assert len(header_lines) == 1
        assert "My Box" in header_lines[0].text

        # Divider
        divider_lines = [ln for ln in lines if ln.role == "divider"]
        assert len(divider_lines) == 1

        # Body lines (list items)
        body_lines = [ln for ln in lines if ln.role == "body"]
        assert len(body_lines) == 2
        assert "Apple" in body_lines[0].text
        assert "Banana" in body_lines[1].text

    def test_box_uses_border_characters(self):
        comp = _make_component(render={
            "type": "box",
            "border": "single",
            "width": 20,
            "sections": [],
        })
        lines = layout(comp, {}, THEME)
        # Top and bottom borders only
        assert len(lines) == 2
        assert "┌" in lines[0].text
        assert "┐" in lines[0].text
        assert "└" in lines[1].text
        assert "┘" in lines[1].text


class TestInlineLayout:
    def test_simple_template(self):
        comp = _make_component(render={
            "type": "inline",
            "template": "Hello, {name}!",
        })
        lines = layout(comp, {"name": "World"}, THEME)
        assert len(lines) == 1
        assert lines[0].text == "Hello, World!"
        assert lines[0].role == "body"

    def test_inline_no_template(self):
        comp = _make_component(render={"type": "inline"})
        lines = layout(comp, {}, THEME)
        assert len(lines) == 1
        assert lines[0].text == ""


class TestWidthClamping:
    def test_max_width_clamps(self):
        comp = _make_component(render={
            "type": "box",
            "border": "single",
            "width": "fill",
            "max_width": 20,
            "sections": [
                {"type": "header", "text": "Title"},
            ],
        })
        lines = layout(comp, {}, THEME, available_width=100)
        # All lines should be <= 20 chars
        for ln in lines:
            assert len(ln.text) <= 20

    def test_min_width_expands(self):
        comp = _make_component(render={
            "type": "box",
            "border": "single",
            "width": "content",
            "min_width": 30,
            "sections": [
                {"type": "header", "text": "Hi"},
            ],
        })
        lines = layout(comp, {}, THEME, available_width=10)
        # Border lines should be at least 30 chars
        assert len(lines[0].text) >= 30


class TestEdgeCases:
    def test_unknown_render_type_returns_empty(self):
        comp = _make_component(render={"type": "unknown_type_xyz"})
        lines = layout(comp, {}, THEME)
        assert lines == []

    def test_no_render_spec_returns_empty(self):
        comp = _make_component(render={})
        lines = layout(comp, {}, THEME)
        # Empty spec defaults to inline with empty template
        assert len(lines) == 1


class TestStackLines:
    def test_returns_tuples_with_roles(self):
        spec = {"border": "single", "width": 20, "prop": "blocks"}
        props = {"blocks": ["Hello", "World"]}
        result = _stack_lines(spec, props, FULL_THEME, available_width=80)
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_border_and_body_roles(self):
        spec = {"border": "single", "width": 20, "prop": "blocks"}
        props = {"blocks": ["Line A"]}
        result = _stack_lines(spec, props, FULL_THEME, available_width=80)
        roles = [r for _, r in result]
        assert roles[0] == "border"   # top
        assert roles[1] == "body"     # content
        assert roles[-1] == "border"  # bottom

    def test_divider_between_blocks(self):
        spec = {"border": "single", "width": 20, "prop": "blocks"}
        props = {"blocks": ["A", "B"]}
        result = _stack_lines(spec, props, FULL_THEME, available_width=80)
        roles = [r for _, r in result]
        # top, body-A, divider, body-B, bottom
        assert roles == ["border", "body", "divider", "body", "border"]

    def test_empty_blocks_returns_empty(self):
        spec = {"border": "single", "width": 20, "prop": "blocks"}
        props = {"blocks": []}
        result = _stack_lines(spec, props, FULL_THEME, available_width=80)
        assert result == []
