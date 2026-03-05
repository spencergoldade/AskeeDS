"""
AskeeDS renderer — component + props + theme = ASCII output.

Takes a Component definition, a props dict, and a Theme, and produces a
rendered ASCII string. The renderer dispatches to registered render type
functions via the render type registry.

    from askee_ds import Loader, Theme, Renderer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    print(renderer.render(components["room-card.default"], {...}))

To register a custom render type:

    from askee_ds.render_types import register

    def my_type(spec, props, ctx):
        return "custom output"

    register("my_type", my_type)
"""

from __future__ import annotations

from .loader import Component
from .theme import Theme
from .render_types import get as _get_render_type, register as _register
from .render_types._registry import RenderContext


class Renderer:

    def __init__(self, theme: Theme, decorations: dict[str, dict] | None = None):
        self.theme = theme
        self._decorations = decorations or {}

    def render(
        self,
        component: Component,
        props: dict,
        *,
        available_width: int = 80,
        available_height: int | None = None,
    ) -> str:
        spec = component.render
        rtype = spec.get("type", "inline")

        render_func = _get_render_type(rtype)
        if render_func is not None:
            ctx = RenderContext(
                theme=self.theme,
                component=component,
                decorations=self._decorations,
                available_width=available_width,
                available_height=available_height,
            )
            return render_func(spec, props, ctx)

        return component.art.rstrip("\n")

    @staticmethod
    def register_type(name: str, func) -> None:
        """Register a custom render type.

        The function receives (spec, props, ctx) and returns a string.
        ctx is a RenderContext with theme, component, and decorations.
        """
        _register(name, func)
