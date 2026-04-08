"""Render types: clock, stage_track, frames, banner, art_lookup.

These are domain-specific render types that don't fit the general-purpose
categories (box, table, tree, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._registry import RenderContext


def render_clock(spec: dict, props: dict, ctx: RenderContext) -> str:
    label = props.get("label", "")
    segments = props.get("segments", 0)
    filled = props.get("filled", 0)
    clock = "\u25cf" * filled + "\u25cb" * max(0, segments - filled)
    return f"{label}\n[{clock}]   {filled} / {segments}"


def render_stage_track(spec: dict, props: dict, ctx: RenderContext) -> str:
    label = props.get("label", "")
    stages = props.get("stages", [])
    current = props.get("current_stage_index", 0)
    boxes: list[str] = []
    centers: list[int] = []
    pos = 0
    for i, stage in enumerate(stages):
        stage_label = stage.get("label", stage.get("id", ""))
        box = f"[ {stage_label} ]"
        if i > 0:
            boxes.append("\u2500")
            pos += 1
        centers.append(pos + (len(box) - 1) // 2)
        boxes.append(box)
        pos += len(box)
    track_line = "".join(boxes)
    marker_line = ""
    if 0 <= current < len(centers):
        marker_line = " " * centers[current] + "^"
    lines: list[str] = []
    if label:
        lines.append(f"{label}:")
    if track_line:
        lines.append(track_line)
    if marker_line:
        lines.append(marker_line)
    return "\n".join(lines)


def render_frames(spec: dict, props: dict, ctx: RenderContext) -> str:
    frames = props.get(spec.get("prop", "frames"), [])
    if frames:
        return str(frames[0])
    return ""


def render_banner(spec: dict, props: dict, ctx: RenderContext) -> str:
    from ..banner import render_banner_text
    from ..sizing import has_width_constraint, resolve_width

    text = props.get("text", "")
    style_hint = props.get("style_hint", "splash")
    font = props.get("font")
    max_width = (
        resolve_width(spec, ctx.available_width)
        if has_width_constraint(spec)
        else None
    )
    result = render_banner_text(text, style_hint, font=font, max_width=max_width or 80)
    if result is not None:
        return result.rstrip("\n")
    return ctx.component.art.rstrip("\n")


def render_art_lookup(spec: dict, props: dict, ctx: RenderContext) -> str:
    art_id = str(props.get("art_id", ""))
    entry = ctx.decorations.get(art_id)
    art_text = entry.get("art", "").rstrip("\n") if entry else ""
    if not art_text:
        art_text = ctx.component.art.rstrip("\n")
    width = int(props.get("width", 0))
    height = int(props.get("height", 0))
    if not width and not height:
        return art_text
    lines = art_text.splitlines()
    if height and len(lines) > height:
        lines = lines[:height]
    if width:
        lines = [ln[:width].ljust(width) for ln in lines]
    if height and len(lines) < height:
        pad = width if width else (max(len(ln) for ln in lines) if lines else 0)
        lines.extend([" " * pad] * (height - len(lines)))
    return "\n".join(lines)
