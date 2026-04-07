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

from collections.abc import Callable
from typing import Any

from .loader import Component
from .theme import Theme

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

# Monospaced font family in preference order. Pyglet tries each name and uses
# the first one the OS can resolve. All choices have full box-drawing, block
# element, and line-drawing glyph coverage. Never rely on the generic
# "monospace" alias — it resolves inconsistently across platforms.
FONT_FAMILY: tuple[str, ...] = (
    "Menlo",
    "Monaco",
    "DejaVu Sans Mono",
    "Liberation Mono",
    "Noto Sans Mono",
)

# Per-pane cursor blink state: pane_id → cursor_visible (bool)
# NOTE: Tests that register draw functions must call reload(pr) to reset this
# dict between test runs, same as _REGISTRY.
_CURSOR_STATE: dict[str, bool] = {}


def _resolve_font_size(component: Component) -> int:
    return FONT_SIZES.get(component.font_size, _DEFAULT_FONT_SIZE)


def _label(text: str, *, font_size: int, **kwargs: Any) -> Any:
    """Create a pyglet.text.Label with project font defaults."""
    import pyglet  # noqa: PLC0415

    return pyglet.text.Label(
        text, font_name=FONT_FAMILY, font_size=font_size, **kwargs
    )


def _parse_tint(tint: str) -> tuple[int, int, int, int]:
    """Parse a hex colour token to an RGBA tuple. Falls back to white."""
    if tint and tint.startswith("#") and len(tint) == 7:
        try:
            r = int(tint[1:3], 16)
            g = int(tint[3:5], 16)
            b = int(tint[5:7], 16)
            return (r, g, b, 255)
        except ValueError:
            pass
    return (255, 255, 255, 255)


def _parse_hex(hex_str: str) -> tuple[int, int, int, int]:
    """Convert '#rrggbb' to (r, g, b, 255). Falls back to white."""
    if hex_str and hex_str.startswith("#") and len(hex_str) == 7:
        try:
            r = int(hex_str[1:3], 16)
            g = int(hex_str[3:5], 16)
            b = int(hex_str[5:7], 16)
            return (r, g, b, 255)
        except ValueError:
            pass
    return (255, 255, 255, 255)


def _lighten(
    rgba: tuple[int, int, int, int], amount: int
) -> tuple[int, int, int, int]:
    """Add amount to each RGB channel, clamped at 255. Alpha stays 255."""
    return (
        min(rgba[0] + amount, 255),
        min(rgba[1] + amount, 255),
        min(rgba[2] + amount, 255),
        255,
    )


def _dim_color(
    rgba: tuple[int, int, int, int], factor: float
) -> tuple[int, int, int, int]:
    """Multiply each RGB channel by factor. Alpha stays 255."""
    return (
        int(rgba[0] * factor),
        int(rgba[1] * factor),
        int(rgba[2] * factor),
        255,
    )


# ---------------------------------------------------------------------------
# Theme integration
# ---------------------------------------------------------------------------

_THEME: Theme | None = None

_FALLBACK_PALETTE: dict[str, tuple[int, int, int, int]] = {
    "bg": (30, 30, 30, 255),
    "bg_secondary": (37, 37, 37, 255),
    "fg": (212, 212, 212, 255),
    "fg_dim": (159, 159, 159, 255),
    "fg_muted": (117, 117, 117, 255),
    "border": (64, 64, 64, 255),
    "accent": (86, 156, 214, 255),
}


def set_theme(theme: Theme) -> None:
    """Set the module-level Theme used by all draw functions."""
    global _THEME  # noqa: PLW0603
    _THEME = theme


