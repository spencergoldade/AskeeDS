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


class TestColumnsLines:
    def test_returns_tuples_with_roles(self):
        spec = {"border": "single", "width": 40}
        props = {"left_content": "Left", "right_content": "Right"}
        result = _columns_lines(spec, props, FULL_THEME, available_width=80)
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_border_and_body_roles(self):
        spec = {"border": "single", "width": 40}
        props = {"left_content": "L", "right_content": "R"}
        result = _columns_lines(spec, props, FULL_THEME, available_width=80)
        roles = [r for _, r in result]
        assert roles[0] == "border"   # top
        assert roles[-1] == "border"  # bottom
        assert all(r == "body" for r in roles[1:-1])

    def test_uses_tj_down_and_tj_up(self):
        spec = {"border": "single", "width": 40}
        props = {"left_content": "L", "right_content": "R"}
        result = _columns_lines(spec, props, FULL_THEME, available_width=80)
        top_text = result[0][0]
        bot_text = result[-1][0]
        assert "┬" in top_text   # tj_down
        assert "┴" in bot_text   # tj_up


class TestShellLines:
    def test_returns_tuples_with_roles(self):
        spec = {"border": "single", "width": 50}
        props = {"header": "Title", "sidebar": "Nav", "content": "Main"}
        result = _shell_lines(spec, props, FULL_THEME, available_width=80)
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_header_role_present(self):
        spec = {"border": "single", "width": 50}
        props = {"header": "Title", "sidebar": "Nav", "content": "Main"}
        result = _shell_lines(spec, props, FULL_THEME, available_width=80)
        roles = [r for _, r in result]
        assert "header" in roles

    def test_divider_between_header_and_body(self):
        spec = {"border": "single", "width": 50}
        props = {"header": "Title", "sidebar": "Nav", "content": "Main"}
        result = _shell_lines(spec, props, FULL_THEME, available_width=80)
        roles = [r for _, r in result]
        # border, header, divider, body..., border
        assert roles[0] == "border"
        assert roles[1] == "header"
        assert roles[2] == "divider"
        assert roles[-1] == "border"

    def test_empty_props_no_crash(self):
        spec = {"border": "single", "width": 50}
        result = _shell_lines(spec, {}, FULL_THEME, available_width=80)
        assert len(result) > 0  # at least borders + header + divider


class TestJoinLayout:
    def test_join_produces_single_styled_line(self):
        comp = _make_component(render={
            "type": "join",
            "over": "exits",
            "separator": " | ",
            "template": "{label}",
        })
        props = {"exits": [{"label": "North"}, {"label": "South"}]}
        lines = layout(comp, props, THEME)
        assert len(lines) == 1
        assert lines[0].role == "body"
        assert "North" in lines[0].text
        assert "South" in lines[0].text
        assert " | " in lines[0].text

    def test_join_with_prefix(self):
        comp = _make_component(render={
            "type": "join",
            "over": "items",
            "separator": ", ",
            "template": "{name}",
            "prefix": "Exits: ",
        })
        props = {"items": [{"name": "A"}, {"name": "B"}]}
        lines = layout(comp, props, THEME)
        assert lines[0].text.startswith("Exits: ")

    def test_join_empty_list(self):
        comp = _make_component(render={
            "type": "join",
            "over": "items",
            "separator": ", ",
            "template": "{label}",
        })
        lines = layout(comp, {}, THEME)
        assert len(lines) == 1
        assert lines[0].text == ""


class TestStackLayout:
    def test_stack_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "stack",
            "border": "single",
            "width": 20,
            "prop": "blocks",
        })
        props = {"blocks": ["Hello", "World"]}
        lines = layout(comp, props, FULL_THEME)
        assert all(isinstance(ln, StyledLine) for ln in lines)
        assert lines[0].role == "border"
        assert lines[-1].role == "border"
        body = [ln for ln in lines if ln.role == "body"]
        assert len(body) == 2

    def test_stack_empty_blocks_returns_empty(self):
        comp = _make_component(render={
            "type": "stack",
            "border": "single",
            "width": 20,
            "prop": "blocks",
        })
        lines = layout(comp, {"blocks": []}, FULL_THEME)
        assert lines == []


class TestColumnsLayout:
    def test_columns_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "columns",
            "border": "single",
            "width": 40,
        })
        props = {"left_content": "Left", "right_content": "Right"}
        lines = layout(comp, props, FULL_THEME)
        assert all(isinstance(ln, StyledLine) for ln in lines)
        assert lines[0].role == "border"
        assert lines[-1].role == "border"


class TestShellLayout:
    def test_shell_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "shell",
            "border": "single",
            "width": 50,
        })
        props = {"header": "Title", "sidebar": "Nav", "content": "Main"}
        lines = layout(comp, props, FULL_THEME)
        assert all(isinstance(ln, StyledLine) for ln in lines)
        headers = [ln for ln in lines if ln.role == "header"]
        assert len(headers) >= 1
        assert "Title" in headers[0].text


class TestTableLayout:
    def test_table_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "table",
            "columns_prop": "columns",
            "rows_prop": "rows",
        })
        props = {
            "columns": ["Name", "Value"],
            "rows": [["Sword", "100"], ["Shield", "50"]],
        }
        lines = layout(comp, props, THEME)
        assert len(lines) > 0
        assert all(isinstance(ln, StyledLine) for ln in lines)
        borders = [ln for ln in lines if ln.role == "border"]
        assert len(borders) >= 3  # top, header-sep, bottom
        headers = [ln for ln in lines if ln.role == "header"]
        assert len(headers) == 1
        assert "Name" in headers[0].text

    def test_table_empty_columns(self):
        comp = _make_component(render={"type": "table"})
        lines = layout(comp, {}, THEME)
        assert lines == []


class TestTreeLayout:
    def test_tree_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "tree",
            "prop": "nodes",
            "template": "{label}",
        })
        props = {"nodes": [
            {"label": "Root", "children": [
                {"label": "Child A"},
                {"label": "Child B"},
            ]},
        ]}
        lines = layout(comp, props, THEME)
        assert len(lines) == 3
        assert all(isinstance(ln, StyledLine) for ln in lines)
        assert all(ln.role == "body" for ln in lines)
        assert "Root" in lines[0].text
        assert "Child A" in lines[1].text

    def test_tree_empty_nodes(self):
        comp = _make_component(render={"type": "tree", "prop": "nodes"})
        lines = layout(comp, {}, THEME)
        assert lines == []


class TestGridLayout:
    def test_grid_produces_styled_lines(self):
        comp = _make_component(render={
            "type": "grid",
            "prop": "slots",
            "columns_prop": "cols",
            "cell_width": 8,
        })
        props = {
            "slots": [{"label": "A"}, {"label": "B"}, {"label": "C"}],
            "cols": 3,
        }
        lines = layout(comp, props, THEME)
        assert len(lines) > 0
        assert all(isinstance(ln, StyledLine) for ln in lines)
        borders = [ln for ln in lines if ln.role == "border"]
        assert len(borders) >= 2

    def test_grid_empty_slots(self):
        comp = _make_component(render={"type": "grid", "prop": "slots"})
        lines = layout(comp, {}, THEME)
        assert lines == []
