"""Render types: stack, columns, shell — layout composition primitives."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..sizing import resolve_width

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_stack(spec: dict, props: dict, ctx: RenderContext) -> str:
    prop_name = spec.get("prop", "blocks")
    blocks = props.get(prop_name, [])
    if not blocks or not isinstance(blocks, list):
        return ""
    bd = ctx.theme.border(spec.get("border", "single"))
    outer = resolve_width(spec, ctx.available_width)
    width = outer - 2
    width = max(width, 10)
    lines: list[str] = []
    for i, block in enumerate(blocks):
        block_str = str(block)
        if i == 0:
            lines.append(bd["tl"] + bd["h"] * width + bd["tr"])
        else:
            lines.append(bd["tj_right"] + bd["h"] * width + bd["tj_left"])
        for bline in block_str.splitlines():
            lines.append(bd["v"] + bline.ljust(width)[:width] + bd["v"])
    lines.append(bd["bl"] + bd["h"] * width + bd["br"])
    return "\n".join(lines)


def render_columns(spec: dict, props: dict, ctx: RenderContext) -> str:
    left_str = str(props.get(spec.get("left_prop", "left_content"), ""))
    right_str = str(props.get(spec.get("right_prop", "right_content"), ""))
    left_w = int(props.get(spec.get("width_prop", "left_width"), 0)) or 20
    bd = ctx.theme.border(spec.get("border", "single"))
    outer = resolve_width(spec, ctx.available_width)
    right_w = outer - left_w - 3
    right_w = max(right_w, 10)
    left_lines = left_str.splitlines() if left_str.strip() else [""]
    right_lines = right_str.splitlines() if right_str.strip() else [""]
    height = max(len(left_lines), len(right_lines))
    while len(left_lines) < height:
        left_lines.append("")
    while len(right_lines) < height:
        right_lines.append("")
    lines: list[str] = []
    lines.append(bd["tl"] + bd["h"] * left_w + bd["tj_down"] + bd["h"] * right_w + bd["tr"])
    for ll, rl in zip(left_lines, right_lines):
        lines.append(
            bd["v"] + ll.ljust(left_w)[:left_w]
            + bd["v"] + rl.ljust(right_w)[:right_w]
            + bd["v"]
        )
    lines.append(bd["bl"] + bd["h"] * left_w + bd["tj_up"] + bd["h"] * right_w + bd["br"])
    return "\n".join(lines)


def render_shell(spec: dict, props: dict, ctx: RenderContext) -> str:
    header_str = str(props.get(spec.get("header_prop", "header"), ""))
    sidebar_str = str(props.get(spec.get("sidebar_prop", "sidebar"), ""))
    content_str = str(props.get(spec.get("content_prop", "content"), ""))
    sidebar_w = int(props.get(spec.get("width_prop", "sidebar_width"), 0)) or 20
    bd = ctx.theme.border(spec.get("border", "single"))
    outer = resolve_width(spec, ctx.available_width)
    content_w = outer - sidebar_w - 3
    content_w = max(content_w, 10)
    total_inner = sidebar_w + 1 + content_w
    sb_lines = sidebar_str.splitlines() if sidebar_str.strip() else [""]
    ct_lines = content_str.splitlines() if content_str.strip() else [""]
    body_h = max(len(sb_lines), len(ct_lines))
    while len(sb_lines) < body_h:
        sb_lines.append("")
    while len(ct_lines) < body_h:
        ct_lines.append("")
    lines: list[str] = []
    lines.append(bd["tl"] + bd["h"] * total_inner + bd["tr"])
    for hl in (header_str.splitlines() or [""]):
        lines.append(bd["v"] + hl.ljust(total_inner)[:total_inner] + bd["v"])
    lines.append(bd["tj_right"] + bd["h"] * sidebar_w + bd["tj_down"] + bd["h"] * content_w + bd["tj_left"])
    for sl, cl in zip(sb_lines, ct_lines):
        lines.append(
            bd["v"] + sl.ljust(sidebar_w)[:sidebar_w]
            + bd["v"] + cl.ljust(content_w)[:content_w]
            + bd["v"]
        )
    lines.append(bd["bl"] + bd["h"] * sidebar_w + bd["tj_up"] + bd["h"] * content_w + bd["br"])
    return "\n".join(lines)
