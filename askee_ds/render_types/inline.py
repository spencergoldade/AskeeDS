"""Render types: inline (single-line template) and join (array with separator)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import interpolate

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_inline(spec: dict, props: dict, ctx: RenderContext) -> str:
    return interpolate(spec.get("template", ""), props)


def render_join(spec: dict, props: dict, ctx: RenderContext) -> str:
    items = props.get(spec.get("over", ""), [])
    sep = spec.get("separator", "  ")
    tmpl = spec.get("template", "{label}")
    prefix = interpolate(spec.get("prefix", ""), props)
    parts = [interpolate(tmpl, item) for item in items]
    return prefix + sep.join(parts)
