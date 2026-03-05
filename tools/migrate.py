#!/usr/bin/env python3
"""
Migrate components.txt (U+241F format) to YAML category files.

Reads the existing AskeeDS component library, converts each component
to the new YAML format with typed props and reference art, and writes
them as category-split files under components/core/ and components/game/.

Usage:
    python3 tools/migrate.py              # dry run (prints summary)
    python3 tools/migrate.py --write      # writes files to disk
    python3 tools/migrate.py --preview N  # show full YAML for component N

Only dependency: PyYAML (already in the project).
"""

import argparse
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from askee_ds.components import parse_components


# ─────────────────────────────────────────────────────────────────────
# Category mapping
# ─────────────────────────────────────────────────────────────────────

CATEGORY_MAP = {
    # core/layouts — foundational layout containers
    "layout.app.shell":       "core/layouts",
    "layout.two-column":      "core/layouts",
    "layout.stack":           "core/layouts",

    # core/buttons — action triggers
    "button.icon":            "core/buttons",
    "button.text":            "core/buttons",

    # core/inputs — user input
    "command-input.default":  "core/inputs",
    "input.text":             "core/inputs",
    "form.single-field":      "core/inputs",

    # core/feedback — system responses
    "feedback.success":       "core/feedback",
    "feedback.error":         "core/feedback",
    "feedback.mixed":         "core/feedback",
    "modal.overlay":          "core/feedback",
    "toast.inline":           "core/feedback",
    "progress-bar.horizontal":"core/feedback",
    "spinner.loading":        "core/feedback",

    # core/navigation — wayfinding
    "nav.vertical":           "core/navigation",
    "breadcrumb.inline":      "core/navigation",

    # core/display — text, data, and content elements
    "typography.banner":      "core/display",
    "divider.horizontal":     "core/display",
    "label.inline":           "core/display",
    "icon.placeholder":       "core/display",
    "tooltip.default":        "core/display",
    "card.simple":            "core/display",
    "header.banner":          "core/display",
    "table.fourcolumn":       "core/display",

    # game/hud — heads-up display
    "status-bar.default":     "game/hud",
    "status-bar.risk":        "game/hud",
    "meter.resource":         "game/hud",
    "counter.ammo":           "game/hud",
    "counter.score":          "game/hud",
    "status-icon.row":        "game/hud",
    "cooldown.badge":         "game/hud",
    "cooldown.row":           "game/hud",
    "hint-bar.contextual":    "game/hud",
    "hint-bar.interactions":  "game/hud",

    # game/inventory
    "inventory.grid":         "game/inventory",
    "inventory.list":         "game/inventory",

    # game/character — stats, conditions, relationships
    "character-sheet.compact":"game/character",
    "panel.survival-status":  "game/character",
    "panel.consequence":      "game/character",
    "tree.compact":           "game/character",
    "tree.relationships":     "game/character",

    # game/exploration — rooms, maps, narrative
    "room-card.default":      "game/exploration",
    "entity-list.room":       "game/exploration",
    "exit-list.inline":       "game/exploration",
    "minimap.default":        "game/exploration",
    "narrative-log.pane":     "game/exploration",

    # game/conversation — dialogue and choices
    "speech-bubble.left":     "game/conversation",
    "speech-bubble.right":    "game/conversation",
    "choice-wheel.inline":    "game/conversation",

    # game/trackers — objectives, time, fronts
    "tracker.objective":      "game/trackers",
    "tracker.clock":          "game/trackers",
    "tracker.front":          "game/trackers",

    # game/notifications — achievements, loot
    "notification.achievement":"game/notifications",
    "notification.loot":      "game/notifications",

    # game/menus — game-specific menus
    "menu.main":              "game/menus",
    "menu.pause":             "game/menus",
    "quick-select.radial":    "game/menus",

    # game/screens — full-screen states
    "screen.loading":         "game/screens",
    "screen.crafting":        "game/screens",
    "screen.death":           "game/screens",
    "screen.tutorial":        "game/screens",
    "decoration.placeholder": "game/screens",
}


# ─────────────────────────────────────────────────────────────────────
# Known integer props (from prop_shapes.yaml scalar_types + conventions)
# ─────────────────────────────────────────────────────────────────────

