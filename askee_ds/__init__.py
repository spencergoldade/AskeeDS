"""
AskeeDS — ASCII design system and component framework for TUI games.

Framework API (new):
    from askee_ds import Loader, Theme, Renderer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    print(renderer.render(components["room-card.default"], {...}))

Legacy parsers (still available):
    from askee_ds import components, decorations, maps, box_drawing
"""

from .loader import Component, Loader, PropDef
from .renderer import Renderer
from .theme import Theme

# Legacy modules kept for backward compatibility
from . import box_drawing, components, decorations, maps  # noqa: F401

__all__ = [
    "Component",
    "Loader",
    "PropDef",
    "Renderer",
    "Theme",
    "box_drawing",
    "components",
    "decorations",
    "maps",
]
