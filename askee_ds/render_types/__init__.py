"""
Render type registry for AskeeDS.

Each render type is a function: (spec, props, ctx) -> str.
Built-in types are auto-registered on import. Register custom types
with register() to extend the renderer without modifying its source.

    from askee_ds.render_types import register, list_types

    def my_renderer(spec, props, ctx):
        return f"Custom: {ctx.theme.colors('neutral')}"

    register("my_custom", my_renderer)
"""

from ._registry import RenderContext, register, get, list_types

from .inline import render_inline, render_join
from .box import render_box
from .table import render_table
from .bubble import render_bubble
from .tree import render_tree
from .grid import render_grid
from .charmap import render_charmap
from .layout import render_stack, render_columns, render_shell
from .specialized import (
    render_clock, render_stage_track, render_frames,
    render_banner, render_art_lookup,
)

register("inline", render_inline)
register("join", render_join)
register("box", render_box)
register("table", render_table)
register("bubble", render_bubble)
register("tree", render_tree)
register("grid", render_grid)
register("charmap", render_charmap)
register("stack", render_stack)
register("columns", render_columns)
register("shell", render_shell)
register("clock", render_clock)
register("stage_track", render_stage_track)
register("frames", render_frames)
register("banner", render_banner)
register("art_lookup", render_art_lookup)

__all__ = [
    "RenderContext",
    "register",
    "get",
    "list_types",
]