INTEGER_PROPS = {
    "hp_current", "hp_max", "turn_count", "max_visible", "max_length",
    "value", "max", "current", "columns", "current_stage_index",
    "turns_left", "width", "height", "filled", "success_chance",
    "quantity", "amount", "row", "col",
}

# Array element shapes keyed by prop name (from prop_shapes.yaml)
ARRAY_SHAPES = {
    "stats":        {"label": "string", "current": "integer", "max": "integer"},
    "needs":        {"label": "string", "current": "integer", "max": "integer"},
    "segments":     {"id": "string", "label": "string"},
    "exits":        {"id": "string", "label": "string"},
    "directions":   {"id": "string", "label": "string"},
    "options":      {"id": "string", "label": "string"},
    "items":        {"id": "string", "label": "string"},
    "objectives":   {"id": "string", "label": "string", "checked": "boolean"},
    "lines":        "string",
    "hints":        {"id": "string", "label": "string"},
    "interactions": {"id": "string", "label": "string"},
    "nodes":        {"id": "string", "label": "string", "children": "array"},
    "relations":    {"name": "string", "attitude": "string", "tags": "array"},
    "abilities":    {"label": "string", "turns_left": "integer"},
    "blocks":       "string",
    "controls":     {"id": "string", "label": "string"},
    "slots":        {"id": "string", "label": "string"},
    "frames":       "string",
    "actions":      {"id": "string", "label": "string"},
    "npcs":         {"id": "string", "label": "string"},
    "icons":        {"symbol": "string", "label": "string"},
    "inputs":       {"label": "string", "item_name": "string"},
    "resource_costs": {"label": "string", "amount": "integer"},
    "body_conditions": {"label": "string", "severity": "string"},
    "mental_conditions": {"label": "string", "severity": "string"},
    "legend_entries": {"char": "string", "label": "string"},
    "grid":         "array",
}

