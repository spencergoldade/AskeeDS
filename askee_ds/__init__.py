"""
AskeeDS — ASCII design system and component framework for TUI games.

Framework API (new):
    from askee_ds import Loader, Theme, Renderer, Validator

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    print(renderer.render(components["room-card.default"], {...}))

    validator = Validator.from_schema_file("components/_schema.yaml")
    errors = validator.validate_all(components)

Legacy parsers (still available):
    from askee_ds import components, decorations, maps, box_drawing
"""

from .loader import Component, Loader, PropDef
from .renderer import Renderer
from .theme import Theme
from .validator import Validator

# Legacy modules kept for backward compatibility
from . import box_drawing, components, decorations, maps  # noqa: F401

__all__ = [
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
