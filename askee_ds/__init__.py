"""
AskeeDS — ASCII design system and component framework for TUI games.

    from askee_ds import Loader, Theme, Renderer, Composer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    composer = Composer(renderer, components)

    print(renderer.render(components["room-card.default"], {...}))
    print(composer.compose("layout.stack", {"blocks": [...]}))
"""

from .composer import Composer
from .loader import Component, Loader, PropDef
from .output import RenderOutput
from .renderer import Renderer
from .theme import Theme
from .validator import Validator

__all__ = [
    "Composer",
    "Component",
    "Loader",
    "PropDef",
    "RenderOutput",
    "Renderer",
    "Theme",
    "Validator",
]