# Render specs for components proven in the POC
POC_RENDER_SPECS = {
    "button.text": {
        "type": "inline",
        "template": "[ {label} ]",
    },
    "status-bar.default": {
        "type": "box",
        "width": 50,
        "border": "single",
        "sections": [
            {"type": "text", "text": " HP: {hp_current}/{hp_max}  |  {location}  |  Turn {turn_count}"},
        ],
    },
    "character-sheet.compact": {
        "type": "box",
        "width": 34,
        "border": "single",
        "sections": [
            {"type": "header", "text": "{name}"},
            {"type": "divider"},
            {"type": "bars", "over": "stats", "bar_width": 10,
             "template": " {label:<5} [{bar}] {current}/{max}"},
        ],
    },
    "room-card.default": {
        "type": "box",
        "width": 44,
        "border": "single",
        "sections": [
            {"type": "header", "text": "{title}"},
            {"type": "divider"},
            {"type": "wrap", "text": "{description_text}", "indent": 1},
            {"type": "blank"},
            {"type": "list", "label": "Items", "over": "items",
             "template": "  {label}", "if_empty": "hide"},
            {"type": "list", "label": "NPCs", "over": "npcs",
             "template": "  {label}", "if_empty": "hide"},
            {"type": "divider"},
            {"type": "list", "label": "Exits", "over": "exits",
             "template": "  {label}"},
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────
# Prop parsing
# ─────────────────────────────────────────────────────────────────────

def parse_prop_string(raw: str) -> dict:
    """Parse a comma-separated prop string into typed PropDef dicts."""
    if not raw or raw.strip().lower() == "none":
        return {}

    # Strip variant info after semicolons (e.g. "; optional variant stats: ...")
    main_part = raw.split(";")[0]

    props = {}
    for token in main_part.split(","):
        token = token.strip()
        if not token:
            continue

        required = True
        is_array = False

        # Handle trailing [] for arrays
        if token.endswith("[]"):
            token = token[:-2]
            is_array = True

        # Handle _optional suffix
        clean = token
        if clean.endswith("_optional"):
            clean = clean[:-9]  # remove _optional
            required = False
        elif clean == "color_role_optional":
            clean = "color_role"
            required = False

        # Determine type
        if is_array:
            ptype = "array"
            element = ARRAY_SHAPES.get(clean)
            if element:
                props[clean] = {"type": "array", "required": required}
                if isinstance(element, dict):
                    props[clean]["element"] = element
                else:
                    props[clean]["element_type"] = element
            else:
                props[clean] = {"type": "array", "required": required,
                                "element": {"id": "string", "label": "string"}}
        elif clean in INTEGER_PROPS:
            props[clean] = {"type": "integer", "required": required}
        elif clean == "interactive":
            props[clean] = {"type": "boolean", "required": required}
        else:
            props[clean] = {"type": "string", "required": required}

    return props


# ─────────────────────────────────────────────────────────────────────
# Component conversion
# ─────────────────────────────────────────────────────────────────────

def convert_component(comp: dict) -> dict:
    """Convert a parsed U+241F component to the new YAML structure."""
    name = comp["name"]
    meta = comp.get("meta", {})
    art = comp.get("art", "").strip("\n")

    category = CATEGORY_MAP.get(name, "uncategorized")
    status = meta.get("component-status", "unknown").lower().replace(" ", "-")

    props_raw = meta.get("props", "")
    props = parse_prop_string(props_raw)

    result = {
        "category": category,
        "description": meta.get("description", ""),
        "status": status,
        "props": props if props else None,
    }

    # Render spec: use POC spec if available, else reference
    if name in POC_RENDER_SPECS:
        result["render"] = POC_RENDER_SPECS[name]
    else:
        result["render"] = {"type": "reference"}

    if art:
        result["art"] = art + "\n"

    # Optional fields
    color_hints = meta.get("color-hint", "")
    if color_hints:
        result["color_hint"] = color_hints.split(",")[0].strip().split()[0]

    if meta.get("interactive", "").lower() == "true":
        result["interactive"] = True

    if meta.get("variant"):
        result["variant"] = meta["variant"]

    notes = meta.get("usage", "")
    if notes:
        result["notes"] = notes

    return result


# ─────────────────────────────────────────────────────────────────────
# YAML output — hand-formatted for readability
# ─────────────────────────────────────────────────────────────────────

def yaml_value(val, indent=0) -> str:
    """Format a value for YAML output."""
    prefix = "  " * indent
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, str):
        if "\n" in val:
            lines = val.split("\n")
            out = "|\n"
            for line in lines:
                out += f"{prefix}  {line}\n"
            return out.rstrip("\n")
        if any(c in val for c in ":#{}[]|>&*!%@`'\","):
            escaped = val.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if not val:
            return '""'
        return val
    if isinstance(val, list):
        if not val:
            return "[]"
        out = ""
        for item in val:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    formatted = yaml_value(v, indent + 1)
                    if first:
                        out += f"\n{prefix}  - {k}: {formatted}"
                        first = False
                    else:
                        out += f"\n{prefix}    {k}: {formatted}"
            else:
                out += f"\n{prefix}  - {yaml_value(item, indent + 1)}"
        return out
    if isinstance(val, dict):
        if not val:
            return "{}"
        out = ""
        for k, v in val.items():
            formatted = yaml_value(v, indent + 1)
            if isinstance(v, (dict, list)) and v:
                out += f"\n{prefix}  {k}:{formatted}"
            else:
                out += f"\n{prefix}  {k}: {formatted}"
        return out
    return str(val)


def component_to_yaml(name: str, data: dict) -> str:
    """Produce a clean YAML block for one component."""
    lines = [f"{name}:"]

    field_order = [
        "category", "description", "status", "props", "render",
        "art", "color_hint", "interactive", "variant", "notes",
    ]

    for key in field_order:
        if key not in data or data[key] is None:
            continue
        val = data[key]

        if key == "art":
            art_lines = val.rstrip("\n").split("\n")
            nonempty = [l for l in art_lines if l.strip()]
            if nonempty:
                min_indent = min(len(l) - len(l.lstrip()) for l in nonempty)
            else:
                min_indent = 0
            lines.append("  art: |2")
            for al in art_lines:
                stripped = al[min_indent:] if len(al) >= min_indent else al
                lines.append(f"    {stripped}")
        elif key == "props" and isinstance(val, dict):
            lines.append("  props:")
            for pname, pdef in val.items():
                if isinstance(pdef, dict):
                    lines.append(f"    {pname}:")
                    for pk, pv in pdef.items():
                        if isinstance(pv, dict):
                            lines.append(f"      {pk}:")
                            for ek, ev in pv.items():
                                lines.append(f"        {ek}: {ev}")
                        else:
                            lines.append(f"      {pk}: {yaml_value(pv)}")
                else:
                    lines.append(f"    {pname}: {yaml_value(pdef)}")
        elif key == "render" and isinstance(val, dict):
            lines.append("  render:")
            for rk, rv in val.items():
                if isinstance(rv, list):
                    lines.append(f"    {rk}:")
                    for item in rv:
                        if isinstance(item, dict):
                            first = True
                            for ik, iv in item.items():
                                if first:
                                    lines.append(f"      - {ik}: {yaml_value(iv, 4)}")
                                    first = False
                                else:
                                    lines.append(f"        {ik}: {yaml_value(iv, 4)}")
                        else:
                            lines.append(f"      - {yaml_value(item, 3)}")
                else:
                    lines.append(f"    {rk}: {yaml_value(rv, 2)}")
        elif isinstance(val, str) and len(val) > 70:
            lines.append(f"  {key}: >-")
            wrapped = []
            words = val.split()
            current = ""
            for w in words:
                if current and len(current) + len(w) + 1 > 70:
                    wrapped.append(current)
                    current = w
                else:
                    current = f"{current} {w}" if current else w
            if current:
                wrapped.append(current)
            for wl in wrapped:
                lines.append(f"    {wl}")
        else:
            lines.append(f"  {key}: {yaml_value(val)}")

    return "\n".join(lines)


def category_header(category: str) -> str:
    """A comment header for a category file."""
    parts = category.split("/")
    group = parts[0]
    name = parts[1] if len(parts) > 1 else parts[0]
    nice = name.replace("-", " ").replace("_", " ").title()
    return f"# AskeeDS — {group}/{name}\n# {nice} components.\n"


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true",
                        help="Write YAML files to disk under components/")
    parser.add_argument("--preview", type=int, metavar="N",
                        help="Print full YAML for the Nth component (0-based)")
    parser.add_argument("--source", default=str(ROOT / "design" / "ascii" / "components.txt"),
                        help="Path to components.txt")
    args = parser.parse_args()

    with open(args.source) as f:
        text = f.read()
    parsed = parse_components(text)

    # Convert all components
    converted = []
    for comp in parsed:
        name = comp["name"]
        data = convert_component(comp)
        converted.append((name, data))

    # Preview mode
    if args.preview is not None:
        idx = args.preview
        if 0 <= idx < len(converted):
            name, data = converted[idx]
            print(component_to_yaml(name, data))
        else:
            print(f"Index {idx} out of range (0–{len(converted)-1})")
        return

    # Group by category
    by_category: dict[str, list[tuple[str, dict]]] = {}
    for name, data in converted:
        cat = data["category"]
        by_category.setdefault(cat, []).append((name, data))

    # Summary
    print(f"Migrating {len(converted)} components into {len(by_category)} category files:\n")
    for cat in sorted(by_category):
        names = [n for n, _ in by_category[cat]]
        print(f"  {cat}.yaml ({len(names)} components)")
        for n in names:
            print(f"    - {n}")
    print()

    if not args.write:
        print("Dry run — pass --write to create files.")
        print("Use --preview N to inspect a specific component.\n")
        return

    # Write files
    out_root = ROOT / "components"
    created = []
    for cat in sorted(by_category):
        parts = cat.split("/")
        dir_path = out_root / parts[0]
        dir_path.mkdir(parents=True, exist_ok=True)
        file_name = parts[1] + ".yaml" if len(parts) > 1 else parts[0] + ".yaml"
        file_path = dir_path / file_name

        blocks = [category_header(cat)]
        for name, data in by_category[cat]:
            blocks.append(component_to_yaml(name, data))

        file_path.write_text("\n\n".join(blocks) + "\n")
        created.append(str(file_path.relative_to(ROOT)))

    print(f"Wrote {len(created)} files:\n")
    for p in sorted(created):
        print(f"  {p}")
    print()


if __name__ == "__main__":
    main()
