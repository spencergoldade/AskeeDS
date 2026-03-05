"""Render type: table — auto-width column table with header separator."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
