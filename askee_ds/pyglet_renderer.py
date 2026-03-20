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
