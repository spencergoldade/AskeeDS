"""
AskeeDS Framework — Proof of Concept
=====================================

What this does:
    Demonstrates the full AskeeDS architecture in one runnable file.
    Component definitions live in YAML (with typed props, render specs,
    and reference ASCII art). A loader parses them, a theme resolves
    color tokens and box-drawing characters, and a renderer turns
    definition + props + theme into real ASCII output.

How to use it:
    python poc_renderer.py

Only dependency: PyYAML (pip install pyyaml).
No external files needed — everything is embedded.
"""

import re
import textwrap
import yaml
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────
# YAML: Design Tokens
# ─────────────────────────────────────────────────────────────────────

TOKENS_YAML = """\
colors:
  neutral:
    bg: "#1e1e1e"
    fg: "#d4d4d4"
    border: "#404040"
    accent: "#569cd6"
  danger:
    bg: "#2d1b1b"
    fg: "#f48771"
    border: "#8b3a3a"
    accent: "#f48771"
  arcane:
    bg: "#251b2d"
    fg: "#d4a0f0"
    border: "#6b4a7b"
    accent: "#d4a0f0"
  nature:
    bg: "#1b2d1b"
    fg: "#90c990"
    border: "#4a6b4a"
    accent: "#90c990"
  dungeon:
    bg: "#252525"
    fg: "#a0a0a0"
    border: "#505050"
    accent: "#a0a0a0"

box_drawing:
  single:
    tl: "+"
    tr: "+"
    bl: "+"
    br: "+"
    h: "-"
    v: "|"
    tj_down: "+"
    tj_up: "+"
    tj_right: "+"
    tj_left: "+"
  rounded:
    tl: "."
    tr: "."
    bl: "'"
    br: "'"
    h: "-"
    v: "|"
    tj_down: "+"
    tj_up: "+"
    tj_right: "+"
    tj_left: "+"

bar:
  filled: "\\u2588"
  empty: "\\u2591"
"""


# ─────────────────────────────────────────────────────────────────────
# YAML: Component Definitions
# ─────────────────────────────────────────────────────────────────────

COMPONENTS_YAML = """\
button.text:
  category: core/buttons
  description: Text-only button for actions and commands.
  status: approved
  props:
    label:
      type: string
      required: true
    color_role:
      type: string
      required: false
  render:
    type: inline
    template: "[ {label} ]"
  art: |
    [ Submit ]
  color_hint: neutral

status-bar.default:
  category: game/hud
  description: Horizontal bar showing key player stats at a glance.
  status: approved
  props:
    hp_current:
      type: integer
      required: true
    hp_max:
      type: integer
      required: true
    location:
      type: string
      required: true
    turn_count:
      type: integer
      required: true
    color_role:
      type: string
      required: false
  render:
    type: box
    width: 50
    border: single
    sections:
      - type: text
        text: " HP: {hp_current}/{hp_max}  |  {location}  |  Turn {turn_count}"
  art: |
    +------------------------------------------------+
    | HP: 8/10  |  Dark Cavern  |  Turn 42           |
    +------------------------------------------------+
  color_hint: neutral

character-sheet.compact:
  category: game/character
  description: Compact stat block with name header and resource bars.
  status: in-review
  props:
    name:
      type: string
      required: true
    stats:
      type: array
      required: true
      element:
        label: string
        current: integer
        max: integer
    color_role:
      type: string
      required: false
  render:
    type: box
    width: 34
    border: single
    sections:
      - type: header
        text: "{name}"
      - type: divider
      - type: bars
        over: stats
        bar_width: 10
        template: " {label:<5} [{bar}] {current}/{max}"
  art: |
    +--------------------------------+
    | Hero Name                      |
    +--------------------------------+
    | HP    [████████░░] 8/10        |
    | STR   [██████░░░░] 6/10        |
    | DEX   [██████████] 10/10       |
    +--------------------------------+
  color_hint: neutral

room-card.default:
  category: game/exploration
  description: Overview of a room with description, entities, and exits.
  status: approved
  props:
    title:
      type: string
      required: true
    description_text:
      type: string
      required: true
    items:
      type: array
      required: false
      element:
        id: string
        label: string
    npcs:
      type: array
      required: false
      element:
        id: string
        label: string
    exits:
      type: array
      required: true
      element:
        id: string
        label: string
    color_role:
      type: string
      required: false
  render:
    type: box
    width: 44
    border: single
    sections:
      - type: header
        text: "{title}"
      - type: divider
      - type: wrap
        text: "{description_text}"
        indent: 1
      - type: blank
      - type: list
        label: "Items"
        over: items
        template: "  {label}"
        if_empty: hide
      - type: list
        label: "NPCs"
        over: npcs
        template: "  {label}"
        if_empty: hide
      - type: divider
      - type: list
        label: "Exits"
        over: exits
        template: "  {label}"
  art: |
    +------------------------------------------+
    | Dark Cavern                              |
    +------------------------------------------+
    | A damp cave with moss-covered walls.     |
    |                                          |
    | Items:                                   |
    |   rusty key                              |
    |   torch                                  |
    | NPCs:                                    |
    |   goblin                                 |
    +------------------------------------------+
    | Exits: north, east                       |
    +------------------------------------------+
  color_hint: dungeon
"""


