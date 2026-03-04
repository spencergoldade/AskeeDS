#!/usr/bin/env python3
"""
AskeeDS component visual test — interactive TUI to review components by status,
browse the library, and test how props affect each component.

Run: python tools/component_visual_test.py (from repo root)
Requires: pip install textual  OR  pip install -e ".[visual-test]"

Use the keyboard to filter by status, search by name, open a component, edit prop
values, and see a live preview. Press Z on the detail screen to randomize prop
values (useful for QA). Session notes are saved under tools/visual_test_notes/
in date-separated files (YYYY-MM-DD.md). No other data is persisted.
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))  # so askee_ds.banner is importable for typography.banner

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import (
        Button,
        Footer,
        Header,
        Input,
        Label,
        OptionList,
        Select,
        Static,
    )
    from textual.screen import Screen, ModalScreen
    from textual import on
except ImportError as e:
    print("Textual is required for the component visual test.", file=sys.stderr)
    print("Install with: pip install textual", file=sys.stderr)
    print("Or from repo: pip install -e \".[visual-test]\"", file=sys.stderr)
    sys.exit(1)

from parse_components import parse_components, parse_props_meta, COMPONENT_STATUSES

COMPONENTS_PATH = ROOT / "design" / "ascii" / "components.txt"
STATUS_OPTIONS = [("All", "All")] + [(s, s) for s in sorted(COMPONENT_STATUSES)]

# Section divider for TUI (horizontal line from box-drawing convention; 60 chars)
SECTION_DIVIDER = "-" * 60

# Session notes: one file per day under tools/visual_test_notes/
NOTES_DIR = ROOT / "tools" / "visual_test_notes"


def append_session_note(component_name: str | None, text: str) -> None:
    """Append a timestamped line to today's notes file. Creates NOTES_DIR if needed."""
    if not text.strip():
        return
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = NOTES_DIR / f"{today}.md"
    ts = datetime.now().strftime("%H:%M")
    prefix = f"- {ts}"
    if component_name:
        prefix += f" [{component_name}]"
    prefix += " "
    line = prefix + text.strip() + "\n"
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        path.write_text(line, encoding="utf-8")


def load_components() -> list[dict]:
    """Load component library from design/ascii/components.txt."""
    if not COMPONENTS_PATH.exists():
        return []
    content = COMPONENTS_PATH.read_text(encoding="utf-8")
    return parse_components(content)


def approved_component_names(components: list[dict] | None = None) -> list[str]:
    """Return component names whose status is Approved. Use when adding explicit
    apply_props_to_art / default_props / randomize support so the tool stays aligned
    with the canonical set."""
    lib = components if components is not None else load_components()
    return [c["name"] for c in lib if c.get("meta", {}).get("component-status") == "Approved"]


def default_props_for_component(name: str, parsed_props: list[dict]) -> dict:
    """Return default/sample prop values for visual testing (in-memory only)."""
    scalar_defaults = {
        "title": "Sample Title",
        "body_text": "Sample body text.",
        "description_text": "A small clearing in the woods.",
        "hp_current": 85,
        "hp_max": 100,
        "location_name": "The Clearing",
        "turn_count": 12,
        "prompt": "> ",
        "placeholder": "command",
        "label": "Label",
        "text": "Additional information for your perusal",
        "name": "Sample",
        "risk_level": "Hunted",
        "luck_band_optional": "Fading",
        "hint_text": "[Tab: complete] [Up/Down: history]",
        "content": "Value 1",
        "icon": "☆",
        "variant": "default",
        "style_hint": "splash",
        "font": "",
    }
    result = {}
    for p in parsed_props:
        prop_name = p["name"]
        if p["is_array"]:
            if "exit" in prop_name or "direction" in prop_name:
                result[prop_name] = [{"id": "n", "label": "north"}, {"id": "s", "label": "south"}]
            elif prop_name == "stats":
                # Character sheet-style stats: mix of value-only and current/max rows.
                result[prop_name] = [
                    {"label": "HP", "current": 50, "max": 100},
                    {"label": "Mana", "current": 30, "max": 60},
                    {"label": "Status", "value": "Cautious"},
                ]
            elif "item" in prop_name or "option" in prop_name or "entity" in prop_name or "npcs" in prop_name:
                result[prop_name] = [
                    {"id": "1", "label": "Item 1"},
                    {"id": "2", "label": "Item 2"},
                ]
            elif "hint" in prop_name or "hints" in prop_name:
                result[prop_name] = [{"id": "1", "label": "look"}, {"id": "2", "label": "go <dir>"}]
            elif prop_name == "needs":
                result[prop_name] = [
                    {"label": "Hunger", "current": 30, "max": 100},
                    {"label": "Thirst", "current": 55, "max": 100},
                    {"label": "Fatigue", "current": 70, "max": 100},
                ]
            elif "block" in prop_name:
                result[prop_name] = ["Block 1", "Block 2"]
            elif "segment" in prop_name:
                result[prop_name] = [
                    {"id": "home", "label": "Home"},
                    {"id": "clearing", "label": "The Clearing"},
                    {"id": "guard", "label": "Guard post"},
                ]
            elif "objective" in prop_name:
                result[prop_name] = [
                    {"id": "1", "label": "Find the key", "checked": False},
                    {"id": "2", "label": "Talk to the guard", "checked": True},
                    {"id": "3", "label": "Open the door", "checked": False},
                ]
            elif prop_name == "lines":
                result[prop_name] = ["You enter the clearing.", "The guard eyes you but says nothing."]
            elif "interaction" in prop_name:
                result[prop_name] = [{"id": "1", "label": "pet dog"}, {"id": "2", "label": "talk to guard"}]
            elif "node" in prop_name:
                result[prop_name] = [
                    {"id": "combat", "label": "Combat", "children": [{"id": "1", "label": "Strike"}, {"id": "2", "label": "Block"}]},
                    {"id": "lore", "label": "Lore", "children": [{"id": "3", "label": "Identify"}]},
                ]
            elif "relation" in prop_name:
                result[prop_name] = [
                    {"id": "allies", "label": "Allies", "items": [{"label": "Guard captain", "attitude": "friendly", "tags": ["city", "watch"]}]},
                    {"id": "rivals", "label": "Rivals", "items": [{"label": "Thieves' Guild", "attitude": "hostile", "tags": ["underworld"]}]},
                ]
            elif "abilit" in prop_name:
                result[prop_name] = [
                    {"label": "Strike", "turns_left": 0},
                    {"label": "Block", "turns_left": 2},
                    {"label": "Dash", "turns_left": 1},
                ]
            else:
                result[prop_name] = [{"id": "1", "label": "Option 1"}]
        else:
            if prop_name == "stats_dict":
                result[prop_name] = {"HP": 85, "Mana": 30, "Stamina": 60}
            else:
                result[prop_name] = scalar_defaults.get(
                prop_name, scalar_defaults.get("label", "<value>")
            )
    return result


