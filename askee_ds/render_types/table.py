"""Render type: table — auto-width column table with header separator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..sizing import resolve_width

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_table(spec: dict, props: dict, ctx: RenderContext) -> str:
    columns = props.get(spec.get("columns_prop", "columns"), [])
    rows = props.get(spec.get("rows_prop", "rows"), [])
    if not columns:
        return ""

    col_widths = [len(str(h)) for h in columns]
    for r in rows:
        for i, cell in enumerate(r if isinstance(r, list) else []):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    if spec.get("width") is not None or spec.get("min_width") is not None or spec.get("max_width") is not None:
        max_total = resolve_width(spec, ctx.available_width)
        n = len(col_widths)
        inner_budget = max_total - 2 - 2 * n
        if inner_budget >= n and sum(col_widths) > inner_budget and sum(col_widths) > 0:
            col_widths = [max(1, int(w * inner_budget / sum(col_widths))) for w in col_widths]

    def _sep() -> str:
        return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def _data_row(cells: list) -> str:
        parts: list[str] = []
        for i, w in enumerate(col_widths):
            val = str(cells[i]) if i < len(cells) else ""
            parts.append(" " + val.ljust(w) + " ")
        return "|" + "|".join(parts) + "|"

    lines = [_sep(), _data_row(columns), _sep()]
    for r in rows:
        cells = r if isinstance(r, list) else []
        lines.append(_data_row(cells))
    lines.append(_sep())
    return "\n".join(lines)