# ─────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────

@dataclass
class PropDef:
    name: str
    type: str
    required: bool = True
    element: Optional[dict] = None


@dataclass
class Component:
    name: str
    category: str
    description: str
    status: str
    props: dict
    render: dict
    art: str = ""
    color_hint: str = "neutral"


# ─────────────────────────────────────────────────────────────────────
# Loader — parses YAML into Component objects
# ─────────────────────────────────────────────────────────────────────

class Loader:

    def load_components(self, source: str) -> dict[str, Component]:
        raw = yaml.safe_load(source)
        components = {}
        for name, defn in raw.items():
            props = {}
            for pname, pdef in defn.get("props", {}).items():
                if isinstance(pdef, dict):
                    props[pname] = PropDef(
                        name=pname,
                        type=pdef.get("type", "string"),
                        required=pdef.get("required", True),
                        element=pdef.get("element"),
                    )
                else:
                    props[pname] = PropDef(name=pname, type=str(pdef))
            components[name] = Component(
                name=name,
                category=defn.get("category", ""),
                description=defn.get("description", ""),
                status=defn.get("status", ""),
                props=props,
                render=defn.get("render", {}),
                art=defn.get("art", ""),
                color_hint=defn.get("color_hint", "neutral"),
            )
        return components

    def load_tokens(self, source: str) -> dict:
        return yaml.safe_load(source)


# ─────────────────────────────────────────────────────────────────────
# Theme — resolves tokens to concrete values
# ─────────────────────────────────────────────────────────────────────

class Theme:

    def __init__(self, tokens: dict):
        self.tokens = tokens

    def colors(self, role: str) -> dict:
        palette = self.tokens.get("colors", {})
        return palette.get(role, palette.get("neutral", {}))

    def border(self, style: str = "single") -> dict:
        styles = self.tokens.get("box_drawing", {})
        return styles.get(style, styles.get("single", {}))

    def bar_chars(self) -> tuple[str, str]:
        bar = self.tokens.get("bar", {"filled": "\u2588", "empty": "\u2591"})
        return bar["filled"], bar["empty"]


# ─────────────────────────────────────────────────────────────────────
# Renderer — component + props + theme → ASCII string
# ─────────────────────────────────────────────────────────────────────

class Renderer:

    def __init__(self, theme: Theme):
        self.theme = theme

    def render(self, component: Component, props: dict) -> str:
        spec = component.render
        rtype = spec.get("type", "inline")
        if rtype == "inline":
            return self._render_inline(spec, props)
        if rtype == "join":
            return self._render_join(spec, props)
        if rtype == "box":
            return self._render_box(spec, props)
        return component.art.rstrip("\n")

    # -- inline ---------------------------------------------------------

    def _render_inline(self, spec: dict, props: dict) -> str:
        return self._interpolate(spec.get("template", ""), props)

    # -- join -----------------------------------------------------------

    def _render_join(self, spec: dict, props: dict) -> str:
        items = props.get(spec.get("over", ""), [])
        sep = spec.get("separator", "  ")
        tmpl = spec.get("template", "{label}")
        prefix = spec.get("prefix", "")
        parts = [self._interpolate(tmpl, item) for item in items]
        return prefix + sep.join(parts)

    # -- box ------------------------------------------------------------

    def _render_box(self, spec: dict, props: dict) -> str:
        width = spec.get("width", 40)
        bd = self.theme.border(spec.get("border", "single"))
        inner = width - 2
        lines: list[str] = []

        lines.append(bd["tl"] + bd["h"] * inner + bd["tr"])

        for section in spec.get("sections", []):
            stype = section.get("type", "text")

            if stype == "header":
                text = self._interpolate(section["text"], props)
                lines.append(self._row(f" {text}", inner, bd))

            elif stype == "divider":
                lines.append(bd["tj_right"] + bd["h"] * inner + bd["tj_left"])

            elif stype == "text":
                text = self._interpolate(section["text"], props)
                lines.append(self._row(text, inner, bd))

            elif stype == "wrap":
                raw = self._interpolate(section["text"], props)
                indent = section.get("indent", 0)
                prefix = " " * indent
                wrapped = textwrap.wrap(
                    raw, width=inner - indent * 2, break_long_words=False,
                )
                for wline in wrapped or [""]:
                    lines.append(self._row(f"{prefix}{wline}", inner, bd))

            elif stype == "blank":
                lines.append(self._row("", inner, bd))

            elif stype == "list":
                items = props.get(section.get("over", ""), [])
                if not items and section.get("if_empty") == "hide":
                    continue
                label = section.get("label", "")
                tmpl = section.get("template", "  {label}")
                if label:
                    lines.append(self._row(f" {label}:", inner, bd))
                for item in items:
                    text = self._interpolate(tmpl, item)
                    lines.append(self._row(text, inner, bd))

            elif stype == "bars":
                bar_width = section.get("bar_width", 10)
                tmpl = section.get("template", " {label} [{bar}] {current}/{max}")
                filled_ch, empty_ch = self.theme.bar_chars()
                for item in props.get(section.get("over", ""), []):
                    cur = item.get("current", 0)
                    mx = item.get("max", 1)
                    ratio = cur / mx if mx else 0
                    n = round(ratio * bar_width)
                    bar_str = filled_ch * n + empty_ch * (bar_width - n)
                    text = self._interpolate(tmpl, {**item, "bar": bar_str})
                    lines.append(self._row(text, inner, bd))

            elif stype == "progress":
                bar_width = section.get("bar_width", 20)
                tmpl = section.get("template", " {label} [{bar}] {value}/{max}")
                filled_ch, empty_ch = self.theme.bar_chars()
                val = props.get(section.get("value_prop", "value"), 0)
                mx = props.get(section.get("max_prop", "max"), 1)
                ratio = val / mx if mx else 0
                n = round(ratio * bar_width)
                bar_str = filled_ch * n + empty_ch * (bar_width - n)
                merged = {**props, "bar": bar_str}
                text = self._interpolate(tmpl, merged)
                lines.append(self._row(text, inner, bd))

            elif stype == "numbered_list":
                items = props.get(section.get("over", ""), [])
                tmpl = section.get("template", " {label}")
                for i, item in enumerate(items, 1):
                    text = self._interpolate(f" {i}. {tmpl.lstrip()}", item)
                    lines.append(self._row(text, inner, bd))

            elif stype == "checked_list":
                items = props.get(section.get("over", ""), [])
                check_prop = section.get("check_prop", "checked")
                tmpl = section.get("template", "{label}")
                for item in items:
                    mark = "x" if item.get(check_prop) else " "
                    text = f" [{mark}] " + self._interpolate(tmpl, item)
                    lines.append(self._row(text, inner, bd))

        lines.append(bd["bl"] + bd["h"] * inner + bd["br"])
        return "\n".join(lines)

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _row(text: str, inner_width: int, bd: dict) -> str:
        return bd["v"] + text.ljust(inner_width)[:inner_width] + bd["v"]

    @staticmethod
    def _interpolate(template: str, props: dict) -> str:
        def _replace(m: re.Match) -> str:
            key, fmt = m.group(1), m.group(2)
            val = props.get(key, m.group(0))
            return format(val, fmt) if fmt else str(val)
        return re.sub(r"\{(\w+)(?::([^}]+))?\}", _replace, template)