# Sample data for randomizing props (QA / visual testing)
_RANDOM_WORDS = (
    "alpha", "bravo", "cellar", "delta", "echo", "forest", "glade", "haven",
    "ivory", "jade", "kite", "lunar", "marsh", "north", "oak", "port", "quest",
    "river", "stone", "tower", "umbra", "vale", "west", "yarn", "zenith",
)
_RANDOM_PLACES = ("The Clearing", "The Alley", "Town Square", "Dark Woods", "Riverbank", "Cave Mouth")
_RANDOM_LABELS = ("Submit", "Cancel", "Look", "Go north", "Take item", "Use", "Drop", "Inventory")
_RANDOM_ICONS = ("☆", "★", "†", "•", "◆", "►", "♥")


def randomize_props_for_component(name: str, parsed_props: list[dict]) -> dict:
    """Return random but sensible prop values for QA visual testing (in-memory only)."""
    result = {}
    for p in parsed_props:
        prop_name = p["name"]
        if p["is_array"]:
            n = random.randint(1, 5)
            if "exit" in prop_name or "direction" in prop_name:
                dirs = ["north", "south", "east", "west", "up", "down"]
                chosen = random.sample(dirs, min(n, len(dirs)))
                result[prop_name] = [{"id": d[0], "label": d} for d in chosen]
            elif "item" in prop_name or "option" in prop_name or "entity" in prop_name or "npcs" in prop_name or "hint" in prop_name or "hints" in prop_name:
                result[prop_name] = [
                    {"id": str(i), "label": random.choice(_RANDOM_WORDS).capitalize() + " " + str(i)}
                    for i in range(1, n + 1)
                ]
            elif "block" in prop_name:
                result[prop_name] = [f"Block {random.choice(_RANDOM_WORDS)}" for _ in range(n)]
            elif "segment" in prop_name:
                n = random.randint(2, 4)
                result[prop_name] = [
                    {"id": f"s{i}", "label": "Home" if i == 0 else random.choice(_RANDOM_PLACES)}
                    for i in range(n)
                ]
            elif "objective" in prop_name:
                n = random.randint(2, 5)
                result[prop_name] = [
                    {"id": str(i), "label": random.choice(_RANDOM_WORDS).capitalize() + " objective", "checked": random.choice((True, False))}
                    for i in range(1, n + 1)
                ]
            elif prop_name == "lines":
                n = random.randint(1, 4)
                result[prop_name] = [" ".join(random.choices(_RANDOM_WORDS, k=random.randint(3, 6))).capitalize() + "." for _ in range(n)]
            elif "interaction" in prop_name:
                result[prop_name] = [
                    {"id": str(i), "label": f"{random.choice(('pet', 'talk to', 'inspect'))} {random.choice(_RANDOM_WORDS)}"}
                    for i in range(1, n + 1)
                ]
            elif "node" in prop_name:
                result[prop_name] = [
                    {"id": f"n{i}", "label": random.choice(_RANDOM_WORDS).capitalize(), "children": [{"id": f"c{j}", "label": random.choice(_RANDOM_WORDS).capitalize()} for j in range(1, 3)]}
                    for i in range(1, n + 1)
                ]
            elif "relation" in prop_name:
                result[prop_name] = [
                    {"id": f"r{i}", "label": random.choice(_RANDOM_WORDS).capitalize(), "items": [{"label": random.choice(_RANDOM_WORDS).capitalize(), "attitude": random.choice(("friendly", "hostile", "neutral")), "tags": []}]}
                    for i in range(1, n + 1)
                ]
            elif "abilit" in prop_name:
                result[prop_name] = [
                    {"label": random.choice(("Strike", "Block", "Dash", "Shoot", "Heal")), "turns_left": random.randint(0, 5)}
                    for i in range(1, n + 1)
                ]
            else:
                result[prop_name] = [
                    {"id": str(i), "label": random.choice(_RANDOM_LABELS) if i == 1 else f"Option {i}"}
                    for i in range(1, n + 1)
                ]
        else:
            if "hp_current" in prop_name or "current" in prop_name:
                result[prop_name] = random.randint(1, 99)
            elif "hp_max" in prop_name or "max" in prop_name:
                result[prop_name] = random.randint(50, 150)
            elif "turn_count" in prop_name or "count" in prop_name:
                result[prop_name] = random.randint(1, 999)
            elif "location" in prop_name or "title" in prop_name:
                result[prop_name] = random.choice(_RANDOM_PLACES)
            elif "body" in prop_name or "description" in prop_name or "text" in prop_name:
                result[prop_name] = " ".join(random.choices(_RANDOM_WORDS, k=random.randint(3, 8))).capitalize() + "."
            elif "icon" in prop_name:
                result[prop_name] = random.choice(_RANDOM_ICONS)
            elif "label" in prop_name:
                result[prop_name] = random.choice(_RANDOM_LABELS)
            elif "prompt" in prop_name:
                result[prop_name] = random.choice(("> ", "$ ", "? "))
            elif prop_name == "variant":
                result[prop_name] = random.choice(("default", "stats"))
            elif prop_name == "stats_dict":
                result[prop_name] = {random.choice(_RANDOM_WORDS).capitalize(): random.randint(1, 100) for _ in range(3)}
            else:
                result[prop_name] = random.choice(_RANDOM_WORDS).capitalize()
    return result


def _serialize_prop_value(value: object) -> str:
    """Serialize a prop value for display in an input (e.g. JSON for lists)."""
    if isinstance(value, list):
        return json.dumps(value, indent=0)
    return str(value)


def _parse_prop_value(raw: str, is_array: bool) -> tuple[object, str | None]:
    """Parse user input into a prop value. Returns (value, error_message)."""
    raw = raw.strip()
    if is_array:
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                return raw, "Must be a JSON array"
            return parsed, None
        except json.JSONDecodeError as e:
            return raw, f"Invalid JSON: {e}"
    return raw, None


def _format_prop_value_for_art(value: object) -> str:
    """Format a prop value as it appears in reference art for default-as-placeholder substitution.
    Exits/directions use '  ' (e.g. 'north  south'); other lists use ', ' (e.g. 'Item 1, Item 2')."""
    if isinstance(value, list):
        if not value:
            return ""
        if isinstance(value[0], dict):
            labels = [str(item.get("label", item.get("id", ""))) for item in value]
            if len(labels) == 2 and all(
                L in ("north", "south", "east", "west", "up", "down") for L in labels
            ):
                return "  ".join(labels)
            return ", ".join(labels)
        return ", ".join(str(x) for x in value)
    return str(value)


