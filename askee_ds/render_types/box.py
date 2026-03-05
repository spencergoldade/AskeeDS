"""Render type: box — bordered box with typed sections.

Sections are the building blocks inside a box: header, text, wrap, list,
bars, progress, checked_list, active_list, numbered_list, divider, blank.
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

from ._helpers import interpolate, row
from ..sizing import resolve_width

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_box(spec: dict, props: dict, ctx: RenderContext) -> str:
    width = resolve_width(spec, ctx.available_width)
    bd = ctx.theme.border(spec.get("border", "single"))
    inner = width - 2
    lines: list[str] = []

    lines.append(bd["tl"] + bd["h"] * inner + bd["tr"])

    for section in spec.get("sections", []):
        lines.extend(_render_section(section, props, inner, bd, ctx))

    lines.append(bd["bl"] + bd["h"] * inner + bd["br"])
    return "\n".join(lines)


def _render_section(
    section: dict, props: dict, inner: int, bd: dict, ctx: RenderContext,
) -> list[str]:
    stype = section.get("type", "text")
    lines: list[str] = []

    if stype == "header":
        text = interpolate(section["text"], props)
        lines.append(row(f" {text}", inner, bd))

    elif stype == "divider":
        lines.append(bd["tj_right"] + bd["h"] * inner + bd["tj_left"])

    elif stype == "text":
        text = interpolate(section["text"], props)
        lines.append(row(text, inner, bd))

    elif stype == "wrap":
        raw = interpolate(section["text"], props)
        indent = section.get("indent", 0)
        prefix = " " * indent
        wrapped = textwrap.wrap(
            raw, width=inner - indent * 2, break_long_words=False,
        )
        for wline in wrapped or [""]:
            lines.append(row(f"{prefix}{wline}", inner, bd))

    elif stype == "blank":
        lines.append(row("", inner, bd))

    elif stype == "list":
        items = props.get(section.get("over", ""), [])
        if not items and section.get("if_empty") == "hide":
            return lines
        label = section.get("label", "")
        tmpl = section.get("template", "  {label}")
        if label:
            lines.append(row(f" {label}:", inner, bd))
        for item in items:
            if isinstance(item, str):
                text = interpolate(tmpl, {"": item, "label": item})
            else:
                text = interpolate(tmpl, item)
            lines.append(row(text, inner, bd))

    elif stype == "bars":
        bar_width = section.get("bar_width", 10)
        tmpl = section.get(
            "template", " {label} [{bar}] {current}/{max}"
        )
        filled_ch, empty_ch = ctx.theme.bar_chars()
        for item in props.get(section.get("over", ""), []):
            cur = item.get("current", 0)
            mx = item.get("max", 1)
            ratio = cur / mx if mx else 0
            n = round(ratio * bar_width)
            bar_str = filled_ch * n + empty_ch * (bar_width - n)
            text = interpolate(tmpl, {**item, "bar": bar_str})
            lines.append(row(text, inner, bd))

    elif stype == "progress":
        bar_width = section.get("bar_width", 20)
        tmpl = section.get(
            "template", " {label} [{bar}] {value}/{max}"
        )
        filled_ch, empty_ch = ctx.theme.bar_chars()
        val = props.get(section.get("value_prop", "value"), 0)
        mx = props.get(section.get("max_prop", "max"), 1)
        ratio = val / mx if mx else 0
        n = round(ratio * bar_width)
        bar_str = filled_ch * n + empty_ch * (bar_width - n)
        merged = {**props, "bar": bar_str}
        text = interpolate(tmpl, merged)
        lines.append(row(text, inner, bd))

    elif stype == "numbered_list":
        items = props.get(section.get("over", ""), [])
        tmpl = section.get("template", " {label}")
        for i, item in enumerate(items, 1):
            text = interpolate(f" {i}. {tmpl.lstrip()}", item)
            lines.append(row(text, inner, bd))

    elif stype == "checked_list":
        items = props.get(section.get("over", ""), [])
        check_prop = section.get("check_prop", "checked")
        tmpl = section.get("template", "{label}")
        for item in items:
            mark = "x" if item.get(check_prop) else " "
            text = f" [{mark}] " + interpolate(tmpl, item)
            lines.append(row(text, inner, bd))

    elif stype == "active_list":
        items = props.get(section.get("over", ""), [])
        active_id = props.get(
            section.get("active_prop", "active_id"), ""
        )
        marker = section.get("marker", ">")
        tmpl = section.get("template", "{label}")
        pad = " " * len(marker)
        for item in items:
            item_id = item.get("id", "")
            prefix = marker if item_id == active_id else pad
            text = f" {prefix} " + interpolate(tmpl, item)
            lines.append(row(text, inner, bd))

    return lines
