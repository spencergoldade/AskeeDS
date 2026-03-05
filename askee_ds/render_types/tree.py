"""Render type: tree — recursive tree with branch connectors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import interpolate

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_tree(spec: dict, props: dict, ctx: RenderContext) -> str:
    nodes = props.get(spec.get("prop", "nodes"), [])
    tmpl = spec.get("template", "{label}")
    lines: list[str] = []
    _tree_walk(nodes, tmpl, lines, "")
    return "\n".join(lines)


def _tree_walk(
    nodes: list, tmpl: str, lines: list[str], prefix: str,
) -> None:
    for i, node in enumerate(nodes):
        is_last = i == len(nodes) - 1
        connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
        text = interpolate(tmpl, node)
        lines.append(prefix + connector + text)
        children = node.get("children", [])
        if children:
            ext = "    " if is_last else "\u2502   "
            _tree_walk(children, tmpl, lines, prefix + ext)