def apply_props_to_art(component_name: str, art: str, props: dict, parsed_props: list[dict] | None = None) -> str:
    """Substitute current prop values into the reference art for preview.
    Explicit branches take precedence for precise layout. When parsed_props is provided,
    the generic path uses default-as-placeholder substitution so all components can show
    visible prop changes; add new components via an explicit branch or rely on this."""
    out = art
    # status-bar.default: HP: 85/100  |  The Clearing  |  Turn 12
    if component_name == "status-bar.default":
        hp_c = props.get("hp_current", 85)
        hp_m = props.get("hp_max", 100)
        loc = props.get("location_name", "The Clearing")
        turn = props.get("turn_count", 12)
        out = out.replace("85/100", f"{hp_c}/{hp_m}")
        out = out.replace("The Clearing", str(loc))
        out = out.replace("Turn 12", f"Turn {turn}")
    # status-bar.risk
    elif component_name == "status-bar.risk":
        out = out.replace("40/100", f"{props.get('hp_current', 40)}/{props.get('hp_max', 100)}")
        out = out.replace("The Alley", str(props.get("location_name", "The Alley")))
        out = out.replace("Turn 27", f"Turn {props.get('turn_count', 27)}")
        out = out.replace("Hunted", str(props.get("risk_level", "Hunted")))
        out = out.replace("Fading", str(props.get("luck_band_optional", "Fading")))
    # room-card.default: title in header, body, exits at end
    elif component_name == "room-card.default":
        title = str(props.get("title", "The Clearing"))[:40]
        body = str(props.get("description_text", "A small clearing in the woods."))[:37]
        out = out.replace("The Clearing", title, 1)  # first occurrence in +-- The Clearing ---
        out = out.replace("A small clearing in the woods.", body.ljust(37)[:37])
        exits = props.get("exits", [])
        if isinstance(exits, list):
            if exits and isinstance(exits[0], dict):
                exit_labels = "  ".join(str(e.get("label", e.get("id", ""))) for e in exits)
            else:
                exit_labels = "  ".join(str(e) for e in exits)
            out = out.replace("north  south", exit_labels[:20])
    # breadcrumb.inline: single line built from segments (ordered path from root)
    elif component_name == "breadcrumb.inline":
        segments = props.get("segments", [])
        if isinstance(segments, list) and segments:
            if isinstance(segments[0], dict):
                parts = [str(s.get("label", s.get("id", ""))) for s in segments]
            else:
                parts = [str(s) for s in segments]
            out = " > ".join(parts)
        else:
            out = art.strip() or "Home > The Clearing > Guard post"
        return out
    # button.icon: [icon] label
    elif component_name == "button.icon":
        icon = str(props.get("icon", "☆"))[:2]
        label = str(props.get("label", "Star this"))
        return f"[{icon}] {label}"
    # button.text: [ label ] — ensure something always appears
    elif component_name == "button.text":
        label = (str(props.get("label", "Submit")).strip()) or "Submit"
        return f"[ {label} ]"
    # card.simple: title in header, body_text as one wrapable string (fixed-width box, inner 36)
    elif component_name == "card.simple":
        inner = 36
        title_part = str(props.get("title", "Card title"))[: (inner - 2)]
        filler_len = max(0, (inner - 2) - len(title_part))
        header = "+-- " + title_part + " " + "-" * filler_len + "+"
        body_str = str(
            props.get(
                "body_text",
                "Body text goes here and may wrap across multiple lines when needed. ",
            )
        )
        words = body_str.split()
        lines = []
        current = []
        current_len = 0
        for w in words:
            need = len(w) + (len(current) if current else 0)
            if current:
                need += 1
            if current_len + need <= inner and current:
                current.append(w)
                current_len += need
            elif current_len + need <= inner:
                current = [w]
                current_len = len(w)
            else:
                if current:
                    line = " ".join(current).ljust(inner)[:inner]
                    lines.append(line)
                current = [w]
                current_len = len(w)
        if current:
            lines.append(" ".join(current).ljust(inner)[:inner])
        while len(lines) < 2:
            lines.append(" ".ljust(inner))
        body_part = "\n".join("| " + line + " |" for line in lines[:2])
        footer = "+" + "-" * (inner + 2) + "+"
        return header + "\n" + body_part + "\n" + footer
    # character-sheet.compact: name + 2–3 stat rows with bars when current/max present
    elif component_name == "character-sheet.compact":
        name = str(props.get("name", "Hero"))

        def _stat_bar(current: int | float, max_value: int | float, width: int) -> str:
            try:
                cur = float(current)
                mx = float(max_value)
                if mx <= 0:
                    filled = 0
                else:
                    ratio = max(0.0, min(1.0, cur / mx))
                    filled = int(round(width * ratio))
            except Exception:
                filled = 0
            filled = max(0, min(width, filled))
            return "=" * filled + " " * (width - filled)

        stats = props.get("stats", []) or []
        # Fallback to default-like stats if none provided.
        if not stats:
            stats = [
                {"label": "HP", "current": 85, "max": 100},
                {"label": "Mana", "current": 20, "max": 50},
            ]

        lines: list[str] = [name]
        bar_width = 18
        for stat in stats[:3]:
            label = str(stat.get("label", "Stat"))
            label_part = (label + ":").ljust(6)
            if "current" in stat and "max" in stat:
                cur = stat.get("current", 0)
                mx = stat.get("max", 0)
                bar = _stat_bar(cur, mx, bar_width)
                line = f"{label_part} [{bar}] {cur}/{mx}"
            else:
                value = stat.get("value", "")
                line = f"{label_part} {value}"
            lines.append(line)

        return "\n".join(lines)
    # panel.survival-status: title + one row per need { label, current, max } with bar
    elif component_name == "panel.survival-status":
        needs = props.get("needs", []) or []
        if not needs:
            needs = [
                {"label": "Hunger", "current": 30, "max": 100},
                {"label": "Thirst", "current": 55, "max": 100},
                {"label": "Fatigue", "current": 70, "max": 100},
            ]
        bar_width = 20
        lines_list = ["Survival"]
        for need in needs[:6]:
            label = str(need.get("label", "Need"))
            cur = need.get("current", 0)
            mx = need.get("max", 100) or 100
            try:
                ratio = max(0.0, min(1.0, float(cur) / float(mx)))
                filled = int(round(bar_width * ratio))
            except Exception:
                filled = 0
            filled = max(0, min(bar_width, filled))
            bar = "=" * filled + " " * (bar_width - filled)
            label_part = (label + ":").ljust(9)
            lines_list.append(f"{label_part} [{bar}] {cur}/{mx}")
        return "\n".join(lines_list)
    # cooldown.row: each ability { label, turns_left } → "Label [n]" in one row
    elif component_name == "cooldown.row":
        abilities = props.get("abilities", []) or []
        if not abilities:
            abilities = [
                {"label": "Strike", "turns_left": 0},
                {"label": "Block", "turns_left": 2},
                {"label": "Dash", "turns_left": 1},
            ]
        parts = []
        for ab in abilities[:8]:
            label = str(ab.get("label", "Ability"))
            turns = ab.get("turns_left", 0)
            try:
                turns = int(turns)
            except (TypeError, ValueError):
                turns = 0
            parts.append(f"{label} [{turns}]")
        return "  ".join(parts)
    # tooltip.default: text (default) or variant stats → name + stats_dict
    elif component_name == "tooltip.default":
        variant = str(props.get("variant", "default")).strip().lower()
        if variant == "stats" or (props.get("name") is not None and props.get("stats_dict") is not None):
            name = str(props.get("name", "Stats"))
            stats_dict = props.get("stats_dict")
            if isinstance(stats_dict, dict):
                inner_lines = [name]
                for k, v in list(stats_dict.items())[:6]:
                    inner_lines.append(f"  {k}: {v}")
                inner = "\n".join(inner_lines)
            elif isinstance(stats_dict, list):
                inner_lines = [name]
                for item in stats_dict[:6]:
                    if isinstance(item, dict):
                        inner_lines.append("  " + str(item.get("label", item.get("key", ""))) + ": " + str(item.get("value", item.get("amount", ""))))
                    else:
                        inner_lines.append("  " + str(item))
                inner = "\n".join(inner_lines)
            else:
                inner = name
            inner_w = 30
            top = "+" + "-" * inner_w + "+"
            out_lines = [top]
            for line in inner.splitlines():
                out_lines.append("|  " + line[: inner_w - 4].ljust(inner_w - 4) + " |")
            out_lines.append(top)
            return "\n".join(out_lines)
        text = str(props.get("text", "Additional information for your perusal"))
        # Wrap text to fit box width (e.g. 30 chars)
        width = 30
        words = text.split()
        line_lines = []
        current = []
        current_len = 0
        for w in words:
            need = len(w) + (1 if current else 0)
            if current_len + need <= width and current:
                current.append(w)
                current_len += need
            elif current_len + need <= width:
                current = [w]
                current_len = len(w)
            else:
                if current:
                    line_lines.append(" ".join(current))
                current = [w]
                current_len = len(w)
        if current:
            line_lines.append(" ".join(current))
        if not line_lines:
            line_lines = ["Additional information for your perusal", "your perusal"]
        inner_w = 29
        top = "+" + "-" * inner_w + "+"
        mid = "\n".join("|  " + ln[:inner_w].ljust(inner_w) + " |" for ln in line_lines[:3])
        return top + "\n" + mid + "\n" + top
    # feedback.success: one line from message
    elif component_name == "feedback.success":
        return str(props.get("message", "Taken: rusty sword (+1 weapon)"))
    # feedback.error: one line message and optional suggestion
    elif component_name == "feedback.error":
        msg = str(props.get("message", "You don't see \"sword\" here."))
        sug = props.get("suggestion")
        if sug:
            return msg + " " + str(sug)
        return msg
    # label.inline: label: value
    elif component_name == "label.inline":
        label = str(props.get("label", "HP"))
        value = props.get("value", 85)
        return f"{label}: {value}"
    # input.text: prompt + placeholder text padded with underscores
    elif component_name == "input.text":
        prompt = str(props.get("prompt", "> "))
        placeholder = str(props.get("placeholder", "command"))
        try:
            width = min(int(props.get("max_length", 15)), 40)
        except (TypeError, ValueError):
            width = 15
        field = (placeholder[:width]).ljust(width, "_")
        return prompt + field
    # toast.inline: single-line box with message
    elif component_name == "toast.inline":
        msg = str(props.get("message", "Saved."))[:33]
        line = "|  " + msg.ljust(33) + " |"
        return "+-----------------------------------+\n" + line + "\n+-----------------------------------+"
    # progress-bar.horizontal: bar with = and spaces, optional percent
    elif component_name == "progress-bar.horizontal":
        value = int(props.get("value", 50))
        max_val = int(props.get("max", 100)) or 1
        width = 24
        filled = int(round(width * value / max_val))
        filled = max(0, min(width, filled))
        bar = "=" * filled + " " * (width - filled)
        pct = int(round(100 * value / max_val))
        label = str(props.get("label_optional", ""))
        if label:
            return f"{label} [{bar}] {pct}%"
        return f"[{bar}] {pct}%"
    # meter.resource: one row type + bar + current/max
    elif component_name == "meter.resource":
        typ = str(props.get("type", "HP"))[:6].ljust(6)
        cur = int(props.get("current", 85))
        mx = int(props.get("max", 100)) or 1
        width = 24
        filled = max(0, min(width, int(round(width * cur / mx))))
        bar = "=" * filled + " " * (width - filled)
        return f"{typ} [{bar}] {cur}/{mx}"
    # counter.ammo: label: current/max
    elif component_name == "counter.ammo":
        label = str(props.get("label", "Ammo"))
        cur = props.get("current", 12)
        mx = props.get("max", 24)
        return f"{label}: {cur}/{mx}"
    # counter.score: label: value
    elif component_name == "counter.score":
        label = str(props.get("label", "Score"))
        value = props.get("value", "1,250")
        return f"{label}: {value}"
    # modal.overlay: box.card with title and body_text (same inner width pattern as card.simple)
    elif component_name == "modal.overlay":
        inner = 36
        title_part = str(props.get("title", "Confirm"))[: (inner - 2)]
        filler_len = max(0, (inner - 2) - len(title_part))
        header = "+-- " + title_part + " " + "-" * filler_len + "+"
        body_str = str(props.get("body_text", "Are you sure you want to quit?"))[:inner * 2]
        words = body_str.split()
        lines = []
        current = []
        current_len = 0
        for w in words:
            need = len(w) + (len(current) if current else 0)
            if current:
                need += 1
            if current_len + need <= inner and current:
                current.append(w)
                current_len += need
            elif current_len + need <= inner:
                current = [w]
                current_len = len(w)
            else:
                if current:
                    line = " ".join(current).ljust(inner)[:inner]
                    lines.append(line)
                current = [w]
                current_len = len(w)
        if current:
            lines.append(" ".join(current).ljust(inner)[:inner])
        if not lines:
            lines.append("".ljust(inner))
        body_part = "\n".join("| " + line + " |" for line in lines[:3])
        footer = "+" + "-" * (inner + 2) + "+"
        return header + "\n" + body_part + "\n" + footer
    # form.single-field: bordered box with label, field line, hint
    elif component_name == "form.single-field":
        label = str(props.get("label", "Name"))[:20]
        placeholder = str(props.get("placeholder", "your character name"))[:25]
        hint = str(props.get("hint", "(your character name)"))[:30]
        top = "+----------------------------------+"
        line1 = "| " + (label + ": ").ljust(22) + placeholder.ljust(15) + "      |"
        line2 = "| " + hint.ljust(34) + "            |"
        return top + "\n" + line1 + "\n" + line2 + "\n" + top
    # exit-list.inline: Exits: dir1 dir2 ...
    elif component_name == "exit-list.inline":
        directions = props.get("directions", [])
        if isinstance(directions, list) and directions:
            if isinstance(directions[0], dict):
                labels = [str(d.get("label", d.get("id", ""))) for d in directions]
            else:
                labels = [str(d) for d in directions]
            return "Exits: " + "  ".join(labels[:8])
        return "Exits: north  south  east"
    # entity-list.room: You see: then * item per line (items + npcs)
    elif component_name == "entity-list.room":
        items = props.get("items", [])
        npcs = props.get("npcs", [])
        if isinstance(items, list):
            item_labels = [str(x.get("label", x.get("id", "")) if isinstance(x, dict) else x) for x in items]
        else:
            item_labels = []
        if isinstance(npcs, list):
            npc_labels = [str(x.get("label", x.get("id", "")) if isinstance(x, dict) else x) for x in npcs]
        else:
            npc_labels = []
        lines = ["You see:"]
        for l in item_labels[:6]:
            lines.append("  * " + str(l))
        for l in npc_labels[:6]:
            lines.append("  * " + str(l))
        if len(lines) == 1:
            lines.append("  * brass lamp")
            lines.append("  * guard")
        return "\n".join(lines)
    # choice-wheel.inline: numbered options
    elif component_name == "choice-wheel.inline":
        options = props.get("options", [])
        if isinstance(options, list) and options:
            parts = []
            for i, o in enumerate(options[:8], 1):
                label = o.get("label", o.get("id", "")) if isinstance(o, dict) else str(o)
                parts.append(f"{i}. {label}")
            return "\n".join(parts)
        return "1. Go north\n2. Talk to guard\n3. Take lamp"
    # inventory.list: - label (qty) per line
    elif component_name == "inventory.list":
        items = props.get("items", [])
        if isinstance(items, list) and items:
            lines = []
            for it in items[:10]:
                if isinstance(it, dict):
                    lab = str(it.get("label", it.get("id", "")))
                    qty = it.get("quantity", 1)
                    lines.append(f"- {lab} ({qty})")
                else:
                    lines.append(f"- {it}")
            return "\n".join(lines)
        return "- rusty sword (1)\n- brass lamp (1)\n- key (2)"
    # menu.main: box with title and item lines
    elif component_name == "menu.main":
        title = str(props.get("title", "AskeeDS"))[:28]
        items = props.get("items", [])
        if isinstance(items, list) and items:
            item_lines = ["|  " + (it.get("label", it.get("id", "")) if isinstance(it, dict) else str(it))[:32].ljust(32) + " |" for it in items[:8]]
        else:
            item_lines = ["|  New game                       |", "|  Load game                      |", "|  Options                        |", "|  Quit                           |"]
        header = "+-- " + title + " " + "-" * max(0, 29 - len(title)) + "+"
        footer = "+---------------------------------+"
        return header + "\n" + "\n".join(item_lines) + "\n" + footer
    # menu.pause: same shape as menu.main
    elif component_name == "menu.pause":
        title = str(props.get("title", "Paused"))[:28]
        items = props.get("items", [])
        if isinstance(items, list) and items:
            item_lines = ["|  " + (it.get("label", it.get("id", "")) if isinstance(it, dict) else str(it))[:32].ljust(32) + " |" for it in items[:8]]
        else:
            item_lines = ["|  Resume                         |", "|  Options                        |", "|  Quit                           |"]
        header = "+-- " + title + " " + "-" * max(0, 29 - len(title)) + "+"
        return header + "\n" + "\n".join(item_lines) + "\n+---------------------------------+"
    # typography.banner: Figlet-style art from text + style_hint or font (banner only; use pyfiglet when available)
    elif component_name == "typography.banner":
        text = str(props.get("text", "AskeeDS"))
        style_hint = str(props.get("style_hint", "splash"))
        font_val = props.get("font")
        font = str(font_val).strip() if font_val else None
        try:
            from askee_ds.banner import render_banner_text
            rendered = render_banner_text(
                text, style_hint=style_hint, font=font or None, max_height=10
            )
            if rendered is not None:
                return rendered.rstrip()
        except ImportError:
            pass
        return art.strip() or "  ___  ____  _  __ ______\n / _ )/ __ \\/ |/ // __/ /\n/ _  / /_/ /    /_/ /_/\n/____/\\____/_/|_/___/___"
    # tracker.objective: [ ] or [x] + label per line
    elif component_name == "tracker.objective":
        objectives = props.get("objectives", [])
        if isinstance(objectives, list) and objectives:
            lines = []
            for ob in objectives[:8]:
                if isinstance(ob, dict):
                    lab = str(ob.get("label", ob.get("id", "")))
                    checked = ob.get("checked", False)
                    lines.append("[x] " + lab if checked else "[ ] " + lab)
                else:
                    lines.append("[ ] " + str(ob))
            return "\n".join(lines)
        return "[ ] Find the key\n[x] Talk to the guard\n[ ] Open the door"
    # narrative-log.pane: box with lines[]
    elif component_name == "narrative-log.pane":
        lines_in = props.get("lines", [])
        inner = 50
        if isinstance(lines_in, list) and lines_in:
            body = "\n".join("| " + str(line)[:inner].ljust(inner) + " |" for line in lines_in[:5])
        else:
            body = "| You enter the clearing.                          |\n| The guard eyes you but says nothing.             |\n|                                                  |"
        return "+-- Narrative log ---------------------------------+\n" + body + "\n+--------------------------------------------------+"
    # command-input.default: prompt + placeholder, then hint line
    elif component_name == "command-input.default":
        prompt = str(props.get("prompt", "> "))
        placeholder = str(props.get("placeholder", "go north"))
        hint = str(props.get("hint_text", "[Tab: complete] [Up/Down: history]"))
        return prompt + placeholder + "\n" + hint
    # hint-bar.contextual: Commands: hints
    elif component_name == "hint-bar.contextual":
        hints = props.get("hints", [])
        if isinstance(hints, list) and hints:
            labels = [h.get("label", h.get("id", "")) if isinstance(h, dict) else str(h) for h in hints[:6]]
            return "Commands: " + ", ".join(labels)
        return "Commands: look, go <dir>, take <item>, i(nventory), ? for help"
    # hint-bar.interactions: You can: interactions
    elif component_name == "hint-bar.interactions":
        interactions = props.get("interactions", [])
        if isinstance(interactions, list) and interactions:
            labels = [i.get("label", i.get("id", "")) if isinstance(i, dict) else str(i) for i in interactions[:6]]
            return "You can: " + ", ".join(labels)
        return "You can: pet dog, talk to guard, inspect statue"
    # tree.compact: category lines and indented children
    elif component_name == "tree.compact":
        nodes = props.get("nodes", [])
        if isinstance(nodes, list) and nodes:
            lines = []
            for node in nodes[:6]:
                label = node.get("label", node.get("id", "")) if isinstance(node, dict) else str(node)
                lines.append(label)
                children = node.get("children", []) if isinstance(node, dict) else []
                for c in children[:4]:
                    clab = c.get("label", c.get("id", "")) if isinstance(c, dict) else str(c)
                    lines.append("  > " + clab)
            return "\n".join(lines)
        return "Combat\n  > Strike\n  > Block\n  > Parry\nLore\n  > Identify\n  > Persuade"
    # tree.relationships: category then "  > name (attitude) [tags]"
    elif component_name == "tree.relationships":
        relations = props.get("relations", [])
        if isinstance(relations, list) and relations:
            lines = []
            for r in relations[:6]:
                label = r.get("label", r.get("id", "")) if isinstance(r, dict) else str(r)
                lines.append(label)
                sub = r.get("items", r.get("children", [])) if isinstance(r, dict) else []
                for s in (sub if isinstance(sub, list) else [])[:4]:
                    slab = s.get("label", s.get("id", "")) if isinstance(s, dict) else str(s)
                    att = s.get("attitude", "") if isinstance(s, dict) else ""
                    tags = s.get("tags", []) if isinstance(s, dict) else []
                    tag_str = " [" + ", ".join(tags[:3]) + "]" if tags else ""
                    lines.append("  > " + slab + (f" ({att})" if att else "") + tag_str)
            return "\n".join(lines)
        return "Allies\n  > Guard captain (friendly) [city, watch]\nRivals\n  > Thieves' Guild (hostile) [underworld]"
    # Generic path: explicit branch or default-as-placeholder substitution.
    # When parsed_props is provided, replace default values in art with current props.
    else:
        substituted = False
        if parsed_props is not None:
            default_props = default_props_for_component(component_name, parsed_props)
            for key in props:
                default_val = default_props.get(key)
                if default_val is None:
                    continue
                current_val = props.get(key)
                if isinstance(default_val, (str, int, float)):
                    default_str = str(default_val)
                    current_str = str(current_val)
                elif isinstance(default_val, list):
                    default_str = _format_prop_value_for_art(default_val)
                    current_str = _format_prop_value_for_art(current_val) if isinstance(current_val, list) else str(current_val)
                else:
                    default_str = str(default_val)
                    current_str = str(current_val)
                if default_str and default_str in out:
                    out = out.replace(default_str, current_str, 1)
                    substituted = True
        if not substituted:
            for key, val in props.items():
                if isinstance(val, (str, int, float)) and str(val) in out:
                    out = out.replace(str(val), str(val), 1)
                    break
    # Fallback: when parsed_props was provided, append only if no substitution; else always append
    if parsed_props is None or not substituted:
        try:
            props_preview = json.dumps({k: v for k, v in props.items()}, indent=0)[:200]
        except Exception:
            props_preview = str(props)[:200]
        if "\n[ Props:" not in out:
            out = out.rstrip() + "\n\n[ Props: " + props_preview + " ]"
    return out


