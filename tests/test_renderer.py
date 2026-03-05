"""Tests for the AskeeDS Renderer and all render types."""

from pathlib import Path

from askee_ds import Loader

ROOT = Path(__file__).resolve().parent.parent
TOKENS_DIR = ROOT / "tokens"


def test_render_inline(renderer, components):
    output = renderer.render(
        components["button.icon"], {"icon": "☆", "label": "Star"}
    )
    assert "☆" in output
    assert "Star" in output


def test_render_join(renderer, components):
    output = renderer.render(
        components["breadcrumb.inline"],
        {"segments": [{"label": "Home"}, {"label": "Room"}]},
    )
    assert "Home" in output
    assert "Room" in output


def test_render_box(renderer, components):
    output = renderer.render(
        components["status-bar.default"],
        {"hp_current": 85, "hp_max": 100, "location": "The Clearing", "turn_count": 12},
    )
    assert "85" in output
    assert "The Clearing" in output
    lines = output.strip().split("\n")
    assert len(lines) >= 3


def test_render_box_with_list_section(renderer, components):
    output = renderer.render(
        components["room-card.default"],
        {
            "title": "Cavern",
            "description_text": "A dark cavern.",
            "items": [{"label": "torch"}],
            "npcs": [],
            "exits": [{"id": "n", "label": "north"}],
        },
    )
    assert "Cavern" in output
    assert "torch" in output
    assert "north" in output


def test_render_reference_returns_art(renderer, components):
    comp = components["layout.app.shell"]
    output = renderer.render(comp, {})
    assert len(output) > 0


def test_render_all_non_reference_components(renderer, components):
    """Every component with a declarative render spec should render without exceptions."""
    errors = []
    for name, comp in sorted(components.items()):
        rtype = comp.render.get("type", "reference")
        if rtype == "reference":
            continue
        try:
            renderer.render(comp, {})
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    assert errors == [], "Render failures:\n" + "\n".join(errors)


def test_render_checked_list(renderer, components):
    output = renderer.render(
        components["tracker.objective"],
        {
            "objectives": [
                {"label": "Find key", "checked": True},
                {"label": "Open door", "checked": False},
            ]
        },
    )
    assert "[x]" in output
    assert "[ ]" in output
    assert "Find key" in output


def test_render_active_list(renderer, components):
    output = renderer.render(
        components["nav.vertical"],
        {
            "items": [
                {"id": "inv", "label": "Inventory"},
                {"id": "map", "label": "Map"},
                {"id": "settings", "label": "Settings"},
            ],
            "active_id": "settings",
        },
    )
    assert "> Settings" in output
    assert "> Inventory" not in output
    assert "Inventory" in output


def test_render_clock(renderer, components):
    output = renderer.render(
        components["tracker.clock"],
        {"label": "Quest", "segments": 4, "filled": 2},
    )
    assert "Quest" in output
    assert "●●○○" in output
    assert "2 / 4" in output


def test_render_stage_track(renderer, components):
    output = renderer.render(
        components["tracker.front"],
        {
            "label": "Invasion",
            "stages": [
                {"id": "safe", "label": "Safe"},
                {"id": "war", "label": "War"},
            ],
            "current_stage_index": 0,
        },
    )
    assert "Invasion:" in output
    assert "[ Safe ]" in output
    assert "[ War ]" in output
    assert "^" in output


def test_render_banner_fallback(renderer, components):
    output = renderer.render(components["typography.banner"], {"text": "TEST"})
    assert len(output) > 0


def test_render_frames(renderer, components):
    output = renderer.render(
        components["spinner.loading"], {"frames": ["|", "/", "-", "\\"]}
    )
    assert output == "|"


def test_render_frames_empty(renderer, components):
    output = renderer.render(components["spinner.loading"], {"frames": []})
    assert output == ""


def test_render_table(renderer, components):
    output = renderer.render(
        components["table.fourcolumn"],
        {"columns": ["Name", "Level"], "rows": [["Hero", "5"], ["Mage", "3"]]},
    )
    assert "Name" in output
    assert "Hero" in output
    assert "+" in output
    lines = output.strip().split("\n")
    assert len(lines) == 6