# ─────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────

def main():
    loader = Loader()
    components = loader.load_components(COMPONENTS_YAML)
    tokens = loader.load_tokens(TOKENS_YAML)
    theme = Theme(tokens)
    renderer = Renderer(theme)

    print("=" * 50)
    print("  AskeeDS Framework — Proof of Concept")
    print("=" * 50)

    # 1. Inline component
    print("\n── button.text ──\n")
    print(renderer.render(components["button.text"], {"label": "Attack"}))
    print(renderer.render(components["button.text"], {"label": "Open Inventory"}))

    # 2. Single-row box
    print("\n── status-bar.default ──\n")
    print(renderer.render(components["status-bar.default"], {
        "hp_current": 8, "hp_max": 10,
        "location": "Dark Cavern", "turn_count": 42,
    }))

    # 3. Box with header, divider, and bar sections
    print("\n── character-sheet.compact ──\n")
    print(renderer.render(components["character-sheet.compact"], {
        "name": "Aldric the Weary",
        "stats": [
            {"label": "HP",  "current": 6,  "max": 10},
            {"label": "STR", "current": 8,  "max": 10},
            {"label": "DEX", "current": 10, "max": 10},
            {"label": "INT", "current": 3,  "max": 10},
        ],
    }))

    # 4. Box with wrapped text, conditional lists, and dividers
    print("\n── room-card.default ──\n")
    print(renderer.render(components["room-card.default"], {
        "title": "Sunken Library",
        "description_text": (
            "Water drips from cracked shelves. A faint glow "
            "pulses behind the east wall. Old tomes lie scattered "
            "across the wet stone floor."
        ),
        "items": [
            {"id": "scroll", "label": "waterlogged scroll"},
            {"id": "lantern", "label": "bronze lantern"},
        ],
        "npcs": [
            {"id": "spirit", "label": "whispering spirit"},
        ],
        "exits": [
            {"id": "north", "label": "north (collapsed hallway)"},
            {"id": "east", "label": "east (glowing crack)"},
        ],
    }))

    # 5. Same room-card with no items or NPCs (tests if_empty: hide)
    print("\n── room-card.default (empty room) ──\n")
    print(renderer.render(components["room-card.default"], {
        "title": "Empty Corridor",
        "description_text": "A featureless stone passage stretches ahead.",
        "items": [],
        "npcs": [],
        "exits": [
            {"id": "south", "label": "south (back to library)"},
        ],
    }))

    # 6. Theme inspection
    print("\n── theme inspection ──\n")
    for role in ["neutral", "danger", "arcane", "dungeon"]:
        c = theme.colors(role)
        print(f"  {role:<10}  fg={c['fg']}  bg={c['bg']}  border={c['border']}")

    print()


if __name__ == "__main__":
    main()