class NoteModal(ModalScreen):
    """Modal to enter a session note; appends to tools/visual_test_notes/YYYY-MM-DD.md."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, component_name: str | None = None) -> None:
        super().__init__()
        self._component_name = component_name

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Add session note (saved to tools/visual_test_notes/ by date)", classes="section_title")
            yield Input(placeholder="Note text...", id="note_input")
            yield Horizontal(
                Button("Save", variant="primary", id="note_save"),
                Button("Cancel", id="note_cancel"),
            )

    def on_mount(self) -> None:
        self.query_one("#note_input", Input).focus()

    @on(Button.Pressed, "#note_save")
    @on(Input.Submitted, "#note_input")
    def _save(self) -> None:
        inp = self.query_one("#note_input", Input)
        text = inp.value or ""
        append_session_note(self._component_name, text)
        self.dismiss()
        self.app.notify("Note saved", severity="information", timeout=1)

    @on(Button.Pressed, "#note_cancel")
    def _cancel(self) -> None:
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()


def _startup_banner_text() -> str:
    """AskeeDS Figlet banner for the main menu; random approved font if any, else splash style. Empty if pyfiglet not available."""
    try:
        from askee_ds.banner import render_banner_text
        approved_path = ROOT / "tools" / "figlet_approved_fonts.txt"
        fonts: list[str] = []
        if approved_path.exists():
            try:
                fonts = [f.strip() for f in approved_path.read_text(encoding="utf-8").strip().splitlines() if f.strip()]
            except Exception:
                pass
        out = None
        if fonts:
            font = random.choice(fonts)
            out = render_banner_text("AskeeDS", font=font, max_height=8)
        if not out:
            out = render_banner_text("AskeeDS", style_hint="splash", max_height=8)
        return (out or "").rstrip()
    except ImportError:
        return ""


class StartupScreen(Screen):
    """Choose how to start: browse all, filter by status, quick jump to In Review, or browse Figlet fonts."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, components: list[dict]) -> None:
        super().__init__()
        self.components = components

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("", id="startup_banner")
        yield Static("How do you want to start?", classes="section_title")
        yield Static(SECTION_DIVIDER, classes="section_divider")
        yield OptionList(id="startup_options")
        yield Footer()

    def on_mount(self) -> None:
        banner_el = self.query_one("#startup_banner", Static)
        banner_el.update(_startup_banner_text() or "AskeeDS — Component visual test")
        opt_list = self.query_one("#startup_options", OptionList)
        opt_list.add_option("Browse all components")
        opt_list.add_option("Filter by status only")
        opt_list.add_option("Quick jump to In Review")
        opt_list.add_option("Browse Figlet fonts")

    @on(OptionList.OptionSelected)
    def _on_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if idx == 0:
            self.app.switch_screen(BrowserScreen(self.components, initial_status="All"))
        elif idx == 1:
            self.app.switch_screen(BrowserScreen(self.components, initial_status=None))
        elif idx == 2:
            self.app.switch_screen(BrowserScreen(self.components, initial_status="In Review", quick_jump_in_review=True))
        elif idx == 3:
            self.app.push_screen(FigletFontBrowserScreen())
        else:
            self.app.switch_screen(BrowserScreen(self.components, initial_status=None))

    def action_quit(self) -> None:
        self.app.exit()


