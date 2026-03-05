# AskeeDS Roadmap

Current state and next steps for AskeeDS — an ASCII design system and
component framework for TUI and text-based games.

---

## Current state (v3 architecture)

The v3 foundational restructure is complete. All 9 planned work items
have been implemented, tested, and committed.

- **58 components** (10 approved, 48 ideated) across 15 category files.
- **109 tests** in 10 test modules, running in under 1 second.
- **16 render types** in a pluggable registry (`askee_ds/render_types/`).
- **Declarative sizing**: components declare `width: fill`, `content`, or
  fixed integers, with min/max constraints.
- **Interaction specs**: focusable, keyboard actions, and scrollable
  declarations in component YAML.
- **Screen composition**: full game screens defined as YAML files,
  rendered via `askee-ds compose` or `Composer.compose_screen()`.
- **CLI**: `validate`, `preview`, `list`, `compose`.

### Architecture

```
Component YAML  ──→  Loader  ──→  Renderer (registry)  ──→  ASCII output
Tokens YAML     ──→  Theme   ──→     ↑
Screen YAML     ──→  Composer ──→    ↑
```

The framework has five core classes: `Loader`, `Theme`, `Renderer`,
`Composer`, `Validator`. Render types are modular functions registered
by name. Custom types can be added via `Renderer.register_type()`.

---

## Completed (v3)

1. Registry-based renderer (monolithic → modular)
2. Pytest test suite (unittest → pytest, 7 focused modules)
3. Game content eviction (maps/ and decorations/ archived)
4. Validated color roles (color_hint → default_color_role)
5. Declarative sizing model (fill, content, min/max)
6. Interaction spec (focusable, actions, scrollable)
7. Component catalog audit (63 → 58, proving criteria defined)
8. Declarative screen composition (YAML screens, CLI compose)
9. Documentation updates

---

## What's next

These are the natural next steps now that the foundation is solid.
Priority order reflects dependencies and value.

### 1. Prove more components (ideated → approved)

Apply the proving criteria to move the strongest ideated components to
approved. Priority candidates:

- `command-input.default` — the primary text adventure input
- `entity-list.room` — room contents display
- `narrative-log.pane` — main game output area
- `menu.main` — main menu (already has interaction spec)
- `feedback.success` / `feedback.error` — core game feedback
- `layout.stack` / `layout.app.shell` — layout primitives

Each promotion requires: renders correctly, has tests, props validated,
serves a stated genre, not redundant, interaction spec if interactive.

### 2. Migrate components to adaptive sizing

Convert hardcoded widths to `width: fill` with min/max constraints:

- `status-bar.default` (width: 50 → fill, min 40, max 80)
- `room-card.default` (width: 44 → fill, min 30, max 60)
- `narrative-log.pane` (width: 52 → fill, min 40, max 70)
- Layout components should pass available_width to children

### 3. Table sizing support

Extend the `table` render type to respect `available_width`:
- Column widths proportional to available space
- min/max column width constraints
- Content truncation when table exceeds available width

### 4. Textual adapter interaction wiring

Wire keyboard actions from interaction specs to Textual key bindings:
- Focusable widgets receive focus ring styling
- Action key bindings trigger Textual messages
- Navigation actions update state props

### 5. More screen examples

Create additional screen YAML files demonstrating different game types:
- `screens/examples/rpg_character.yaml` — character sheet with stats
- `screens/examples/inventory.yaml` — grid or list inventory
- `screens/examples/dialogue.yaml` — NPC conversation flow
- `screens/examples/main_menu.yaml` — title screen with menu

### 6. JSON export

Add `askee-ds export --format json` for engines that prefer JSON:
- Export component definitions as JSON
- Export token values as JSON
- Export screen definitions as JSON

---

## Principles

- **Designer-friendly first**: YAML is the primary authoring surface.
- **Prove before promoting**: Components earn `approved` through use.
- **Declarative over imperative**: Render specs, sizing, interaction — data, not code.
- **Test everything that renders**: Every render type has tests.
- **Schema is the contract**: Update `_schema.yaml` first when adding new fields.
- **Archive, don't delete**: Retired files go to `_archive/` with a README.
