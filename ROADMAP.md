# AskeeDS Roadmap

Current state and next steps for AskeeDS — an ASCII design system and
component framework for TUI and text-based games.

---

## Current state (v4)

The v4 foundation sweep is complete. All planned work items — bug fixes,
responsive architecture, component consolidation, snapshot testing,
component proving, screen composition, and documentation — have been
implemented, tested, and committed.

- **56 components** (24 approved, 32 ideated) across 15 category files.
- **157 tests** in 10 test modules, running in ~1 second.
- **16 render types** in a pluggable registry (`askee_ds/render_types/`).
- **24 snapshot golden files** for visual regression testing.
- **Declarative sizing**: 8 components use `width: fill` with
  `min_width`/`max_width` constraints. Layouts propagate `available_width`
  to children.
- **Interaction specs**: Focusable, keyboard actions, and scrollable
  declarations in component YAML.
- **Screen composition**: 17 example screens across 6 gameplay contexts,
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

## Completed

### v4 — Foundation sweep (current)

1. Fixed 5 broken components and render type bugs
2. Wired `available_width` through layout render types
3. Migrated 8 components to adaptive sizing (`width: fill`)
4. Consolidated `speech-bubble` variants; removed `menu.pause`
5. Snapshot testing for all 24 approved components
6. Proved 14 components (10 → 24 approved)
7. Composed 17 example game screens
8. Documentation split into audience-specific guides

### v3 — Architecture

1. Registry-based renderer (monolithic → modular)
2. Pytest test suite (unittest → pytest)
3. Game content eviction (maps/decorations archived)
4. Validated color roles (color_hint → default_color_role)
5. Declarative sizing model
6. Interaction spec
7. Component catalog audit (63 → 58)
8. Declarative screen composition
9. Documentation restructure

---

## What's next

These are natural next steps now that the foundation is solid.
Priority order reflects dependencies and value.

### 1. Prove more components (ideated → approved)

32 ideated components remain. Priority candidates for the next proving
round:

- `command-input.default` — primary text adventure input
- `exit-list.inline` — room exit display
- `room-card.default` — already uses adaptive sizing, high-value
- `status-bar.default` — already uses adaptive sizing, high-value
- `choice-wheel.inline` — interactive dialogue choices
- Layout components (`layout.app.shell`) — composition primitives

Each promotion requires: renders correctly, has tests, props validated,
serves a stated game genre, not redundant, interaction spec if interactive.

### 2. Migrate more components to adaptive sizing

Extend `width: fill` with constraints to the next tier of components:

- `toast.inline`, `progress-bar.horizontal` — feedback components
- `form.single-field` — input component
- Layout components should propagate height as well as width

### 3. Table sizing support

Extend the `table` render type to respect `available_width`:
- Column widths proportional to available space
- Content truncation when table exceeds available width

### 4. Textual adapter interaction wiring

Wire keyboard actions from interaction specs to Textual key bindings:
- Focusable widgets receive focus ring styling
- Action key bindings trigger Textual messages
- Navigation actions update state props

### 5. Theme variants

Support multiple theme definitions (dark, light, high-contrast) that
swap color tokens while keeping the same component structure.

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
