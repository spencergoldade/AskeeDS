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
    }
    result = {}
    for p in parsed_props:
        prop_name = p["name"]
        if p["is_array"]:
            if "exit" in prop_name or "direction" in prop_name:
                result[prop_name] = [{"id": "n", "label": "north"}, {"id": "s", "label": "south"}]
            elif "item" in prop_name or "option" in prop_name or "entity" in prop_name or "npcs" in prop_name:
                result[prop_name] = [
                    {"id": "1", "label": "Item 1"},
                    {"id": "2", "label": "Item 2"},
                ]
            elif "hint" in prop_name or "hints" in prop_name:
                result[prop_name] = [{"id": "1", "label": "look"}, {"id": "2", "label": "go <dir>"}]
            elif "block" in prop_name:
                result[prop_name] = ["Block 1", "Block 2"]
            elif "segment" in prop_name:
                result[prop_name] = [
                    {"id": "home", "label": "Home"},
                    {"id": "clearing", "label": "The Clearing"},
                    {"id": "guard", "label": "Guard post"},
                ]
            else:
                result[prop_name] = [{"id": "1", "label": "Option 1"}]
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
    # button.text: [ label ]
    elif component_name == "button.text":
        label = str(props.get("label", "Submit")).strip()
        return f"[ {label} ]"
    # card.simple: title in header, body_text in first body line (fixed-width box)
    elif component_name == "card.simple":
        title_part = str(props.get("title", "Card title"))[:36]
        filler_len = max(0, 37 - len(title_part))
        header = "+-- " + title_part + " " + "-" * filler_len + "+"
        body_content = str(props.get("body_text", "Body text goes here and may wrap"))[:37].ljust(37)
        body_line1 = "| " + body_content + " |"
        out = header + "\n" + body_line1 + "\n| across multiple lines when needed.   |\n+--------------------------------------+"
        return out
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


class StartupScreen(Screen):
    """Choose how to start: browse all, filter by status, or quick jump to In Review."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, components: list[dict]) -> None:
        super().__init__()
        self.components = components

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("How do you want to start?", classes="section_title")
        yield Static(SECTION_DIVIDER, classes="section_divider")
        yield OptionList(id="startup_options")
        yield Footer()

    def on_mount(self) -> None:
        opt_list = self.query_one("#startup_options", OptionList)
        opt_list.add_option("Browse all components")
        opt_list.add_option("Filter by status only")
        opt_list.add_option("Quick jump to In Review")

    @on(OptionList.OptionSelected)
    def _on_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if idx == 0:
            self.app.switch_screen(BrowserScreen(self.components, initial_status="All"))
        elif idx == 1:
            self.app.switch_screen(BrowserScreen(self.components, initial_status=None))
        elif idx == 2:
            self.app.switch_screen(BrowserScreen(self.components, initial_status="In Review", quick_jump_in_review=True))
        else:
            self.app.switch_screen(BrowserScreen(self.components, initial_status=None))

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
