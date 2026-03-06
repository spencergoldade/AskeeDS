# AskeeDS Roadmap

Current state and next steps for AskeeDS — an ASCII design system and
component framework for TUI and text-based games.

---

## Current state (v4)

The v4 foundation sweep is complete. All planned work items — bug fixes,
responsive architecture, component consolidation, snapshot testing,
component proving, screen composition, and documentation — have been
implemented, tested, and committed.

- **56 components** (all approved) across 15 category files; 24 have snapshot golden files.
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

### 1. (Done) All components approved

All 56 components are now approved. Snapshot coverage exists for 24;
adding canonical props and golden files for the remaining 32 is optional
post-v1.

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

### 7. Standalone designer prototyping tool (medium)

A standalone tool so designers can quickly build **facsimiles** of AskeeDS
interfaces with the UI components. Output is visual-only (no behavior);
meant for layout and flow prototyping. Execution ideas:

- Choose from a list of components to add to a canvas
- Place and move components with arrow keys
- Export or screenshot the composed facsimile for handoff or iteration

### 8. More color themes (low)

Add additional color theme definitions (e.g. more palettes, seasonal, or
accessibility-focused) so products can pick a theme that fits their context.

### 9. Style themes — symbol swap (low)

Support style themes that swap ASCII symbols used in components (borders,
bullets, icons) for a different look and feel while keeping the same
structure. Enables visual variants without changing component logic.

---

## Stakeholder / engine requests

Requests from the Askee engine team are tracked in [STAKEHOLDER_REQUESTS.md](STAKEHOLDER_REQUESTS.md). Prioritized open work is in [BACKLOG.md](BACKLOG.md).

| Request | Status |
|--------|--------|
| **Mod theming / component extension** | Done — contract in INTEGRATING.md (theme/component merge, mod layout, schema, custom render types). |
| **hint-bar.contextual** | Open (optional) — API/component for engine-driven contextual hints. |
| **Screen YAML / composer** | Done — Composer, `askee-ds compose`, and 17 example screens exist. |
| **Python 3.12+** | Done. |

---

## Principles

- **Designer-friendly first**: YAML is the primary authoring surface.
- **Prove before promoting**: Components earn `approved` through use.
- **Declarative over imperative**: Render specs, sizing, interaction — data, not code.
- **Test everything that renders**: Every render type has tests.
- **Schema is the contract**: Update `_schema.yaml` first when adding new fields.
- **Archive, don't delete**: Retired files go to `_archive/` with a README.
