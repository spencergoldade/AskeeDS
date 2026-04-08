"""Render type: bubble — speech bubble with directional tail."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._registry import RenderContext


def _bubble_lines(spec: dict, props: dict) -> list[tuple[str, str]]:
    """Produce (text, role) tuples for a speech bubble.

    Top and bottom separator lines get role ``"border"``;
    content lines get role ``"body"``.
    """
    text = props.get("text", "")
    tail = props.get("tail", spec.get("tail", "left"))
    max_width = spec.get("max_width", 40)
    inner = max_width - 4
    wrapped = textwrap.wrap(text, width=inner, break_long_words=False) or [""]
    content_w = max(len(line) for line in wrapped)
    w = content_w + 2
    sep = "+" + "-" * w + "+"

    result: list[tuple[str, str]] = [(sep, "border")]
    for i, wline in enumerate(wrapped):
        padded = " " + wline.ljust(content_w) + " "
        if tail == "left" and i == 0:
            result.append(("/" + padded + "|", "body"))
        elif tail == "right" and i == len(wrapped) - 1:
            result.append(("|" + padded + "\\", "body"))
        else:
            result.append(("|" + padded + "|", "body"))
    result.append((sep, "border"))
    return result


def render_bubble(spec: dict, props: dict, ctx: RenderContext) -> str:
    return "\n".join(text for text, _ in _bubble_lines(spec, props))
