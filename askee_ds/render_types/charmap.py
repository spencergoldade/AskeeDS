"""Render type: charmap — 2D character grid with optional legend."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_charmap(spec: dict, props: dict, ctx: RenderContext) -> str:
    grid = props.get(spec.get("prop", "grid"), [])
    legend = props.get(spec.get("legend_prop", "legend_entries"), [])
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    bd = ctx.theme.border(spec.get("border", "single"))
    lines: list[str] = []
    lines.append(bd["tl"] + bd["h"] * width + bd["tr"])
    for r in grid:
        row_str = "".join(str(c) for c in r).ljust(width)[:width]
        lines.append(bd["v"] + row_str + bd["v"])
    lines.append(bd["bl"] + bd["h"] * width + bd["br"])
    if legend:
        entries = [f"{e.get('char', '?')} {e.get('label', '')}" for e in legend]
        lines.append("  " + "  ".join(entries))
    return "\n".join(lines)
