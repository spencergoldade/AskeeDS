"""Render type: grid — bordered cell grid from a slots array."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .structured import _grid_lines

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_grid(spec: dict, props: dict, ctx: RenderContext) -> str:
    tuples = _grid_lines(spec, props, ctx.available_width)
    return "\n".join(text for text, _ in tuples)
