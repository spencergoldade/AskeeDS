"""
AskeeDS Textual demo — a live TUI showing themed components.

Renders several AskeeDS components as Textual widgets with themed ANSI
colors. Press Q to quit.

    pip install askee-ds[textual]
    python examples/textual_app.py
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from askee_ds import Loader, Theme, Renderer, Composer
from askee_ds.adapters.textual import AskeeWidget


class AskeeDemo(App):
    """A Textual app showcasing AskeeDS components."""

    CSS = """
    Screen {
        background: #1e1e1e;
    }
    #sidebar {
        width: 28;
        height: 100%;
    }
    #main {
        width: 1fr;
        height: 100%;
    }
    AskeeWidget {
        margin: 0 1;
        height: auto;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        loader = Loader()
        components = loader.load_components_dir("components/")
        tokens = loader.load_tokens_dir("tokens/")
        theme = Theme(tokens)
        renderer = Renderer(theme)
        composer = Composer(renderer, components)

        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(id="sidebar"):
                yield AskeeWidget.from_component(
                    renderer, components["nav.vertical"],
                    props={
                        "items": [
                            {"label": "Inventory", "active": False},
                            {"label": "Map", "active": False},
                            {"label": "Quests", "active": True},
                            {"label": "Character", "active": False},
                        ],
                        "active_index": 2,
                    },
                    theme=theme,
                    color_role="dungeon",
                )
                yield AskeeWidget.from_component(
                    renderer, components["tracker.objective"],
                    props={"objectives": [
                        {"label": "Find the key", "done": True},
                        {"label": "Talk to the guard", "done": True},
                        {"label": "Open the sealed door", "done": False},
                    ]},
                    theme=theme,
                    color_role="nature",
                )

            with Vertical(id="main"):
                yield AskeeWidget.from_component(
                    renderer, components["status-bar.default"],
                    props={
                        "hp_current": 73,
                        "hp_max": 100,
                        "location": "The Undercroft",
                        "turn_count": 42,
                    },
                    theme=theme,
                    color_role="danger",
                )
                yield AskeeWidget.from_component(
                    renderer, components["room-card.default"],
                    props={
                        "title": "The Undercroft",
                        "description_text": (
                            "A low-ceilinged stone chamber. Water drips "
                            "from the walls and the air smells of damp earth."
                        ),
                        "items": [
                            {"label": "rusty key"},
                            {"label": "torch (lit)"},
                        ],
                        "npcs": [{"label": "hooded figure"}],
                        "exits": [
                            {"id": "n", "label": "north"},
                            {"id": "e", "label": "east"},
                        ],
                    },
                    theme=theme,
                    color_role="dungeon",
                )
                yield AskeeWidget.from_component(
                    renderer, components["command-input.default"],
                    props={"prompt": ">"},
                    theme=theme,
                    color_role="neutral",
                )

        yield Footer()


if __name__ == "__main__":
    AskeeDemo().run()
