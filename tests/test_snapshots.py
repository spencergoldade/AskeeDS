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
    "status-bar.default": {
        "hp_current": 85,
        "hp_max": 100,
        "location": "The Clearing",
        "turn_count": 12,
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
