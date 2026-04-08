"""LayoutEngine — spec interpreter producing StyledLines.

Takes a Component + props + Theme, reads the component's ``render`` spec,
and produces ``list[StyledLine]``. Each StyledLine carries its text content
and a semantic role so downstream renderers (Pyglet, Rich, etc.) can apply
colours without re-parsing the layout.

Supports ``type: box`` (bordered panels with typed sections) and
``type: inline`` (single-line template interpolation). Width resolution
uses the component's width/min_width/max_width constraints.

    from askee_ds.layout import StyledLine, layout

    lines = layout(component, props, theme, available_width=80)
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass

from .loader import Component
from .render_types._helpers import interpolate
from .render_types.bubble import _bubble_lines
from .render_types.charmap import _charmap_lines
from .render_types.layout import _stack_lines, _columns_lines, _shell_lines
from .render_types.structured import _table_lines, _grid_lines
from .render_types.tree import _tree_walk
from .sizing import DEFAULT_WIDTH, resolve_width
from .theme import Theme


@dataclass
class StyledLine:
    """A single line of layout output with semantic role annotation."""

    text: str
    role: str  # header, body, border, divider, muted
    indent: int = 0


def layout(
    component: Component,
    props: dict,
    theme: Theme,
    available_width: int = DEFAULT_WIDTH,
) -> list[StyledLine]:
    """Interpret a component's render spec and produce styled lines.

    Returns an empty list for unrecognised render types.
    """
    spec = component.render
    rtype = spec.get("type", "inline")

    if rtype == "box":
        return _layout_box(spec, props, theme, available_width)
    if rtype == "inline":
        return _layout_inline(spec, props, available_width)
    if rtype == "join":
        return _layout_join(spec, props)
    if rtype == "stack":
        return _tuples_to_styled(
            _stack_lines(spec, props, theme, available_width),
        )
    if rtype == "columns":
        return _tuples_to_styled(
            _columns_lines(spec, props, theme, available_width),
        )
    if rtype == "shell":
        return _tuples_to_styled(
            _shell_lines(spec, props, theme, available_width),
        )
    if rtype == "table":
        return _tuples_to_styled(_table_lines(spec, props, available_width))
    if rtype == "tree":
        return _layout_tree(spec, props)
    if rtype == "grid":
        return _tuples_to_styled(_grid_lines(spec, props, available_width))
    if rtype == "bubble":
        return _tuples_to_styled(_bubble_lines(spec, props))
    if rtype == "charmap":
        return _tuples_to_styled(_charmap_lines(spec, props, theme))
    if rtype == "banner":
        return _layout_banner(spec, props, component, available_width)
    if rtype == "clock":
        return _layout_clock(spec, props)
    if rtype == "stage_track":
        return _layout_stage_track(spec, props)
    if rtype == "frames":
        return _layout_frames(spec, props)
    if rtype == "art_lookup":
        return _layout_art_lookup(spec, props, component)

    return []


# -- box layout --------------------------------------------------------------


def _layout_box(
    spec: dict,
    props: dict,
    theme: Theme,
    available_width: int,
) -> list[StyledLine]:
    width = resolve_width(spec, available_width)
    bd = theme.border(spec.get("border", "single"))
    inner = width - 2
    lines: list[StyledLine] = []

    # Top border
    lines.append(StyledLine(
        text=bd["tl"] + bd["h"] * inner + bd["tr"],
        role="border",
    ))

    for section in spec.get("sections", []):
        lines.extend(_section(section, props, inner, bd, theme))

    # Bottom border
    lines.append(StyledLine(
        text=bd["bl"] + bd["h"] * inner + bd["br"],
        role="border",
    ))

    return lines


def _row_text(text: str, inner: int, bd: dict) -> str:
    """Produce a bordered row string: │text        │"""
    return bd["v"] + text.ljust(inner)[:inner] + bd["v"]


def _section(
    section: dict,
    props: dict,
    inner: int,
    bd: dict,
    theme: Theme,
) -> list[StyledLine]:
    stype = section.get("type", "text")
    lines: list[StyledLine] = []

    if stype == "header":
        text = interpolate(section["text"], props)
        lines.append(StyledLine(
            text=_row_text(f" {text}", inner, bd),
            role="header",
        ))

    elif stype == "divider":
        lines.append(StyledLine(
            text=bd["tj_right"] + bd["h"] * inner + bd["tj_left"],
            role="divider",
        ))

    elif stype == "text":
        text = interpolate(section["text"], props)
        lines.append(StyledLine(
            text=_row_text(text, inner, bd),
            role="body",
        ))

    elif stype == "wrap":
        raw = interpolate(section["text"], props)
        indent = section.get("indent", 0)
        prefix = " " * indent
        wrapped = textwrap.wrap(
            raw, width=inner - indent * 2, break_long_words=False,
        )
        for wline in wrapped or [""]:
            lines.append(StyledLine(
                text=_row_text(f"{prefix}{wline}", inner, bd),
                role="body",
                indent=indent,
            ))

    elif stype == "blank":
        lines.append(StyledLine(
            text=_row_text("", inner, bd),
            role="body",
        ))

    elif stype == "list":
        items = props.get(section.get("over", ""), [])
        if not items and section.get("if_empty") == "hide":
            return lines
        label = section.get("label", "")
        tmpl = section.get("template", "  {label}")
        if label:
            lines.append(StyledLine(
                text=_row_text(f" {label}:", inner, bd),
                role="muted",
            ))
        for item in items:
            if isinstance(item, str):
                text = interpolate(tmpl, {"": item, "label": item})
            else:
                text = interpolate(tmpl, item)
            lines.append(StyledLine(
                text=_row_text(text, inner, bd),
                role="body",
            ))

    elif stype == "bars":
        bar_width = section.get("bar_width", 10)
        tmpl = section.get(
            "template", " {label} [{bar}] {current}/{max}",
        )
        filled_ch, empty_ch = theme.bar_chars()
        for item in props.get(section.get("over", ""), []):
            cur = item.get("current", 0)
            mx = item.get("max", 1)
            ratio = cur / mx if mx else 0
            n = round(ratio * bar_width)
            bar_str = filled_ch * n + empty_ch * (bar_width - n)
            text = interpolate(tmpl, {**item, "bar": bar_str})
            lines.append(StyledLine(
                text=_row_text(text, inner, bd),
                role="body",
            ))

    elif stype == "progress":
        bar_width = section.get("bar_width", 20)
        tmpl = section.get(
            "template", " {label} [{bar}] {value}/{max}",
        )
        filled_ch, empty_ch = theme.bar_chars()
        val = props.get(section.get("value_prop", "value"), 0)
        mx = props.get(section.get("max_prop", "max"), 1)
        ratio = val / mx if mx else 0
        n = round(ratio * bar_width)
        bar_str = filled_ch * n + empty_ch * (bar_width - n)
        merged = {**props, "bar": bar_str}
        text = interpolate(tmpl, merged)
        lines.append(StyledLine(
            text=_row_text(text, inner, bd),
            role="body",
        ))

    elif stype == "numbered_list":
        items = props.get(section.get("over", ""), [])
        tmpl = section.get("template", " {label}")
        for i, item in enumerate(items, 1):
            text = interpolate(f" {i}. {tmpl.lstrip()}", item)
            lines.append(StyledLine(
                text=_row_text(text, inner, bd),
                role="body",
            ))

    elif stype == "checked_list":
        items = props.get(section.get("over", ""), [])
        check_prop = section.get("check_prop", "checked")
        tmpl = section.get("template", "{label}")
        for item in items:
            mark = "x" if item.get(check_prop) else " "
            text = f" [{mark}] " + interpolate(tmpl, item)
            lines.append(StyledLine(
                text=_row_text(text, inner, bd),
                role="body",
            ))

    elif stype == "active_list":
        items = props.get(section.get("over", ""), [])
        active_id = props.get(
            section.get("active_prop", "active_id"), "",
        )
        marker = section.get("marker", ">")
        tmpl = section.get("template", "{label}")
        pad = " " * len(marker)
        for item in items:
            item_id = item.get("id", "")
            prefix = marker if item_id == active_id else pad
            text = f" {prefix} " + interpolate(tmpl, item)
            lines.append(StyledLine(
                text=_row_text(text, inner, bd),
                role="body",
            ))

    return lines


# -- join layout ---------------------------------------------------------------


def _layout_tree(spec: dict, props: dict) -> list[StyledLine]:
    nodes = props.get(spec.get("prop", "nodes"), [])
    tmpl = spec.get("template", "{label}")
    raw: list[str] = []
    _tree_walk(nodes, tmpl, raw, "")
    return [StyledLine(text=line, role="body") for line in raw]


def _layout_join(spec: dict, props: dict) -> list[StyledLine]:
    items = props.get(spec.get("over", ""), [])
    sep = spec.get("separator", "  ")
    tmpl = spec.get("template", "{label}")
    prefix = interpolate(spec.get("prefix", ""), props)
    parts = [interpolate(tmpl, item) for item in items]
    return [StyledLine(text=prefix + sep.join(parts), role="body")]


def _layout_banner(
    spec: dict,
    props: dict,
    component: Component,
    available_width: int,
) -> list[StyledLine]:
    """Render a banner using ASCII art generation or a component art fallback."""
    text = props.get("text", "")
    style_hint = props.get("style_hint", "splash")
    font = props.get("font")
    has_width_constraint = (
        spec.get("width") is not None
        or spec.get("min_width") is not None
        or spec.get("max_width") is not None
    )
    max_width = resolve_width(spec, available_width) if has_width_constraint else available_width

    result: str | None = None
    try:
        from .banner import render_banner_text  # noqa: PLC0415

        result = render_banner_text(text, style_hint, font=font, max_width=max_width)
    except ImportError:
        pass

    raw = result.rstrip("\n") if result is not None else component.art.rstrip("\n")
    return [StyledLine(text=line, role="body") for line in raw.splitlines() if line]


# -- flat render-type layout functions -----------------------------------------


def _layout_clock(spec: dict, props: dict) -> list[StyledLine]:
    label = props.get("label", "")
    segments = props.get("segments", 0)
    filled = props.get("filled", 0)
    clock = "\u25cf" * filled + "\u25cb" * max(0, segments - filled)
    lines: list[StyledLine] = []
    if label:
        lines.append(StyledLine(text=label, role="body"))
    lines.append(StyledLine(
        text=f"[{clock}]   {filled} / {segments}", role="body",
    ))
    return lines


def _layout_stage_track(spec: dict, props: dict) -> list[StyledLine]:
    label = props.get("label", "")
    stages = props.get("stages", [])
    current = props.get("current_stage_index", 0)
    if not stages:
        return []
    boxes: list[str] = []
    centers: list[int] = []
    pos = 0
    for i, stage in enumerate(stages):
        stage_label = stage.get("label", stage.get("id", ""))
        box = f"[ {stage_label} ]"
        if i > 0:
            boxes.append("\u2500")
            pos += 1
        centers.append(pos + (len(box) - 1) // 2)
        boxes.append(box)
        pos += len(box)
    track_line = "".join(boxes)
    marker_line = ""
    if 0 <= current < len(centers):
        marker_line = " " * centers[current] + "^"
    lines: list[StyledLine] = []
    if label:
        lines.append(StyledLine(text=f"{label}:", role="body"))
    if track_line:
        lines.append(StyledLine(text=track_line, role="body"))
    if marker_line:
        lines.append(StyledLine(text=marker_line, role="body"))
    return lines


def _layout_frames(spec: dict, props: dict) -> list[StyledLine]:
    frames = props.get(spec.get("prop", "frames"), [])
    if not frames:
        return []
    text = str(frames[0])
    return [StyledLine(text=line, role="body") for line in text.splitlines()]


def _layout_art_lookup(
    spec: dict, props: dict, component: Component,
) -> list[StyledLine]:
    # Decorations not available in layout path; use component art fallback.
    art = component.art.rstrip("\n") if component.art else ""
    if not art:
        return []
    width = int(props.get("width", 0))
    height = int(props.get("height", 0))
    lines = art.splitlines()
    if height and len(lines) > height:
        lines = lines[:height]
    if width:
        lines = [ln[:width].ljust(width) for ln in lines]
    if height and len(lines) < height:
        pad = width if width else (max(len(ln) for ln in lines) if lines else 0)
        lines.extend([" " * pad] * (height - len(lines)))
    return [StyledLine(text=ln, role="body") for ln in lines]


# -- tuple-based layout helpers ------------------------------------------------


def _tuples_to_styled(
    tuples: list[tuple[str, str]],
) -> list[StyledLine]:
    """Convert (text, role) tuples to StyledLine objects."""
    return [StyledLine(text=text, role=role) for text, role in tuples]


# -- inline layout ------------------------------------------------------------


def _layout_inline(
    spec: dict,
    props: dict,
    available_width: int,
) -> list[StyledLine]:
    line = interpolate(spec.get("template", ""), props)
    has_width_constraint = (
        spec.get("width") is not None
        or spec.get("min_width") is not None
        or spec.get("max_width") is not None
    )
    if has_width_constraint:
        target = resolve_width(spec, available_width)
        if len(line) < target:
            pad_char = line[0] if line and line.strip() else " "
            line = line + pad_char * (target - len(line))
        elif len(line) > target:
            line = line[:target]

    return [StyledLine(text=line, role="body")]
