"""Render type registry — maps type names to render functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..loader import Component
    from ..theme import Theme


RenderFunc = Callable[["dict", "dict", "RenderContext"], str]


@dataclass
class RenderContext:
    """Everything a render function needs beyond spec and props."""
    theme: "Theme"
    component: "Component"
    decorations: dict[str, dict]


_registry: dict[str, RenderFunc] = {}


def register(name: str, func: RenderFunc) -> None:
    """Register a render type function by name."""
    _registry[name] = func


def get(name: str) -> RenderFunc | None:
    """Look up a render type function. Returns None if not found."""
    return _registry.get(name)


def list_types() -> list[str]:
    """Return sorted list of all registered render type names."""
    return sorted(_registry.keys())
