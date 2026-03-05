"""
AskeeDS full-screen composition — build a game UI from nested components.

Demonstrates the Composer rendering child components into layout slots,
producing a complete game screen from a single compose() call.

    python examples/full_screen.py
"""

from askee_ds import Loader, Theme, Renderer, Composer

loader = Loader()
components = loader.load_components_dir("components/")
tokens = loader.load_tokens_dir("tokens/")
theme = Theme(tokens)
renderer = Renderer(theme)
composer = Composer(renderer, components)

# -- Build a full game screen using layout.app.shell -------------------------

print(composer.compose("layout.app.shell", {
    "header": ("status-bar.default", {
        "hp_current": 73,
        "hp_max": 100,
        "location": "The Undercroft",
        "turn_count": 42,
    }),
    "sidebar": ("nav.vertical", {
        "items": [
            {"label": "Inventory", "active": False},
            {"label": "Map", "active": False},
            {"label": "Quests", "active": True},
            {"label": "Character", "active": False},
        ],
        "active_index": 2,
    }),
    "content": ("room-card.default", {
        "title": "The Undercroft",
        "description_text": (
            "A low-ceilinged stone chamber. Water drips from the walls "
            "and the air smells of damp earth."
        ),
        "items": [{"label": "rusty key"}, {"label": "torch (lit)"}],
        "npcs": [{"label": "hooded figure"}],
        "exits": [{"id": "n", "label": "north"}, {"id": "e", "label": "east"}],
    }),
    "sidebar_width": 16,
}))

print()

# -- Build a stacked layout --------------------------------------------------

print(composer.compose("layout.stack", {
    "blocks": [
        ("status-bar.default", {
            "hp_current": 73,
            "hp_max": 100,
            "location": "The Undercroft",
            "turn_count": 42,
        }),
        ("room-card.default", {
            "title": "The Undercroft",
            "description_text": "A low-ceilinged stone chamber.",
            "items": [{"label": "rusty key"}],
            "npcs": [],
            "exits": [{"id": "n", "label": "north"}],
        }),
        ("command-input.default", {"prompt": ">"}),
    ],
}))
