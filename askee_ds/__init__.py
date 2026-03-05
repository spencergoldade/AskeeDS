"""
AskeeDS — ASCII design system and component framework for TUI games.

Framework API:
    from askee_ds import Loader, Theme, Renderer, Composer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    composer = Composer(renderer, components)

    print(renderer.render(components["room-card.default"], {...}))
    print(composer.compose("layout.stack", {"blocks": [...]}))

Legacy parsers (still available):
    from askee_ds import components, decorations, maps, box_drawing
"""

from .composer import Composer
from .loader import Component, Loader, PropDef
from .renderer import Renderer
from .theme import Theme
from .validator import Validator

# Legacy modules kept for backward compatibility
from . import box_drawing, components, decorations, maps  # noqa: F401

__all__ = [
    "Composer",
    "Component",
    "Loader",
    "PropDef",
    "Renderer",
    "Theme",
    "Validator",
    "box_drawing",
    "components",
    "decorations",
    "maps",
]
