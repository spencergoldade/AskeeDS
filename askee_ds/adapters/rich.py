"""
Rich adapter — apply Theme color roles to rendered AskeeDS output.

Turns plain ASCII text into Rich Text objects with ANSI colors based on
the component's color role. Box-drawing characters get the border color,
content text gets the foreground color, and highlighted tokens get the
accent color.

    from askee_ds import Loader, Theme, Renderer
    from askee_ds.adapters.rich import RichAdapter
    from rich.console import Console

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    adapter = RichAdapter(theme)

    ascii_output = renderer.render(components["room-card.default"], {...})
    rich_text = adapter.colorize(ascii_output, "dungeon")
    Console().print(rich_text)

Requires: pip install rich  (or pip install askee-ds[rich])
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..theme import Theme

try:
    from rich.text import Text
except ImportError:
    Text = None  # type: ignore[assignment,misc]

_BOX_CHARS = set("+-|┌┐└┘├┤┬┴┼─│═║╔╗╚╝╠╣╦╩╬━┃┏┓┗┛┣┫┳┻╋")
_HIGHLIGHT_RE = re.compile(
    r"(\[x\]|\[ \]|HP:|MP:|Stamina|Turn \d+|Exits?:|Items?:|NPCs?:|>)"
)


class RichAdapter:
    """Apply Theme color roles to rendered ASCII output using Rich."""

    def __init__(self, theme: "Theme"):
        if Text is None:
            raise RuntimeError(
                "Rich is required for the RichAdapter. "
                "Install with: pip install askee-ds[rich]"
            )
        self.theme = theme

    def colorize(self, text: str, color_role: str = "neutral") -> "Text":
        """Convert plain ASCII to a Rich Text with themed colors.

        Args:
            text: Rendered ASCII output from the Renderer or Composer.
            color_role: Theme color role name (e.g. "neutral", "danger",
                "dungeon"). Falls back to "neutral" if not found.

        Returns:
            A Rich Text object ready for Console.print().
        """
        palette = self.theme.colors(color_role)
        fg = palette.get("fg", "#d4d4d4")
        border_color = palette.get("border", "#404040")
        accent = palette.get("accent", fg)
        bg = palette.get("bg", "")

        result = Text()
        style_bg = f" on {bg}" if bg else ""

        for line_idx, line in enumerate(text.splitlines()):
            if line_idx > 0:
                result.append("\n")
            i = 0
            while i < len(line):
                match = _HIGHLIGHT_RE.search(line, i)
                if match and match.start() == i:
                    result.append(match.group(), style=f"bold {accent}{style_bg}")
                    i = match.end()
                    continue
                if match:
                    end = match.start()
                else:
                    end = len(line)
                segment = line[i:end]
                for ch in segment:
                    if ch in _BOX_CHARS:
                        result.append(ch, style=f"{border_color}{style_bg}")
                    else:
                        result.append(ch, style=f"{fg}{style_bg}")
                i = end

        return result

    def render_component(
        self,
        renderer: object,
        component: object,
        props: dict,
        color_role: str | None = None,
    ) -> "Text":
        """Render a component and colorize in one step.

        Args:
            renderer: An askee_ds.Renderer instance.
            component: A Component object.
            props: Props dict for the component.
            color_role: Override color role. If None, uses component.color_hint.

        Returns:
            A Rich Text object.
        """
        from ..renderer import Renderer
        from ..loader import Component

        assert isinstance(renderer, Renderer)
        assert isinstance(component, Component)

        ascii_out = renderer.render(component, props)
        role = color_role or getattr(component, "default_color_role", "neutral")
        return self.colorize(ascii_out, role)
