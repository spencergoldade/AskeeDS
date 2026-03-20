"""
AskeeDS Pyglet rendering pathway.

Draws component panes directly into a pyglet.graphics.Batch — no string output.
The existing ASCII/Textual render() path is completely untouched.

Type contract for callers (engine bridge):
  - viewport: Rect-like — must have .x, .y, .width, .height (int)
  - theme_state: ThemeState-like — must have .palette (str), .tint (str), .vignette (bool)
  - batch: pyglet.graphics.Batch
  - pane_id: non-empty str for any draw function that tracks per-pane state
              (e.g. input-pane cursor blink). Safe to omit for stateless panes.

AskeeDS does not import from the engine package. Both types are passed as Any
to preserve standalone independence.
"""

from __future__ import annotations

from typing import Any, Callable

from .loader import Component

# ---------------------------------------------------------------------------
# Font size token → pixel size mapping
# ---------------------------------------------------------------------------

FONT_SIZES: dict[str, int] = {
    "large": 28,
    "medium": 18,
    "small": 14,
    "micro": 10,
}

_DEFAULT_FONT_SIZE = FONT_SIZES["medium"]

# Per-pane cursor blink state: pane_id → cursor_visible (bool)
# NOTE: Tests that register draw functions must call reload(pr) to reset this
# dict between test runs, same as _REGISTRY.
_CURSOR_STATE: dict[str, bool] = {}


def _resolve_font_size(component: Component) -> int:
    return FONT_SIZES.get(component.font_size, _DEFAULT_FONT_SIZE)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_DrawFn = Callable[[Component, dict, Any, Any, Any, str], None]
#                   component  props  theme  viewport batch  pane_id

# NOTE: Tests that register draw functions must call reload(pr) to reset this
# dict between test runs. Python caches the module, so registrations accumulate
# across tests without an explicit reload.
_REGISTRY: dict[str, _DrawFn] = {}


def register(name: str, fn: _DrawFn) -> None:
    """Register a draw function for a component name."""
    _REGISTRY[name] = fn


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def render_pyglet(
    component: Component,
    props: dict,
    theme_state: Any,
    viewport: Any,
    batch: Any,
    pane_id: str = "",
) -> None:
    """Draw a component pane into a Pyglet batch.

    Dispatches to the registered draw function for component.name, or to
    _draw_fallback if no draw function is registered.

    Args:
        component:   Loaded AskeeDS Component.
        props:       Props dict matching the component's schema.
        theme_state: ThemeState-like — accessed via .palette, .tint, .vignette.
        viewport:    Rect-like — accessed via .x, .y, .width, .height.
        batch:       pyglet.graphics.Batch to accumulate draw calls into.
        pane_id:     Stable per-pane identifier. Must be non-empty for any draw
                     function that maintains per-pane state (e.g. cursor blink).
    """
    fn = _REGISTRY.get(component.name, _draw_fallback)
    fn(component, props, theme_state, viewport, batch, pane_id)


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


