"""Render type: charmap — 2D character grid with optional legend."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._registry import RenderContext
    from ..theme import Theme


def _charmap_lines(spec: dict, props: dict, theme: Theme) -> list[tuple[str, str]]:
    """Produce (text, role) tuples for a charmap grid.

    Border rows get role ``"border"``, grid rows get role ``"body"``,
    and the legend line (if present) gets role ``"muted"``.
    Returns an empty list when the grid prop is missing or empty.
    """
    grid = props.get(spec.get("prop", "grid"), [])
    legend = props.get(spec.get("legend_prop", "legend_entries"), [])
    if not grid:
        return []
    width = max(len(r) for r in grid)
    bd = theme.border(spec.get("border", "single"))
    result: list[tuple[str, str]] = []
    result.append((bd["tl"] + bd["h"] * width + bd["tr"], "border"))
    for r in grid:
        row_str = "".join(str(c) for c in r).ljust(width)[:width]
        result.append((bd["v"] + row_str + bd["v"], "body"))
    result.append((bd["bl"] + bd["h"] * width + bd["br"], "border"))
    if legend:
        entries = [f"{e.get('char', '?')} {e.get('label', '')}" for e in legend]
        result.append(("  " + "  ".join(entries), "muted"))
    return result


def render_charmap(spec: dict, props: dict, ctx: RenderContext) -> str:
    lines = _charmap_lines(spec, props, ctx.theme)
    return "\n".join(text for text, _ in lines)
