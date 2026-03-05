"""Golden-file snapshot tests for approved components.

Each approved component is rendered with canonical props and compared
against a `.txt` file in tests/snapshots/. If the golden file does not
exist, the test creates it (first run). To regenerate all golden files
after an intentional render change, set UPDATE_SNAPSHOTS=1:

    UPDATE_SNAPSHOTS=1 python -m pytest tests/test_snapshots.py
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from askee_ds import Loader, Theme, Renderer

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"
TOKENS_DIR = Path(__file__).resolve().parent.parent / "tokens"
SNAPSHOTS_DIR = Path(__file__).resolve().parent / "snapshots"

CANONICAL_PROPS: dict[str, dict] = {
    "breadcrumb.inline": {
        "segments": [
            {"id": "home", "label": "Home"},
            {"id": "clearing", "label": "The Clearing"},
            {"id": "guard", "label": "Guard Post"},
        ],
    },
    "button.icon": {"label": "Star this", "icon": "\u2606"},
    "button.text": {"label": "Submit"},
    "card.simple": {
        "title": "Card Title",
        "body_text": "Body text goes here and may wrap across multiple lines when needed.",
    },
    "character-sheet.compact": {
        "name": "Hero",
        "stats": [
            {"label": "STR", "value": 14},
            {"label": "DEX", "value": 12},
            {"label": "INT", "value": 10},
        ],
    },
    "choice-wheel.inline": {
        "options": [
            {"id": "north", "label": "Go north"},
            {"id": "talk", "label": "Talk to guard"},
            {"id": "lamp", "label": "Take lamp"},
        ],
    },
    "cooldown.row": {
        "abilities": [
            {"label": "Fireball", "turns_left": 3},
            {"label": "Shield", "turns_left": 0},
        ],
    },
    "counter.ammo": {"current": 7, "max": 12, "label": "Arrows"},
    "entity-list.room": {
        "items": [
            {"id": "lamp", "label": "Brass lamp"},
            {"id": "key", "label": "Rusty key"},
        ],
        "npcs": [{"id": "guard", "label": "Guard"}],
    },
    "feedback.error": {
        "message": 'You don\'t see "sword" here. Did you mean "rusty sword"?',
    },
    "feedback.success": {
        "message": "Taken: rusty sword (+1 weapon)",
    },
    "hint-bar.contextual": {
        "hints": [
            {"id": "look", "label": "look"},
            {"id": "go", "label": "go <dir>"},
            {"id": "take", "label": "take <item>"},
        ],
        "prefix": "Commands: ",
    },
    "inventory.list": {
        "items": [
            {"id": "sword", "label": "Rusty sword"},
            {"id": "lamp", "label": "Brass lamp"},
            {"id": "key", "label": "Key"},
        ],
    },
    "layout.stack": {
        "blocks": ["Status bar content", "Main content area"],
    },
    "layout.two-column": {
        "left_content": "Nav item 1\nNav item 2",
        "right_content": "Content area\nMore content",
        "left_width": 15,
    },
    "menu.main": {
        "title": "Main Menu",
        "items": [
            {"id": "new", "label": "New Game"},
            {"id": "load", "label": "Load Game"},
            {"id": "quit", "label": "Quit"},
        ],
    },
    "minimap.default": {
        "grid": [[".", ".", "#"], [".", "P", "#"], [".", ".", "."]],
        "legend_entries": [
            {"char": ".", "label": "empty"},
            {"char": "#", "label": "wall"},
            {"char": "P", "label": "you"},
        ],
        "player_position": "1,1",
    },
    "narrative-log.pane": {
        "lines": [
            "You enter the clearing.",
            "The guard watches silently.",
        ],
        "max_visible": 10,
    },
    "nav.vertical": {
        "items": [
            {"id": "inv", "label": "Inventory"},
            {"id": "map", "label": "Map"},
            {"id": "settings", "label": "Settings"},
        ],
        "active_id": "inv",
    },
    "room-card.default": {
        "title": "The Clearing",
        "description_text": "A sun-dappled clearing surrounded by ancient oaks.",
        "items": [
            {"id": "lamp", "label": "Brass lamp"},
            {"id": "key", "label": "Rusty key"},
        ],
        "npcs": [
            {"id": "guard", "label": "Guard"},
        ],
        "exits": [
            {"id": "north", "label": "North"},
            {"id": "east", "label": "East"},
        ],
    },
    "speech-bubble": {
        "text": "The guard nods. \"Go north.\"",
        "tail": "left",
    },
    "status-bar.default": {
        "hp_current": 85,
        "hp_max": 100,
        "location": "The Clearing",
        "turn_count": 12,
    },
    "tracker.objective": {
        "objectives": [
            {"id": "key", "label": "Find the key", "checked": False},
            {"id": "guard", "label": "Talk to the guard", "checked": True},
            {"id": "door", "label": "Open the door", "checked": False},
        ],
    },
    "typography.banner": {
        "text": "QUEST",
    },
}

UPDATE = os.environ.get("UPDATE_SNAPSHOTS", "").strip() in ("1", "true", "yes")


@pytest.fixture(scope="module")
def renderer():
    loader = Loader()
    tokens = loader.load_tokens_dir(TOKENS_DIR)
    return Renderer(Theme(tokens))


@pytest.fixture(scope="module")
def components():
    loader = Loader()
    return loader.load_components_dir(COMPONENTS_DIR)


def _golden_path(name: str) -> Path:
    return SNAPSHOTS_DIR / f"{name}.txt"


@pytest.mark.parametrize("name", sorted(CANONICAL_PROPS.keys()))
def test_snapshot(name: str, renderer, components):
    comp = components[name]
    # typography.banner uses pyfiglet when available, which can vary by environment.
    # Force fallback art so the snapshot is deterministic with or without pyfiglet.
    if name == "typography.banner":
        with patch("askee_ds.banner.render_banner_text", return_value=None):
            output = renderer.render(comp, CANONICAL_PROPS[name])
    else:
        output = renderer.render(comp, CANONICAL_PROPS[name])
    golden = _golden_path(name)
    if UPDATE or not golden.exists():
        golden.write_text(output, encoding="utf-8")
        pytest.skip(f"Golden file created: {golden.name}")
    expected = golden.read_text(encoding="utf-8")
    assert output == expected, (
        f"Snapshot mismatch for {name}. "
        f"Run with UPDATE_SNAPSHOTS=1 to update."
    )