def _draw_fallback(
    component: Component,
    props: dict,  # noqa: ARG001
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> None:
    """Render a greyed-out placeholder label for unregistered components."""
    import pyglet  # noqa: PLC0415

    pyglet.text.Label(
        f"[{component.name}]",
        font_size=_resolve_font_size(component),
        x=viewport.x,
        y=viewport.y,
        color=(120, 120, 120, 255),
        batch=batch,
    )


# ---------------------------------------------------------------------------
# history-pane.default
# ---------------------------------------------------------------------------


def _draw_history_pane(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> None:
    import pyglet  # noqa: PLC0415

    lines: list[str] = props.get("lines", [])
    max_lines: int = props.get("max_lines", 20)
    visible = lines[-max_lines:] if len(lines) > max_lines else lines
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    # Background
    pyglet.shapes.Rectangle(
        viewport.x,
        viewport.y,
        viewport.width,
        viewport.height,
        color=(20, 20, 20, 255),
        batch=batch,
    )

    # Draw lines bottom-to-top so most recent is nearest the input pane
    y = viewport.y + line_height
    for line in reversed(visible):
        pyglet.text.Label(
            line,
            font_size=font_size,
            x=viewport.x + 8,
            y=y,
            width=viewport.width - 16,
            multiline=True,
            batch=batch,
        )
        y += line_height


register("history-pane.default", _draw_history_pane)


# ---------------------------------------------------------------------------
# input-pane.default
# ---------------------------------------------------------------------------


def _draw_input_pane(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,
) -> None:
    import pyglet  # noqa: PLC0415

    value: str = props.get("value", "")
    placeholder: str = props.get("placeholder", "")
    font_size = _resolve_font_size(component)

    # Register cursor blink callback once per pane_id
    if pane_id not in _CURSOR_STATE:
        _CURSOR_STATE[pane_id] = True

        def _toggle(_dt: float, _pid: str = pane_id) -> None:
            _CURSOR_STATE[_pid] = not _CURSOR_STATE[_pid]

        pyglet.clock.schedule_interval(_toggle, 0.5)

    cursor = "█" if _CURSOR_STATE.get(pane_id, True) else " "
    if value:
        display_text = f"> {value}{cursor}"
    elif placeholder:
        display_text = f"> {placeholder}"
    else:
        display_text = f"> {cursor}"

    pyglet.text.Label(
        display_text,
        font_size=font_size,
        x=viewport.x + 8,
        y=viewport.y + 8,
        width=viewport.width - 16,
        batch=batch,
    )


register("input-pane.default", _draw_input_pane)


# ---------------------------------------------------------------------------
# character-pane.default
# ---------------------------------------------------------------------------

_VIGNETTE_DEPTH = 32  # pixel width of the vignette edge strips


def _draw_character_pane(
    component: Component,
    props: dict,
    theme_state: Any,
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> None:
    import pyglet  # noqa: PLC0415

    portrait_lines: list[str] = props.get("portrait_lines", [])
    font_size = _resolve_font_size(component)
    line_height = font_size + 2

    y = viewport.y + viewport.height - line_height
    for line in portrait_lines:
        pyglet.text.Label(
            line,
            font_size=font_size,
            x=viewport.x + 4,
            y=y,
            batch=batch,
        )
        y -= line_height

    if theme_state.vignette:
        depth = _VIGNETTE_DEPTH
        dark = (0, 0, 0, 160)
        # Bottom strip
        pyglet.shapes.Rectangle(
            viewport.x, viewport.y, viewport.width, depth,
            color=dark, batch=batch,
        )
        # Top strip
        pyglet.shapes.Rectangle(
            viewport.x, viewport.y + viewport.height - depth,
            viewport.width, depth, color=dark, batch=batch,
        )
        # Left strip
        pyglet.shapes.Rectangle(
            viewport.x, viewport.y, depth, viewport.height,
            color=dark, batch=batch,
        )
        # Right strip
        pyglet.shapes.Rectangle(
            viewport.x + viewport.width - depth, viewport.y,
            depth, viewport.height, color=dark, batch=batch,
        )


register("character-pane.default", _draw_character_pane)


# ---------------------------------------------------------------------------
# stats-pane.default
# ---------------------------------------------------------------------------


def _draw_stats_pane(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> None:
    import pyglet  # noqa: PLC0415

    stats: list[dict] = props.get("stats", [])
    enemy_stats = props.get("enemy_stats")
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    y = viewport.y + viewport.height - line_height
    for entry in stats:
        label = entry.get("label", "")
        value = entry.get("value", "")
        # Label — left-aligned
        pyglet.text.Label(
            label,
            font_size=font_size,
            x=viewport.x + 8,
            y=y,
            batch=batch,
        )
        # Value — right-aligned
        pyglet.text.Label(
            value,
            font_size=font_size,
            x=viewport.x + viewport.width - 8,
            y=y,
            anchor_x="right",
            batch=batch,
        )
        y -= line_height

    if enemy_stats:
        y -= line_height // 2
        pyglet.text.Label(
            "─" * 20,
            font_size=font_size,
            x=viewport.x + 8,
            y=y,
            batch=batch,
        )
        y -= line_height
        pyglet.text.Label(
            str(enemy_stats),
            font_size=font_size,
            x=viewport.x + 8,
            y=y,
            width=viewport.width - 16,
            multiline=True,
            batch=batch,
        )


register("stats-pane.default", _draw_stats_pane)
