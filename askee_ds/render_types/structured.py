"""Structured render helpers — table and grid as (text, role) tuples.

These helpers are consumed by layout.py (LayoutEngine path) and by the thin
``render_*`` wrappers in table.py / grid.py (legacy string-output path).
"""

from __future__ import annotations

from ..sizing import has_width_constraint, resolve_width


def _table_lines(
    spec: dict,
    props: dict,
    available_width: int,
) -> list[tuple[str, str]]:
    """Produce (text, role) tuples for a bordered column table.

    Roles: ``border`` for separator rows, ``header`` for the column header row,
    ``body`` for data rows.
    """
    columns = props.get(spec.get("columns_prop", "columns"), [])
    rows = props.get(spec.get("rows_prop", "rows"), [])
    if not columns:
        return []

    col_widths = [len(str(h)) for h in columns]
    for r in rows:
        for i, cell in enumerate(r if isinstance(r, list) else []):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    if has_width_constraint(spec):
        max_total = resolve_width(spec, available_width)
        n = len(col_widths)
        inner_budget = max_total - 2 - 2 * n
        if inner_budget >= n and sum(col_widths) > inner_budget and sum(col_widths) > 0:
            col_widths = [
                max(1, int(w * inner_budget / sum(col_widths))) for w in col_widths
            ]

    def _sep() -> str:
        return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def _data_row(cells: list) -> str:
        parts: list[str] = []
        for i, w in enumerate(col_widths):
            val = str(cells[i]) if i < len(cells) else ""
            parts.append(" " + val.ljust(w) + " ")
        return "|" + "|".join(parts) + "|"

    result: list[tuple[str, str]] = []
    result.append((_sep(), "border"))
    result.append((_data_row(list(columns)), "header"))
    result.append((_sep(), "border"))
    for r in rows:
        cells = r if isinstance(r, list) else []
        result.append((_data_row(cells), "body"))
    result.append((_sep(), "border"))
    return result


def _grid_lines(
    spec: dict,
    props: dict,
    available_width: int,
) -> list[tuple[str, str]]:
    """Produce (text, role) tuples for a bordered cell grid.

    Roles: ``border`` for separator rows, ``body`` for cell rows.
    """
    slots = list(props.get(spec.get("prop", "slots"), []))
    if not slots:
        return []

    columns = props.get(spec.get("columns_prop", "columns"), 3)
    cell_width = spec.get("cell_width", 8)
    if columns < 1:
        return []

    if has_width_constraint(spec):
        total_width = resolve_width(spec, available_width)
        inner = max(1, total_width - 2)
        cell_width = max(1, inner // columns)

    while len(slots) % columns != 0:
        slots.append(None)

    sep = "+" + (("-" * cell_width + "+") * columns)
    result: list[tuple[str, str]] = []
    for start in range(0, len(slots), columns):
        result.append((sep, "border"))
        r = slots[start: start + columns]
        cells: list[str] = []
        for slot in r:
            if slot and isinstance(slot, dict) and slot.get("label"):
                cells.append((" " + slot["label"]).ljust(cell_width)[:cell_width])
            else:
                cells.append(" " * cell_width)
        result.append(("|" + "|".join(cells) + "|", "body"))
    result.append((sep, "border"))
    return result