# Path for approved Figlet fonts (one name per line); typography.md can reference this.
FIGLET_APPROVED_PATH = ROOT / "tools" / "figlet_approved_fonts.txt"


class FigletFontBrowserScreen(Screen):
    """Browse all pyfiglet fonts with live preview. Approve fonts for use in typography.banner."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("a", "approve", "Approve font"),
        Binding("u", "unapprove", "Unapprove font"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.fonts: list[str] = []
        self._approved: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("Figlet fonts — select to preview. A = approve, U = unapprove. Green = approved.", classes="section_title")
        yield Static(SECTION_DIVIDER, classes="section_divider")
        yield Horizontal(
            Container(OptionList(id="figlet_font_list"), classes="figlet_list_container"),
            Container(Static("Select a font to see preview.", id="figlet_preview"), classes="figlet_preview_container"),
        )
        yield Static("Approved fonts saved to tools/figlet_approved_fonts.txt.", id="figlet_footer_note", classes="section_muted")
        yield Footer()

    def on_mount(self) -> None:
        try:
            from askee_ds.banner import get_figlet_fonts, render_banner_text
            self.fonts = get_figlet_fonts() or []
        except ImportError:
            self.fonts = []
        if not self.fonts:
            self.query_one("#figlet_preview", Static).update(
                "pyfiglet not installed.\n\n"
                "From repo root run:\n  pip install -e \".[visual-test]\"\n"
                "(includes Figlet) or:\n  pip install -e \".[banner]\"\n\n"
                "Plain \"pip install -e .\" does not install optional extras."
            )
            return
        self._load_approved()
        self._refresh_font_list()

    def _load_approved(self) -> None:
        if FIGLET_APPROVED_PATH.exists():
            try:
                self._approved = set(FIGLET_APPROVED_PATH.read_text(encoding="utf-8").strip().splitlines())
            except Exception:
                self._approved = set()
        else:
            self._approved = set()

    def _refresh_font_list(self) -> None:
        """Rebuild the option list with approved fonts shown in green (e.g. on mount)."""
        opt_list = self.query_one("#figlet_font_list", OptionList)
        opt_list.clear_options()
        for f in self.fonts:
            if f in self._approved:
                opt_list.add_option(f"[green]{f}[/green]")
            else:
                opt_list.add_option(f)

    def _update_font_list_option_at_index(self, idx: int) -> None:
        """Update only the option at idx (green if approved, else plain) so highlight/focus is preserved."""
        if idx < 0 or idx >= len(self.fonts):
            return
        font = self.fonts[idx]
        opt_list = self.query_one("#figlet_font_list", OptionList)
        prompt = f"[green]{font}[/green]" if font in self._approved else font
        try:
            opt_list.replace_option_prompt_at_index(idx, prompt)
        except Exception:
            pass

    def _approve_current(self) -> None:
        if not self.fonts:
            self.app.notify("No fonts loaded", severity="warning", timeout=1)
            return
        try:
            opt_list = self.query_one("#figlet_font_list", OptionList)
            idx = getattr(opt_list, "highlighted", None)
            if idx is None or not (0 <= idx < len(self.fonts)):
                self.app.notify("Select a font first (click or Enter)", severity="information", timeout=2)
                return
            font = self.fonts[idx]
            self._approved.add(font)
            FIGLET_APPROVED_PATH.parent.mkdir(parents=True, exist_ok=True)
            lines = sorted(self._approved)
            FIGLET_APPROVED_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self._update_font_list_option_at_index(idx)
            self.app.notify(f"Approved: {font}", severity="information", timeout=2)
            self._update_preview_approval_line(font)
        except Exception as e:
            self.app.notify(f"Could not save: {e}", severity="error", timeout=2)

    def _unapprove_current(self) -> None:
        if not self.fonts:
            self.app.notify("No fonts loaded", severity="warning", timeout=1)
            return
        try:
            opt_list = self.query_one("#figlet_font_list", OptionList)
            idx = getattr(opt_list, "highlighted", None)
            if idx is None or not (0 <= idx < len(self.fonts)):
                self.app.notify("Select a font first (click or Enter)", severity="information", timeout=2)
                return
            font = self.fonts[idx]
            self._approved.discard(font)
            FIGLET_APPROVED_PATH.parent.mkdir(parents=True, exist_ok=True)
            if self._approved:
                lines = sorted(self._approved)
                FIGLET_APPROVED_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
            else:
                FIGLET_APPROVED_PATH.write_text("", encoding="utf-8")
            self._update_font_list_option_at_index(idx)
            self.app.notify(f"Unapproved: {font}", severity="information", timeout=2)
            self._update_preview_approval_line(font)
        except Exception as e:
            self.app.notify(f"Could not save: {e}", severity="error", timeout=2)

    def _update_preview_approval_line(self, font: str) -> None:
        """Refresh the preview for the given font (so Approved: yes/no is current) if it is the one highlighted."""
        try:
            opt_list = self.query_one("#figlet_font_list", OptionList)
            idx = getattr(opt_list, "highlighted", None)
            if idx is None or idx < 0 or idx >= len(self.fonts) or self.fonts[idx] != font:
                return
        except Exception:
            return
        try:
            from askee_ds.banner import render_banner_text
            art = render_banner_text("AskeeDS", font=font, max_height=12)
            if art:
                sample2 = render_banner_text("Quick Fox", font=font, max_height=6)
                block = f"[ {font} ]\n\n{art.rstrip()}"
                if sample2:
                    block += f"\n\n--- sample: Quick Fox ---\n{sample2.rstrip()}"
                block += f"\n\nApproved: {'yes' if font in self._approved else 'no'} (A=approve, U=unapprove)"
                self.query_one("#figlet_preview", Static).update(block)
        except Exception:
            pass

    @on(OptionList.OptionSelected)
    def _on_font_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if idx < 0 or idx >= len(self.fonts):
            return
        font = self.fonts[idx]
        try:
            from askee_ds.banner import render_banner_text
            art = render_banner_text("AskeeDS", font=font, max_height=12)
            if art:
                sample2 = render_banner_text("Quick Fox", font=font, max_height=6)
                block = f"[ {font} ]\n\n{art.rstrip()}"
                if sample2:
                    block += f"\n\n--- sample: Quick Fox ---\n{sample2.rstrip()}"
                block += f"\n\nApproved: {'yes' if font in self._approved else 'no'} (A=approve, U=unapprove)"
                self.query_one("#figlet_preview", Static).update(block)
            else:
                self.query_one("#figlet_preview", Static).update(f"[ {font} ]\n\n(render failed)")
        except Exception as e:
            self.query_one("#figlet_preview", Static).update(f"[ {font} ]\n\nError: {e}")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_approve(self) -> None:
        self._approve_current()

    def action_unapprove(self) -> None:
        self._unapprove_current()

    def action_quit(self) -> None:
        self.app.exit()


class BrowserScreen(Screen):
    """Library browser: filter by status, search by name, list components."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, components: list[dict], initial_status: str | None = None, quick_jump_in_review: bool = False) -> None:
        super().__init__()
        self.components = components
        self.initial_status = initial_status
        self.quick_jump_in_review = quick_jump_in_review
        self.filtered: list[dict] = []
        self.status_filter = "All"
        self.search_query = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("Filter", classes="section_title")
        yield Static(SECTION_DIVIDER, classes="section_divider")
        yield Horizontal(
            Static("Status: ", classes="filter_label"),
            Select(STATUS_OPTIONS, value=self.initial_status if self.initial_status is not None else "In Review", id="status_select"),
            Static("  Search: ", classes="filter_label"),
            Input(placeholder="Filter by name...", id="search_input"),
            id="filter_bar",
            classes="section_filter_bar",
        )
        yield Static("Component list", classes="section_title")
        yield Static(SECTION_DIVIDER, classes="section_divider")
        yield Container(OptionList(id="component_list"), classes="section_list")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_filter()
        self._refresh_list()

    def _apply_filter(self) -> None:
        status_sel = self.query_one("#status_select", Select)
        self.status_filter = str(status_sel.value) if status_sel.value else "All"
        search = self.query_one("#search_input", Input)
        self.search_query = (search.value or "").strip().lower()
        self.filtered = [
            c
            for c in self.components
            if (self.status_filter == "All" or c.get("meta", {}).get("component-status") == self.status_filter)
            and (not self.search_query or self.search_query in c["name"].lower())
        ]
        self.filtered.sort(key=lambda c: (c.get("meta", {}).get("component-status", ""), c["name"]))

    def _refresh_list(self) -> None:
        opt_list = self.query_one("#component_list", OptionList)
        opt_list.clear_options()
        for c in self.filtered:
            status = c.get("meta", {}).get("component-status", "—")
            opt_list.add_option(f"{c['name']}  —  {status}")
        if self.filtered:
            opt_list.add_option("(Start over: change filter above and select first)")

    @on(Select.Changed, "#status_select")
    @on(Input.Changed, "#search_input")
    def _on_filter_change(self) -> None:
        self._apply_filter()
        self._refresh_list()

    @on(OptionList.OptionSelected)
    def _on_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if idx >= len(self.filtered):
            return
        comp = self.filtered[idx]
        self.app.push_screen(DetailScreen(comp, idx, self.filtered))

    def action_quit(self) -> None:
        self.app.exit()