def _resolve_palette(
    theme_state: Any,  # noqa: ARG001
) -> dict[str, tuple[int, int, int, int]]:
    """Resolve the current theme state to a concrete RGBA palette dict."""
    if _THEME is None:
        return _FALLBACK_PALETTE

    colors = _THEME.colors("neutral")
    bg = _parse_hex(colors.get("bg", "#1e1e1e"))
    fg = _parse_hex(colors.get("fg", "#d4d4d4"))
    border = _parse_hex(colors.get("border", "#404040"))
    accent = _parse_hex(colors.get("accent", "#569cd6"))

    return {
        "bg": bg,
        "bg_secondary": _lighten(bg, 7),
        "fg": fg,
        "fg_dim": _dim_color(fg, 0.75),
        "fg_muted": _dim_color(fg, 0.55),
        "border": border,
        "accent": accent,
    }


# ---------------------------------------------------------------------------
# Column mapping and pane chrome
# ---------------------------------------------------------------------------

_COLUMN_MAP: dict[str, str] = {
    "location-header.default": "left",
    "room-description.default": "left",
    "minimap.default": "left",
    "history-pane.default": "middle",
    "input-pane.default": "middle",
    "stats-pane.default": "right",
    "combat-card.enemy": "right",
    "combat-card.actions": "right",
    "inventory.grid": "right",
    "inventory.list": "right",
    "merchant.stock-grid": "right",
    "menu.main": "full",
    "typography.banner": "full",
    "modal.overlay": "full",
    "reading.book": "full",
    "screen.placeholder": "full",
    "character-pane.default": "right",
    "speech-bubble.left": "middle",
    "choice-wheel.inline": "middle",
}