def test_render_bubble_left(renderer, components):
    output = renderer.render(
        components["speech-bubble"],
        {"text": "Hello there.", "speaker_id": "npc", "tail": "left"},
    )
    assert "/" in output
    assert "Hello there." in output


def test_render_bubble_right(renderer, components):
    output = renderer.render(
        components["speech-bubble"],
        {"text": "Goodbye.", "tail": "right"},
    )
    assert "\\" in output
    assert "Goodbye." in output


def test_render_tree(renderer, components):
    output = renderer.render(
        components["tree.compact"],
        {
            "nodes": [
                {
                    "id": "a",
                    "label": "Root",
                    "children": [
                        {"id": "b", "label": "Child", "children": []},
                    ],
                },
            ],
        },
    )
    assert "Root" in output
    assert "Child" in output
    assert "\u2514" in output


def test_render_grid(renderer, components):
    output = renderer.render(
        components["inventory.grid"],
        {
            "slots": [
                {"id": "1", "label": "Sword"},
                {"id": "2", "label": "Shield"},
            ],
            "columns": 2,
        },
    )
    assert "Sword" in output
    assert "Shield" in output
    assert "+" in output


def test_render_charmap(renderer, components):
    output = renderer.render(
        components["minimap.default"],
        {
            "grid": [list("..#"), list(".P.")],
            "legend_entries": [{"char": ".", "label": "floor"}],
            "player_position": "1,1",
        },
    )
    assert "P" in output
    assert ". floor" in output


def test_render_art_lookup_fallback(renderer):
    from askee_ds.loader import Component

    comp = Component(
        name="test.art-fallback",
        category="core",
        status="approved",
        description="Art lookup fallback test",
        props={"art_id": {"type": "string"}},
        render={"type": "art_lookup"},
        art="fallback art",
    )
    output = renderer.render(comp, {"art_id": "nonexistent.thing"})
    assert "fallback art" in output


def test_render_art_lookup_with_decorations_dict():
    from askee_ds import Theme, Renderer
    from askee_ds.loader import Component

    decos = {
        "test.art": {
            "art": ".-====-.\n|      |\n'------'",
        },
    }
    r = Renderer(
        Theme(Loader().load_tokens_dir(TOKENS_DIR)),
        decorations=decos,
    )
    comp = Component(
        name="test.art-decos",
        category="core",
        status="approved",
        description="Art lookup with decorations",
        props={"art_id": {"type": "string"}, "width": {"type": "integer"}, "height": {"type": "integer"}},
        render={"type": "art_lookup"},
        art="fallback",
    )
    output = r.render(comp, {"art_id": "test.art", "width": 20, "height": 6})
    assert ".-====-." in output
    lines = output.splitlines()
    assert len(lines) == 6
    assert all(len(ln) == 20 for ln in lines)


def test_render_bars(renderer, components):
    output = renderer.render(
        components["character-sheet.compact"],
        {
            "name": "Hero",
            "stats": [
                {"label": "HP", "current": 8, "max": 10},
                {"label": "MP", "current": 3, "max": 5},
            ],
        },
    )
    assert "Hero" in output


def test_render_stack(renderer, components):
    output = renderer.render(
        components["layout.stack"],
        {"blocks": ["line one", "line two\nline three"]},
    )
    assert "line one" in output
    assert "line three" in output
    assert "+" in output


def test_render_columns(renderer, components):
    output = renderer.render(
        components["layout.two-column"],
        {"left_content": "left\nstuff", "right_content": "right\ncontent", "left_width": 10},
    )
    assert "left" in output
    assert "right" in output
    lines = output.splitlines()
    assert len(lines) >= 3


def test_render_shell(renderer, components):
    output = renderer.render(
        components["layout.app.shell"],
        {
            "header": "My App",
            "sidebar": "Nav 1\nNav 2",
            "content": "Main content\nhere",
            "sidebar_width": 10,
        },
    )
    assert "My App" in output
    assert "Nav 1" in output
    assert "Main content" in output
