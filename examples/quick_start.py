"""
AskeeDS quick-start — load a component, render it, print it.

    python examples/quick_start.py
"""

from askee_ds import Loader, Theme, Renderer

loader = Loader()
components = loader.load_components_dir("components/")
tokens = loader.load_tokens_dir("tokens/")
theme = Theme(tokens)
renderer = Renderer(theme)

print(renderer.render(components["room-card.default"], {
    "title": "The Clearing",
    "description_text": "Sunlight filters through the canopy.",
    "items": [{"label": "old map"}, {"label": "rusty key"}],
    "npcs": [{"label": "a tired merchant"}],
    "exits": [{"id": "n", "label": "north"}, {"id": "e", "label": "east"}],
}))