def _pane_chrome(
    component_name: str,
    palette: dict[str, tuple[int, int, int, int]],
    viewport: Any,
    batch: Any,
) -> list[Any]:
    """Return background rectangle + optional separator for a pane."""
    import pyglet  # noqa: PLC0415

    column = _COLUMN_MAP.get(component_name, "middle")
    is_side = column in ("left", "right")
    bg_color = palette["bg_secondary"] if is_side else palette["bg"]

    drawables: list[Any] = [
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=bg_color,
            batch=batch,
        ),
    ]

    if column == "left":
        drawables.append(
            pyglet.shapes.Rectangle(
                viewport.x + viewport.width - 1,
                viewport.y,
                1,
                viewport.height,
                color=palette["border"],
                batch=batch,
            )
        )
    elif column == "right":
        drawables.append(
            pyglet.shapes.Rectangle(
                viewport.x,
                viewport.y,
                1,
                viewport.height,
                color=palette["border"],
                batch=batch,
            )
        )

    return drawables


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_DrawFn = Callable[[Component, dict, Any, Any, Any, str], list[Any]]
#                   component  props  theme  viewport batch  pane_id  -> drawables

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
) -> list[Any]:
    """Draw a component pane into a Pyglet batch.

    Dispatches to the registered draw function for component.name, or to
    _draw_fallback if no draw function is registered.

    Returns a list of every Pyglet object created (Labels, Rectangles, etc.).
    Callers **must** keep this list alive until ``batch.draw()`` has been
    called; CPython's reference counting will otherwise destroy the objects
    (and their vertex lists) before the batch renders them.

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
    return fn(component, props, theme_state, viewport, batch, pane_id)


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
) -> list[Any]:
    """Render a greyed-out placeholder label for unregistered components."""
    return [
        _label(
            f"[{component.name}]",
            font_size=_resolve_font_size(component),
            x=viewport.x,
            y=viewport.y + viewport.height - 8,
            anchor_y="top",
            color=(120, 120, 120, 255),
            batch=batch,
        ),
    ]


# ---------------------------------------------------------------------------
# location-header.default
# ---------------------------------------------------------------------------


def _draw_location_header(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    location_name: str = props.get("location_name", "")
    font_size = _resolve_font_size(component)

    return [
        _label(
            location_name,
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - 8,
            anchor_y="top",
            width=viewport.width - 16,
            batch=batch,
        ),
    ]


register("location-header.default", _draw_location_header)


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
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    lines: list[str] = props.get("lines", [])
    max_lines: int = props.get("max_lines", 20)
    visible = lines[-max_lines:] if len(lines) > max_lines else lines
    font_size = _resolve_font_size(component)

    d: list[Any] = []

    # Background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    if visible:
        text = "\n".join(visible)
        label = _label(
            text,
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - 8,
            anchor_y="top",
            width=viewport.width - 16,
            height=viewport.height - 16,
            multiline=True,
            color=(255, 255, 255, 255),
            batch=batch,
        )
        d.append(label)

    return d


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
) -> list[Any]:
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

    return [
        _label(
            display_text,
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - 8,
            anchor_y="top",
            width=viewport.width - 16,
            batch=batch,
        ),
    ]


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
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    portrait_lines: list[str] = props.get("portrait_lines", [])
    font_size = _resolve_font_size(component)
    line_height = font_size + 2
    tint_color = _parse_tint(theme_state.tint)

    d: list[Any] = []

    y = viewport.y + viewport.height - line_height
    for line in portrait_lines:
        d.append(
            _label(
                line,
                font_size=font_size,
                x=viewport.x + 4,
                y=y,
                color=tint_color,
                batch=batch,
            )
        )
        y -= line_height

    if theme_state.vignette:
        depth = _VIGNETTE_DEPTH
        dark = (0, 0, 0, 160)
        # Bottom strip
        d.append(
            pyglet.shapes.Rectangle(
                viewport.x,
                viewport.y,
                viewport.width,
                depth,
                color=dark,
                batch=batch,
            )
        )
        # Top strip
        d.append(
            pyglet.shapes.Rectangle(
                viewport.x,
                viewport.y + viewport.height - depth,
                viewport.width,
                depth,
                color=dark,
                batch=batch,
            )
        )
        # Left strip
        d.append(
            pyglet.shapes.Rectangle(
                viewport.x,
                viewport.y,
                depth,
                viewport.height,
                color=dark,
                batch=batch,
            )
        )
        # Right strip
        d.append(
            pyglet.shapes.Rectangle(
                viewport.x + viewport.width - depth,
                viewport.y,
                depth,
                viewport.height,
                color=dark,
                batch=batch,
            )
        )

    return d


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
) -> list[Any]:
    stats: list[dict] = props.get("stats", [])
    enemy_stats = props.get("enemy_stats")
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    y = viewport.y + viewport.height - line_height
    for entry in stats:
        label = entry.get("label", "")
        value = entry.get("value", "")
        # Label — left-aligned
        d.append(
            _label(
                label,
                font_size=font_size,
                x=viewport.x + 8,
                y=y,
                batch=batch,
            )
        )
        # Value — right-aligned
        d.append(
            _label(
                value,
                font_size=font_size,
                x=viewport.x + viewport.width - 8,
                y=y,
                anchor_x="right",
                batch=batch,
            )
        )
        y -= line_height

    if enemy_stats:
        y -= line_height // 2
        d.append(
            _label(
                "─" * 20,
                font_size=font_size,
                x=viewport.x + 8,
                y=y,
                batch=batch,
            )
        )
        y -= line_height
        d.append(
            _label(
                str(enemy_stats),
                font_size=font_size,
                x=viewport.x + 8,
                y=y,
                width=viewport.width - 16,
                multiline=True,
                batch=batch,
            )
        )

    return d


register("stats-pane.default", _draw_stats_pane)


# ---------------------------------------------------------------------------
# menu.main
# ---------------------------------------------------------------------------


def _draw_menu_main(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    title: str = props.get("title", "")
    items: list[dict] = props.get("items", [])
    selected_index: int = props.get("selected_index", 0)
    font_size = _resolve_font_size(component)
    line_height = font_size + 6

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # Title centered near top
    d.append(
        _label(
            title,
            font_size=font_size + 4,
            x=viewport.x + viewport.width // 2,
            y=viewport.y + viewport.height - line_height * 2,
            anchor_x="center",
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # Menu items centered below title
    start_y = viewport.y + viewport.height - line_height * 4
    for i, item in enumerate(items):
        label: str = item.get("label", "")
        if i == selected_index:
            display_text = f"> {label}"
            color = (255, 255, 255, 255)
        else:
            display_text = label
            color = (160, 160, 160, 255)
        d.append(
            _label(
                display_text,
                font_size=font_size,
                x=viewport.x + viewport.width // 2,
                y=start_y - i * line_height,
                anchor_x="center",
                color=color,
                batch=batch,
            )
        )

    return d


register("menu.main", _draw_menu_main)


# ---------------------------------------------------------------------------
# typography.banner
# ---------------------------------------------------------------------------


def _draw_typography_banner(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    text: str = props.get("text", "")
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []
    lines = text.split("\n")
    # Center block vertically: start at top and work down
    start_y = viewport.y + viewport.height - line_height
    for i, line in enumerate(lines):
        d.append(
            _label(
                line,
                font_size=font_size,
                x=viewport.x + viewport.width // 2,
                y=start_y - i * line_height,
                anchor_x="center",
                color=(255, 255, 255, 255),
                batch=batch,
            )
        )

    return d


register("typography.banner", _draw_typography_banner)


# ---------------------------------------------------------------------------
# modal.overlay
# ---------------------------------------------------------------------------


def _draw_modal_overlay(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    title: str = props.get("title", "")
    body: str = props.get("body", props.get("body_text", ""))
    actions: list[dict] = props.get("actions", [])
    font_size = _resolve_font_size(component)
    line_height = font_size + 6

    d: list[Any] = []

    # Dimmed semi-transparent background over full viewport
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(0, 0, 0, 160),
            batch=batch,
        )
    )

    # Modal box: 60% width, centered
    box_width = int(viewport.width * 0.6)
    box_height = line_height * (4 + len(actions))
    box_x = viewport.x + (viewport.width - box_width) // 2
    box_y = viewport.y + (viewport.height - box_height) // 2

    d.append(
        pyglet.shapes.Rectangle(
            box_x,
            box_y,
            box_width,
            box_height,
            color=(40, 40, 40, 255),
            batch=batch,
        )
    )

    # Title centered at top of box
    d.append(
        _label(
            title,
            font_size=font_size,
            x=box_x + box_width // 2,
            y=box_y + box_height - line_height,
            anchor_x="center",
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # Body text below title
    d.append(
        _label(
            body,
            font_size=font_size,
            x=box_x + 16,
            y=box_y + box_height - line_height * 2,
            width=box_width - 32,
            multiline=True,
            color=(200, 200, 200, 255),
            batch=batch,
        )
    )

    # Action labels below body
    for i, action in enumerate(actions):
        label: str = action.get("label", "")
        d.append(
            _label(
                label,
                font_size=font_size,
                x=box_x + box_width // 2,
                y=box_y + box_height - line_height * (3 + i),
                anchor_x="center",
                color=(180, 180, 180, 255),
                batch=batch,
            )
        )

    return d


register("modal.overlay", _draw_modal_overlay)


# ---------------------------------------------------------------------------
# HP bar helpers
# ---------------------------------------------------------------------------

_HP_COLOR_GREEN = (80, 220, 80, 255)
_HP_COLOR_YELLOW = (220, 200, 60, 255)
_HP_COLOR_RED = (220, 60, 60, 255)
_HP_COLOR_GREY = (120, 120, 120, 255)

_HP_FILL_CHAR = "█"
_HP_EMPTY_CHAR = "░"
_HP_BAR_SEGMENTS = 8


def _hp_bar_color(current: int, maximum: int) -> tuple[int, int, int, int]:
    """Return an RGBA color tuple based on HP percentage.

    Args:
        current: Current HP value.
        maximum: Maximum HP value.

    Returns:
        RGBA tuple: green above 50%, yellow 25–50%, red below 25%, grey if max <= 0.
    """
    if maximum <= 0:
        return _HP_COLOR_GREY
    pct = current / maximum
    if pct > 0.50:
        return _HP_COLOR_GREEN
    if pct >= 0.25:
        return _HP_COLOR_YELLOW
    return _HP_COLOR_RED


def _draw_hp_bar(
    label: str,
    current: int,
    max_val: int,
    x: int,
    y: int,
    width: int,
    font_size: int,
    batch: Any,
) -> list[Any]:
    """Draw a text-based HP bar: 'Label [████░░░░] current/max'.

    Returns created pyglet objects so the caller can retain them.

    Args:
        label:     Label text placed before the bar (e.g. "Flesh").
        current:   Current HP value.
        max_val:   Maximum HP value.
        x:         Left edge x coordinate.
        y:         Bottom y coordinate.
        width:     Available pixel width (unused by text layout, kept for future use).
        font_size: Font size in pixels.
        batch:     Pyglet batch to draw into.
    """
    color = _hp_bar_color(current, max_val)
    if max_val > 0:
        filled = round(_HP_BAR_SEGMENTS * max(0, current) / max_val)
    else:
        filled = 0
    empty = _HP_BAR_SEGMENTS - filled
    bar = _HP_FILL_CHAR * filled + _HP_EMPTY_CHAR * empty
    text = f"{label} [{bar}] {current}/{max_val}"

    return [
        _label(
            text,
            font_size=font_size,
            x=x,
            y=y,
            width=width,
            color=color,
            batch=batch,
        ),
    ]


# ---------------------------------------------------------------------------
# combat-card.enemy
# ---------------------------------------------------------------------------


def _draw_combat_card_enemy(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    enemy_name: str = props.get("enemy_name", "")
    enemy_hp: int = props.get("enemy_hp", 0)
    enemy_hp_max: int = props.get("enemy_hp_max", 0)
    hp_label: str = props.get("hp_label", "Flesh")
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # Enemy name header
    d.append(
        _label(
            enemy_name,
            font_size=font_size + 2,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # HP bar
    d.extend(
        _draw_hp_bar(
            hp_label,
            enemy_hp,
            enemy_hp_max,
            viewport.x + 8,
            viewport.y + viewport.height - line_height * 2,
            viewport.width - 16,
            font_size,
            batch,
        )
    )

    return d


register("combat-card.enemy", _draw_combat_card_enemy)


# ---------------------------------------------------------------------------
# combat-card.actions
# ---------------------------------------------------------------------------


def _draw_combat_card_actions(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    player_hp: int = props.get("player_hp", 0)
    player_hp_max: int = props.get("player_hp_max", 0)
    round_num: int = props.get("round", 1)
    hp_label: str = props.get("hp_label", "Flesh")
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # Player HP bar
    d.extend(
        _draw_hp_bar(
            hp_label,
            player_hp,
            player_hp_max,
            viewport.x + 8,
            viewport.y + viewport.height - line_height,
            viewport.width - 16,
            font_size,
            batch,
        )
    )

    # Round counter
    d.append(
        _label(
            f"Round {round_num}",
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height * 2,
            width=viewport.width - 16,
            color=(200, 200, 200, 255),
            batch=batch,
        )
    )

    return d


register("combat-card.actions", _draw_combat_card_actions)


# ---------------------------------------------------------------------------
# speech-bubble.left
# ---------------------------------------------------------------------------


def _draw_speech_bubble_left(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    npc_id: str = props.get("npc_id", "")
    npc_speech: str = props.get("npc_speech", "")
    active: bool = props.get("active", True)
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    text_color = (220, 220, 220, 255) if active else (120, 120, 120, 255)

    return [
        # Dark background
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(30, 30, 30, 255),
            batch=batch,
        ),
        # NPC name header
        _label(
            npc_id,
            font_size=font_size + 2,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(255, 255, 255, 255),
            batch=batch,
        ),
        # Speech text (multiline)
        _label(
            npc_speech,
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height * 2,
            width=viewport.width - 16,
            multiline=True,
            color=text_color,
            batch=batch,
        ),
    ]


register("speech-bubble.left", _draw_speech_bubble_left)


# ---------------------------------------------------------------------------
# choice-wheel.inline
# ---------------------------------------------------------------------------


def _draw_choice_wheel_inline(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    options: list[dict] = props.get("options", [])
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(25, 25, 25, 255),
            batch=batch,
        )
    )

    # "Choose:" header
    d.append(
        _label(
            "Choose:",
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(160, 160, 160, 255),
            batch=batch,
        )
    )

    # Numbered options
    for i, option in enumerate(options):
        label_text = f"{i + 1}. {option.get('label', '')}"
        d.append(
            _label(
                label_text,
                font_size=font_size,
                x=viewport.x + 16,
                y=viewport.y + viewport.height - line_height * (i + 2),
                width=viewport.width - 32,
                color=(220, 220, 220, 255),
                batch=batch,
            )
        )

    return d


register("choice-wheel.inline", _draw_choice_wheel_inline)


# ---------------------------------------------------------------------------
# merchant.stock-grid
# ---------------------------------------------------------------------------


def _draw_merchant_stock_grid(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    stock: list[dict] = props.get("stock", [])
    player_gold: int = props.get("player_gold", 0)
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # "Stock" header
    d.append(
        _label(
            "Stock",
            font_size=font_size + 2,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # Stock item rows
    for i, item in enumerate(stock):
        row_y = viewport.y + viewport.height - line_height * (i + 2)
        d.append(
            _label(
                item.get("label", ""),
                font_size=font_size,
                x=viewport.x + 8,
                y=row_y,
                width=(viewport.width - 16) // 2,
                color=(200, 200, 200, 255),
                batch=batch,
            )
        )
        d.append(
            _label(
                f"{item.get('price', 0)}g",
                font_size=font_size,
                x=viewport.x + viewport.width // 2,
                y=row_y,
                width=(viewport.width - 16) // 2,
                color=(200, 180, 60, 255),
                batch=batch,
            )
        )

    # Player gold at bottom
    d.append(
        _label(
            f"Gold: {player_gold}",
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + 8,
            width=viewport.width - 16,
            color=(200, 180, 60, 255),
            batch=batch,
        )
    )

    return d


register("merchant.stock-grid", _draw_merchant_stock_grid)


# ---------------------------------------------------------------------------
# inventory.list
# ---------------------------------------------------------------------------


def _draw_inventory_list(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    sellable: list[dict] = props.get("sellable", [])
    player_gold: int = props.get("player_gold", 0)
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # "Your Items" header
    d.append(
        _label(
            "Your Items",
            font_size=font_size + 2,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # Sellable item rows
    for i, item in enumerate(sellable):
        row_y = viewport.y + viewport.height - line_height * (i + 2)
        d.append(
            _label(
                item.get("label", ""),
                font_size=font_size,
                x=viewport.x + 8,
                y=row_y,
                width=(viewport.width - 16) // 2,
                color=(200, 200, 200, 255),
                batch=batch,
            )
        )
        d.append(
            _label(
                f"{item.get('value', 0)}g",
                font_size=font_size,
                x=viewport.x + viewport.width // 2,
                y=row_y,
                width=(viewport.width - 16) // 2,
                color=(200, 180, 60, 255),
                batch=batch,
            )
        )

    # Player gold at bottom
    d.append(
        _label(
            f"Gold: {player_gold}",
            font_size=font_size,
            x=viewport.x + 8,
            y=viewport.y + 8,
            width=viewport.width - 16,
            color=(200, 180, 60, 255),
            batch=batch,
        )
    )

    return d


register("inventory.list", _draw_inventory_list)


# ---------------------------------------------------------------------------
# inventory.grid
# ---------------------------------------------------------------------------


def _draw_inventory_grid(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    items: list[dict] = props.get("items", [])
    selected_index: int = props.get("selected_index", 0)
    font_size = _resolve_font_size(component)
    line_height = font_size + 4

    d: list[Any] = []

    # Dark background
    d.append(
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(20, 20, 20, 255),
            batch=batch,
        )
    )

    # "Inventory" header
    d.append(
        _label(
            "Inventory",
            font_size=font_size + 2,
            x=viewport.x + 8,
            y=viewport.y + viewport.height - line_height,
            width=viewport.width - 16,
            color=(255, 255, 255, 255),
            batch=batch,
        )
    )

    # Item rows with selection indicator
    for i, item in enumerate(items):
        if i == selected_index:
            prefix = "> "
            color = (255, 255, 255, 255)
        else:
            prefix = "  "
            color = (160, 160, 160, 255)
        d.append(
            _label(
                f"{prefix}{item.get('label', '')}",
                font_size=font_size,
                x=viewport.x + 8,
                y=viewport.y + viewport.height - line_height * (i + 2),
                width=viewport.width - 16,
                color=color,
                batch=batch,
            )
        )

    return d


register("inventory.grid", _draw_inventory_grid)


# ---------------------------------------------------------------------------
# reading.book
# ---------------------------------------------------------------------------


def _draw_reading_book(
    component: Component,
    props: dict,
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    import pyglet  # noqa: PLC0415

    title: str = props.get("title", "")
    content: str = props.get("content", "")
    current_page: int = props.get("current_page", 1)
    total_pages: int = props.get("total_pages", 1)
    font_size = _resolve_font_size(component)

    margin = 24
    return [
        # Dark background
        pyglet.shapes.Rectangle(
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            color=(15, 15, 15, 255),
            batch=batch,
        ),
        # Title centred near top
        _label(
            title,
            font_size=font_size + 4,
            x=viewport.x + viewport.width // 2,
            y=viewport.y + viewport.height - (font_size + 4) * 2,
            anchor_x="center",
            color=(255, 255, 255, 255),
            batch=batch,
        ),
        # Content as multiline label with 24px margins
        _label(
            content,
            font_size=font_size,
            x=viewport.x + margin,
            y=viewport.y + viewport.height - (font_size + 4) * 4,
            width=viewport.width - margin * 2,
            multiline=True,
            color=(200, 200, 200, 255),
            batch=batch,
        ),
        # Page indicator centred near bottom
        _label(
            f"Page {current_page}/{total_pages}",
            font_size=font_size,
            x=viewport.x + viewport.width // 2,
            y=viewport.y + (font_size + 4) * 2,
            anchor_x="center",
            color=(160, 160, 160, 255),
            batch=batch,
        ),
        # Navigation hint below page indicator
        _label(
            "next / prev / close",
            font_size=font_size - 2,
            x=viewport.x + viewport.width // 2,
            y=viewport.y + font_size,
            anchor_x="center",
            color=(120, 120, 120, 255),
            batch=batch,
        ),
    ]


register("reading.book", _draw_reading_book)


# ---------------------------------------------------------------------------
# screen.placeholder
# ---------------------------------------------------------------------------


def _draw_screen_placeholder(
    component: Component,
    props: dict,  # noqa: ARG001
    theme_state: Any,  # noqa: ARG001
    viewport: Any,
    batch: Any,
    pane_id: str,  # noqa: ARG001
) -> list[Any]:
    return [
        _label(
            f"[{component.name}]",
            font_size=_resolve_font_size(component),
            x=viewport.x + viewport.width // 2,
            y=viewport.y + viewport.height // 2,
            anchor_x="center",
            anchor_y="center",
            color=(120, 120, 120, 255),
            batch=batch,
        ),
    ]


register("screen.placeholder", _draw_screen_placeholder)
