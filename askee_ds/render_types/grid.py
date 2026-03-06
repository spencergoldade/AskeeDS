"""Render type: grid — bordered cell grid from a slots array."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..sizing import resolve_width

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_grid(spec: dict, props: dict, ctx: RenderContext) -> str:
    slots = list(props.get(spec.get("prop", "slots"), []))
    columns = props.get(spec.get("columns_prop", "columns"), 3)
    cell_width = spec.get("cell_width", 8)
    if columns < 1:
        return ""

    if spec.get("width") is not None or spec.get("min_width") is not None or spec.get("max_width") is not None:
        total_width = resolve_width(spec, ctx.available_width)
        inner = max(1, total_width - 2)
        cell_width = max(1, inner // columns)

    while len(slots) % columns != 0:
        slots.append(None)

    sep = "+" + (("-" * cell_width + "+") * columns)
    lines: list[str] = []
    for start in range(0, len(slots), columns):
        lines.append(sep)
        r = slots[start : start + columns]
        cells: list[str] = []
        for slot in r:
            if slot and isinstance(slot, dict) and slot.get("label"):
                cells.append((" " + slot["label"]).ljust(cell_width)[:cell_width])
            else:
                cells.append(" " * cell_width)
        lines.append("|" + "|".join(cells) + "|")
    lines.append(sep)
    return "\n".join(lines)
