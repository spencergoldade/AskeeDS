"""
Textual adapter — render AskeeDS components as Textual widgets.

Wraps the Rich adapter to produce a Static widget with themed ANSI colors.
Can be mounted into any Textual app layout.

    from askee_ds import Loader, Theme, Renderer
    from askee_ds.adapters.textual import AskeeWidget

    class MyApp(App):
        def compose(self):
            loader = Loader()
            components = loader.load_components_dir("components/")
            tokens = loader.load_tokens_dir("tokens/")
            theme = Theme(tokens)
            renderer = Renderer(theme)

            widget = AskeeWidget.from_component(
                renderer, components["room-card.default"],
                props={...}, theme=theme, color_role="dungeon",
            )
            yield widget

Requires: pip install askee-ds[textual]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..loader import Component
    from ..renderer import Renderer
    from ..theme import Theme

try:
    from textual.widgets import Static
    from rich.text import Text
except ImportError:
    Static = None  # type: ignore[assignment,misc]
    Text = None  # type: ignore[assignment,misc]

from .rich import RichAdapter


class AskeeWidget(Static):  # type: ignore[misc]
    """A Textual Static widget displaying themed AskeeDS output."""

    def __init__(
        self,
        content: "Text",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        focusable: bool = False,
    ) -> None:
        if Static is None:
            raise RuntimeError(
                "Textual is required for AskeeWidget. "
                "Install with: pip install askee-ds[textual]"
            )
        super().__init__(content, name=name, id=id, classes=classes)
        self.can_focus = focusable

    @classmethod
    def from_component(
        cls,
        renderer: "Renderer",
        component: "Component",
        props: dict,
        theme: "Theme",
        color_role: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> "AskeeWidget":
        """Render a component and wrap it as a themed Textual widget.

        Args:
            renderer: An askee_ds.Renderer instance.
            component: A Component object to render.
            props: Props dict for the component.
            theme: Theme for color resolution.
            color_role: Override color role. If None, uses component.color_hint.
            name, id, classes: Standard Textual widget kwargs.
        """
        adapter = RichAdapter(theme)
        rich_text = adapter.render_component(
            renderer, component, props, color_role=color_role
        )
        focusable = component.interaction.get("focusable", False)
        return cls(
            rich_text, name=name, id=id, classes=classes, focusable=focusable,
        )

    @classmethod
    def from_text(
        cls,
        text: str,
        theme: "Theme",
        color_role: str = "neutral",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> "AskeeWidget":
        """Wrap pre-rendered ASCII text as a themed Textual widget.

        Args:
            text: Pre-rendered ASCII output (e.g. from Composer).
            theme: Theme for color resolution.
            color_role: Theme color role name.
            name, id, classes: Standard Textual widget kwargs.
        """
        adapter = RichAdapter(theme)
        rich_text = adapter.colorize(text, color_role)
        return cls(rich_text, name=name, id=id, classes=classes)
