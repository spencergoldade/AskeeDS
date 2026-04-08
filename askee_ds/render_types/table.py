"""Render type: table — auto-width column table with header separator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .structured import _table_lines

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_table(spec: dict, props: dict, ctx: RenderContext) -> str:
    tuples = _table_lines(spec, props, ctx.available_width)
    return "\n".join(text for text, _ in tuples)
