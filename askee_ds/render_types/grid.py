"""Render type: grid — bordered cell grid from a slots array."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_grid(spec: dict, props: dict, ctx: RenderContext) -> str:
    slots = list(props.get(spec.get("prop", "slots"), []))
    columns = props.get(spec.get("columns_prop", "columns"), 3)
    cell_width = spec.get("cell_width", 8)
    if columns < 1:
        return ""

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
