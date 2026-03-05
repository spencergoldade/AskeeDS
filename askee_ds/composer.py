"""
Compose AskeeDS layout components from child component trees.

The Composer renders children bottom-up and passes the resulting strings
as props to layout components. This turns flat render calls into composed
full-screen UIs.

    from askee_ds import Loader, Theme, Renderer, Composer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    composer = Composer(renderer, components)

    output = composer.compose("layout.stack", {
        "blocks": [
            ("status-bar.default", {"hp_current": 85, "hp_max": 100,
                                    "location": "Cavern", "turn_count": 5}),
            ("room-card.default",  {"title": "Cavern", ...}),
            ("command-input.default", {"prompt": ">"}),
        ],
    })
"""

from __future__ import annotations

from .loader import Component
from .renderer import Renderer


class Composer:

    def __init__(self, renderer: Renderer, components: dict[str, Component]):
        self.renderer = renderer
        self.components = components

    def compose(self, layout_name: str, slots: dict) -> str:
        """Render a layout component with child components in its slots.

        Each slot value can be:
        - A string (passed through as-is)
        - A tuple of (component_name, props_dict) to render
        - A list of the above (for array-typed slots like 'blocks')
        """
        comp = self.components.get(layout_name)
        if comp is None:
            raise ValueError(f"Unknown component: {layout_name!r}")
        resolved: dict = {}
        for key, value in slots.items():
            resolved[key] = self._resolve(value)
        return self.renderer.render(comp, resolved)

    def _resolve(self, value: object) -> object:
        if isinstance(value, str):
            return value
        if isinstance(value, tuple) and len(value) == 2:
            name, props = value
            if isinstance(name, str) and isinstance(props, dict):
                child = self.components.get(name)
                if child is None:
                    raise ValueError(f"Unknown component: {name!r}")
                child_props = {k: self._resolve(v) for k, v in props.items()}
                return self.renderer.render(child, child_props)
        if isinstance(value, list):
            return [self._resolve(item) for item in value]
        return value