class DetailScreen(Screen):
    """Single component view: reference art, editable props, live preview."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("escape", "back", "Back"),
        Binding("n", "next_component", "Next"),
        Binding("p", "prev_component", "Previous"),
        Binding("r", "reset_props", "Reset props"),
        Binding("z", "randomize_props", "Randomize props"),
        Binding("N", "add_note", "Note"),
    ]

    def __init__(self, component: dict, index: int, filtered_list: list[dict]) -> None:
        super().__init__()
        self.component = component
        self.index = index
        self.filtered_list = filtered_list
        self.parsed_props = parse_props_meta(component.get("meta", {}).get("props", "") or "")
        self.prop_values = default_props_for_component(component["name"], self.parsed_props)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield ScrollableContainer(
            Vertical(
                Static(id="detail_header"),
                Static("Reference art", classes="section_title"),
                Static(SECTION_DIVIDER, classes="section_divider"),
                Container(Static(id="reference_art"), classes="art_block section_reference"),
                Static("Props (edit below)", classes="section_title"),
                Static(SECTION_DIVIDER, classes="section_divider"),
                Container(
                    *self._props_widgets(),
                    classes="section_props",
                ),
                Static("Preview (with current props)", classes="section_title"),
                Static(SECTION_DIVIDER, classes="section_divider"),
                Container(Static(id="preview_art"), classes="art_block section_preview"),
                id="detail_content",
            ),
            id="detail_scroll",
        )
        yield Footer()

    def _props_widgets(self) -> list:
        widgets = []
        for p in self.parsed_props:
            name = p["name"]
            suffix = "[]" if p["is_array"] else ""
            raw = _serialize_prop_value(self.prop_values.get(name))
            widgets.append(Horizontal(Label(f"{name}{suffix}: "), Input(value=raw, id=f"prop_{name}")))
        return widgets

    def on_mount(self) -> None:
        self._set_header()
        self._set_reference_art()
        self._update_preview()

    def _set_header(self) -> None:
        meta = self.component.get("meta", {})
        name = self.component["name"]
        status = meta.get("component-status", "—")
        desc = (meta.get("description") or "")[:80]
        self.query_one("#detail_header", Static).update(
            f"[bold]{name}[/bold]  [dim]({status})[/dim]\n{desc}"
        )

    def _set_reference_art(self) -> None:
        art = (self.component.get("art") or "").rstrip()
        self.query_one("#reference_art", Static).update(art or "(no art)")

    def _get_prop_values_from_inputs(self) -> dict:
        out = {}
        for p in self.parsed_props:
            name = p["name"]
            try:
                inp = self.query_one(f"#prop_{name}", Input)
                raw = inp.value or ""
                val, err = _parse_prop_value(raw, p["is_array"])
                out[name] = val
            except Exception:
                out[name] = self.prop_values.get(name)
        return out

    def _update_preview(self) -> None:
        self.prop_values = self._get_prop_values_from_inputs()
        preview = apply_props_to_art(
            self.component["name"],
            self.component.get("art") or "",
            self.prop_values,
            self.parsed_props,
        )
        self.query_one("#preview_art", Static).update(preview.rstrip())

    @on(Input.Changed)
    def _on_prop_change(self) -> None:
        self._update_preview()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_next_component(self) -> None:
        if self.index + 1 < len(self.filtered_list):
            next_comp = self.filtered_list[self.index + 1]
            self.app.pop_screen()
            self.app.push_screen(DetailScreen(next_comp, self.index + 1, self.filtered_list))

    def action_prev_component(self) -> None:
        if self.index > 0:
            prev_comp = self.filtered_list[self.index - 1]
            self.app.pop_screen()
            self.app.push_screen(DetailScreen(prev_comp, self.index - 1, self.filtered_list))

    def action_reset_props(self) -> None:
        self.prop_values = default_props_for_component(self.component["name"], self.parsed_props)
        for p in self.parsed_props:
            name = p["name"]
            try:
                inp = self.query_one(f"#prop_{name}", Input)
                inp.value = _serialize_prop_value(self.prop_values.get(name))
            except Exception:
                pass
        self._update_preview()

    def action_randomize_props(self) -> None:
        self.prop_values = randomize_props_for_component(self.component["name"], self.parsed_props)
        for p in self.parsed_props:
            name = p["name"]
            try:
                inp = self.query_one(f"#prop_{name}", Input)
                inp.value = _serialize_prop_value(self.prop_values.get(name))
            except Exception:
                pass
        self._update_preview()
        self.notify("Props randomized (QA)", severity="information", timeout=1)

    def action_add_note(self) -> None:
        self.app.push_screen(NoteModal(component_name=self.component["name"]))

    def action_quit(self) -> None:
        self.app.exit()


class ComponentVisualTestApp(App):
    """AskeeDS component visual test application."""

    TITLE = "AskeeDS component visual test"
    CSS_PATH = ROOT / "tools" / "component_visual_test.tcss"
    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.components = load_components()

    def on_mount(self) -> None:
        if not self.components:
            self.notify("No components found. Is design/ascii/components.txt present?", severity="error")
            return
        self.push_screen(StartupScreen(self.components))


def main() -> int:
    if not COMPONENTS_PATH.exists():
        print(f"Error: {COMPONENTS_PATH} not found. Run from repo root.", file=sys.stderr)
        return 1
    app = ComponentVisualTestApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
