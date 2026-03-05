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

from pathlib import Path

import yaml

from .loader import Component
from .renderer import Renderer


class Composer:

    def __init__(self, renderer: Renderer, components: dict[str, Component]):
        self.renderer = renderer
        self.components = components

    def compose(
        self,
        layout_name: str,
        slots: dict,
        *,
        available_width: int = 80,
        available_height: int | None = None,
    ) -> str:
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
            resolved[key] = self._resolve(value, available_width=available_width)
        return self.renderer.render(
            comp, resolved,
            available_width=available_width,
            available_height=available_height,
        )

    def compose_screen(
        self,
        screen_path: str | Path,
        *,
        available_width: int | None = None,
        available_height: int | None = None,
    ) -> str:
        """Load and render a screen from a YAML file.

        A screen YAML file declares a layout component and fills its slots
        with component references (with props), nested layouts, or plain text.

        Args:
            screen_path: Path to the screen YAML file.
            available_width: Override the screen's declared width.
            available_height: Override the screen's declared height.
        """
        text = Path(screen_path).read_text(encoding="utf-8")
        screen = yaml.safe_load(text) or {}

        layout = screen.get("layout")
        if not layout:
            raise ValueError(f"Screen {screen_path} missing 'layout' field")

        width = available_width or screen.get("available_width", 80)
        height = available_height or screen.get("available_height")

        raw_slots = screen.get("slots", {})
        resolved = self._resolve_screen_slots(raw_slots, available_width=width)

        return self.compose(
            layout, resolved,
            available_width=width,
            available_height=height,
        )

    def _resolve_screen_slots(
        self, slots_def: dict, *, available_width: int = 80,
    ) -> dict:
        """Recursively resolve screen slot definitions into renderable data."""
        resolved: dict = {}
        for key, value in slots_def.items():
            if isinstance(value, list):
                resolved[key] = [
                    self._resolve_screen_entry(item, available_width=available_width)
                    for item in value
                ]
            elif isinstance(value, dict):
                resolved[key] = self._resolve_screen_entry(
                    value, available_width=available_width,
                )
            else:
                resolved[key] = value
        return resolved

    def _resolve_screen_entry(
        self, entry: object, *, available_width: int = 80,
    ) -> object:
        """Resolve a single screen entry (component ref, nested layout, or text)."""
        if isinstance(entry, str):
            return entry
        if not isinstance(entry, dict):
            return str(entry)

        if "text" in entry:
            return entry["text"]

        comp_name = entry.get("component")
        if comp_name is None:
            return str(entry)

        comp = self.components.get(comp_name)
        if comp is None:
            raise ValueError(f"Unknown component in screen: {comp_name!r}")

        if "slots" in entry:
            inner_slots = self._resolve_screen_slots(
                entry["slots"], available_width=available_width,
            )
            return self.compose(
                comp_name, inner_slots, available_width=available_width,
            )

        props = entry.get("props", {})
        return self.renderer.render(
            comp, props, available_width=available_width,
        )

    def _resolve(self, value: object, *, available_width: int = 80) -> object:
        if isinstance(value, str):
            return value
        if isinstance(value, tuple) and len(value) == 2:
            name, props = value
            if isinstance(name, str) and isinstance(props, dict):
                child = self.components.get(name)
                if child is None:
                    raise ValueError(f"Unknown component: {name!r}")
                child_props = {
                    k: self._resolve(v, available_width=available_width)
                    for k, v in props.items()
                }
                return self.renderer.render(
                    child, child_props, available_width=available_width,
                )
        if isinstance(value, list):
            return [
                self._resolve(item, available_width=available_width)
                for item in value
            ]
        return value
