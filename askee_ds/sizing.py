"""
AskeeDS sizing — resolve adaptive width and height from render specs.

Components declare sizing behavior in their render spec. Width can be:
  - An integer (fixed): always that many characters wide.
  - "fill": expand to the available container width.
  - "content": size to content (upper-bounded by available width).

Optional constraints narrow the result:
  - min_width / max_width: clamp the resolved width.
  - min_height / max_height: clamp the resolved height.

    from askee_ds.sizing import resolve_width

    width = resolve_width(spec, available=100)
"""

from __future__ import annotations

DEFAULT_WIDTH = 100
DEFAULT_HEIGHT = 30

_ABSOLUTE_MIN_WIDTH = 4


def has_width_constraint(spec: dict) -> bool:
    """Return True if *spec* declares any width constraint.

    Checks for ``width``, ``min_width``, or ``max_width`` keys with
    non-None values.
    """
    return (
        spec.get("width") is not None
        or spec.get("min_width") is not None
        or spec.get("max_width") is not None
    )


def resolve_width(spec: dict, available: int = DEFAULT_WIDTH) -> int:
    """Resolve the effective width from a render spec.

    Args:
        spec: The component's render spec dict.
        available: The available width in the container (characters).

    Returns:
        Concrete width in characters.
    """
    raw = spec.get("width")
    min_w = spec.get("min_width")
    max_w = spec.get("max_width")

    if raw is None:
        w = available
    elif isinstance(raw, int):
        w = raw
    elif raw == "fill":
        w = available
    elif raw == "content":
        w = available
    else:
        w = available

    if min_w is not None:
        w = max(w, int(min_w))
    if max_w is not None:
        w = min(w, int(max_w))

    return max(w, _ABSOLUTE_MIN_WIDTH)


def resolve_height(
    spec: dict, content_lines: int, available: int | None = None,
) -> int:
    """Resolve the effective height from a render spec.

    Args:
        spec: The component's render spec dict.
        content_lines: The number of lines the content produced.
        available: The available height in the container, if known.

    Returns:
        Concrete height in lines.
    """
    raw = spec.get("height")
    min_h = spec.get("min_height")
    max_h = spec.get("max_height")

    if raw is None or raw == "content":
        h = content_lines
    elif isinstance(raw, int):
        h = raw
    elif raw == "fill":
        h = available if available else content_lines
    else:
        h = content_lines

    if min_h is not None:
        h = max(h, int(min_h))
    if max_h is not None:
        h = min(h, int(max_h))

    return max(h, 1)
