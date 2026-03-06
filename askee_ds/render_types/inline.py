"""Render types: inline (single-line template) and join (array with separator)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import interpolate
from ..sizing import resolve_width

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_inline(spec: dict, props: dict, ctx: RenderContext) -> str:
    line = interpolate(spec.get("template", ""), props)
    if spec.get("width") is not None or spec.get("min_width") is not None or spec.get("max_width") is not None:
        target = resolve_width(spec, ctx.available_width)
        if len(line) < target:
            pad_char = (line[0] if line and line.strip() else "-")
            line = line + pad_char * (target - len(line))
        elif len(line) > target:
            line = line[:target]
    return line


def render_join(spec: dict, props: dict, ctx: RenderContext) -> str:
    items = props.get(spec.get("over", ""), [])
    sep = spec.get("separator", "  ")
    tmpl = spec.get("template", "{label}")
    prefix = interpolate(spec.get("prefix", ""), props)
    parts = [interpolate(tmpl, item) for item in items]
    return prefix + sep.join(parts)
