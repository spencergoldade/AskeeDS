# AskeeDS Framework Roadmap

Feature work to evolve AskeeDS from a component library into a full
framework. The v2 migration (YAML format, package extraction, validator,
CI, tests, README) is complete.

For full context on past decisions and trade-offs, refer to the chats:
- [AskeeDS v2 restructure](a32bb85b-95ca-4c2f-8e46-8e7ddc56dc0a) —
  original Phase 1 assessment, user Q&A, and architectural decisions.
- [AskeeDS v2 continuation](9a993808-7acd-40f4-818e-d6cb7d3888a5) —
  Phase 4 schema work, framework buildout plan, and post-migration roadmap.
- [AskeeDS v2 completion](3dac5a38-9c27-49e3-a37d-5e62b0f8fa31) —
  Phases 3–7 completion, archive work, CI rewrite, and this roadmap.

---

## Context for new agents

**What is AskeeDS?** An ASCII-based design system and component framework
for TUI/text-based games. It defines game UI components (menus, HUD,
inventory, character sheets, exploration screens, etc.) as structured YAML
with typed props and reference ASCII art. A Python framework (the `askee_ds`
package) loads these definitions, resolves a theme, and renders real ASCII
output.

**What is Askee?** A separate game engine (not in this repo) that will
consume AskeeDS. The name "Askee" is reserved for the engine; the design
system package is `askee_ds` to avoid collision.

**Key decisions made (do not revisit):**
- Components are YAML definitions under `components/`, split by category
  into `components/core/` (6 files, 25 components) and `components/game/`
  (9 files, 38 components).
- Design tokens live in `tokens/` (colors.yaml, box-drawing.yaml,
  typography.yaml).
- The framework has four core classes: `Loader`, `Theme`, `Renderer`,
  `Validator`. Import via `from askee_ds import Loader, Theme, Renderer`.
- The `{prop}` interpolation with regex is intentionally simple. Do not
  add Jinja2 — ASCII art templates need alignment-aware rendering, not
  general-purpose templating.
- The custom `Validator` reads `_schema.yaml` directly. Do not add
  jsonschema as a dependency.
- 46 of 63 components have declarative render specs. The 17 reference-only
  components need specialized renderers (see section 1 below).
- 10 components are `approved` (proven core). 53 are `ideated` (defined
  but not yet individually proven). All remain in the same YAML files.

**Current file structure:**
```
components/                     # YAML component definitions (the product)
  _schema.yaml                  # meta-schema, enforced by Validator
  core/                         # 6 files, 25 components
    buttons.yaml, display.yaml, feedback.yaml,
    inputs.yaml, layouts.yaml, navigation.yaml
  game/                         # 9 files, 38 components
    character.yaml, conversation.yaml, exploration.yaml,
    hud.yaml, inventory.yaml, menus.yaml,
    notifications.yaml, screens.yaml, trackers.yaml
tokens/                         # design tokens
  colors.yaml                   # 10 semantic color roles
  box-drawing.yaml              # 3 border character sets
  typography.yaml               # font conventions, approved Figlet fonts
askee_ds/                       # Python package
  __init__.py                   # exports Loader, Theme, Renderer, Validator + legacy
  loader.py                     # loads YAML components and tokens (opt. validation)
  renderer.py                   # renders components from definitions
  theme.py                      # resolves tokens to concrete values
  validator.py                  # validates components against _schema.yaml
  cli.py                        # unified CLI (validate, preview, list) + legacy
  banner.py                     # Figlet banner rendering (used by typography.banner)
  components.py                 # LEGACY: U+241F parser (falls back to archive)
  decorations.py                # LEGACY: decoration parser
  maps.py                       # LEGACY: map parser
  box_drawing.py                # LEGACY: loads design/ascii/box-drawing.yaml
  _paths.py                     # repo root helper
tests/
  test_framework.py             # 25 tests: Loader, Renderer, Theme, Validator
  test_package.py               # 5 legacy tests: components, decorations, maps
tools/
  parse_components.py           # LEGACY: parser CLI (not in CI)
  parse_decorations.py          # LEGACY: decoration CLI (in CI)
  parse_maps.py                 # LEGACY: map CLI (in CI)
  render_demo.py                # LEGACY: demo renderer (functional)
  test_parse_*.py               # LEGACY: parser tests (19 tests)
examples/
  quick_start.py                # minimal hello-world (new framework)
  all_components.py             # visual catalog of all renderable components
  map_preview.py                # uses legacy askee_ds.maps API
_archive/                       # archived files (see README in each folder)
  poc_renderer.py, design-ascii/, tools/
```

**Files not yet migrated (still in design/ascii/):**
```
design/ascii/maps/              # map layouts and index
design/ascii/map-tiles.yaml     # tileset definitions
design/ascii/box-drawing.yaml   # legacy box-drawing (askee_ds/box_drawing.py)
design/ascii/decoration-catalog.txt  # U+241F format decorations
```

**How to verify things work:**
```bash
askee-ds validate                          # schema validation
askee-ds preview room-card.default --props '{"title":"Test","description_text":"A test.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
askee-ds list --status approved            # list approved components
python3 -m unittest discover -s tests -v   # framework + package tests
python3 -m unittest discover -s tools      # legacy parser tests
```

**Workspace rules to follow:**
- Always update `CHANGELOG.md` before committing.
- Commit after major changes; let the user control when to push.
- Never reference `.cursor/`, `.mdc`, or gitignored paths from shipped
  files.
- Use `command git commit` for commits.

## Current state (numbers)

- **63 components** in YAML (10 approved, 53 ideated).
- **59 renderable** (94%) via declarative render specs (inline, join, box,
  clock, stage_track, banner, frames, table, bubble, tree, grid, charmap,
  art_lookup + active_list section).
- **4 reference-only** — 3 layout components (Composer) + 1 intentional.
- **43 framework + package tests**, 19 legacy tool tests.
- **CI**: Validates YAML, renders all non-reference components, validates
  maps and decorations.

---

## Principles

- **Designer-friendly first**: AskeeDS is for game designers as much as
  developers. Changes should make authoring easier, not just coding easier.
- **Prove before promoting**: Components start as `ideated` and earn their
  way to `approved` through design, implementation, and testing. Do not
  bulk-approve.
- **Declarative over imperative**: Prefer render specs (data) over custom
  code paths. New renderer capabilities should be general-purpose section
  types, not one-off branches.
- **Test everything that renders**: Every new section type or render type
  needs tests. The `render-all-non-reference` test in CI catches
  regressions.
- **Schema is the contract**: `_schema.yaml` defines what is valid. Update
  it first when adding new types, so the Validator enforces correctness
  from the start.
- **Archive, don't delete**: Retired files go to `_archive/` with a README
  explaining what, why, and when to delete. Nothing is silently removed.

---

## 1. Specialized renderers for the 17 reference-only components

Each requires updating `_schema.yaml` with the new type and adding tests.

### Batch A — Low-hanging fruit (done)

- [x] `nav.vertical` — `active_list` section (box with `>` marker)
- [x] `tracker.clock` — `clock` render type (`●`/`○` segments)
- [x] `tracker.front` — `stage_track` render type (`[ label ]─[ label ]` + `^`)
- [x] `typography.banner` — `banner` render type (pyfiglet with art fallback)
- [x] `spinner.loading` — `frames` render type (returns first frame)
- [x] Schema + 6 tests

**Result**: 51/63 components renderable (81%).

### Batch B — New layout primitives (done)

- [x] `table.fourcolumn` — `table` render type: auto-width columns, header separator
- [x] `speech-bubble.left` + `speech-bubble.right` — `bubble` render type: bordered bubble with `/`/`\` tail
- [x] `tree.compact` + `tree.relationships` — `tree` render type: recursive `├──`/`└──`/`│` connectors
- [x] `inventory.grid` — `grid` render type: bordered cell grid from `slots[]` + `columns`
- [x] `minimap.default` — `charmap` render type: 2D character grid + legend
- [x] `decoration.placeholder` — `art_lookup` render type: falls back to reference art
- [x] Schema updates + 7 tests

**Result**: 59/63 components renderable (94%). Remaining 4: 3 layout components (Composer, section 2) + 1 intentionally reference.

### Batch C — Stays reference (no work needed)

- [x] `quick-select.radial` — intentionally `reference`; spatial compass-rose layout is consumer-implemented

---

## 2. Component composition (`askee_ds/composer.py`)

The three layout components (`layout.app.shell`, `layout.two-column`,
`layout.stack`) are **compositional** — they take other rendered components
as slot content. The Composer renders children bottom-up, passes the
resulting strings as props to the layout, and the layout's render spec
arranges them. This is what turns AskeeDS into a "framework."

- [ ] `layout.stack` — `stack` render type: concatenate `blocks` vertically
- [ ] `layout.two-column` — `columns` render type: side-by-side with border column
- [ ] `layout.app.shell` — `shell` render type: header row + two-column body
- [ ] `askee_ds/composer.py` — Composer class with `compose()` method
- [ ] Export `Composer` from `askee_ds/__init__.py`
- [ ] CLI `compose` subcommand (takes JSON tree description)
- [ ] Tests for Composer and layout render types

**Depends on**: Batch B (child components need to render).

<details><summary>Proposed API</summary>

```python
from askee_ds import Loader, Theme, Renderer, Composer

loader = Loader()
components = loader.load_components_dir("components/")
tokens = loader.load_tokens_dir("tokens/")
theme = Theme(tokens)
renderer = Renderer(theme)
composer = Composer(renderer, components)

output = composer.compose("layout.stack", {
    "blocks": [
        ("status-bar.default", {"hp_current": 8, "hp_max": 10,
                                "location": "Cavern", "turn_count": 5}),
        ("room-card.default",  {"title": "Cavern", "description_text": "A dark cave.",
                                "items": [], "npcs": [],
                                "exits": [{"id": "n", "label": "north"}]}),
        ("command-input.default", {"prompt": ">"}),
    ],
})
print(output)
```

</details>

---

## 3. Runtime adapters

Adapters translate AskeeDS output into runtime-native widgets. Optional,
live under `askee_ds/adapters/`.

- [ ] `askee_ds/adapters/rich.py` — Rich `Renderable` applying Theme color roles as ANSI markup
- [ ] `askee_ds/adapters/textual.py` — Textual `Widget` wrapping the Rich adapter with CSS layout
- [ ] `askee-ds export --format json` — CLI command for engines that prefer JSON over YAML
- [ ] Document game-engine integration pattern (load YAML, resolve props, render via engine)

**Depends on**: Renderer extensions (Batch B) mostly complete.
Rich adapter first, then Textual adapter.

---

## 4. Maps and decorations migration

Maps and decorations are still in `design/ascii/` in their original
formats. Legacy parsers and CLI tools are still active and in CI.

### Maps (relocation, not format conversion)

- [ ] Move `design/ascii/maps/` → `maps/` (top level)
- [ ] Move `design/ascii/map-tiles.yaml` → `maps/` or `tokens/map-tiles.yaml`
- [ ] Update `askee_ds/maps.py` to use new path (with fallback)
- [ ] Update CI to validate maps from new path
- [ ] Archive `design/ascii/maps/` once confirmed

### Decorations (U+241F → YAML conversion)

- [ ] Convert `decoration-catalog.txt` → `decorations/catalog.yaml`
- [ ] Add `DecorationLoader` to `askee_ds/loader.py`
- [ ] Wire `decoration.placeholder` `art_lookup` render type to loaded catalog
- [ ] Update `askee_ds/decorations.py` (legacy) to fall back to archive
- [ ] Archive `design/ascii/decoration-catalog.txt` → `_archive/design-ascii/`
- [ ] Update CI

### Box-drawing consolidation

- [ ] Archive `design/ascii/box-drawing.yaml` → `_archive/design-ascii/`
- [ ] Remove or deprecate `askee_ds/box_drawing.py`

### After migration (unlocked when above are done)

- [ ] Remove `design/ascii/` directory entirely
- [ ] Archive legacy modules (`components.py`, `decorations.py`, `maps.py`, `box_drawing.py`, `_paths.py`)
- [ ] Remove legacy CLI entries from `pyproject.toml`
- [ ] Archive legacy tools and their tests

---

## 5. Examples

- [x] `examples/quick_start.py` — minimal hello-world
- [x] `examples/all_components.py` — visual catalog of all renderable components
- [ ] `examples/map_preview.py` — archive when maps are migrated (section 4)
- [ ] `examples/textual_app.py` — Textual app using AskeeDS (depends on section 3)
- [ ] `examples/full_screen.py` — composed layout tree (depends on section 2)

---

## 6. Packaging and release

- [ ] Update `pyproject.toml` description to reflect the framework
- [ ] Bump version to `0.2.0`
- [ ] Remove `visual-test` optional dependency group (archived)
- [ ] Add `dev` extra with `pytest`; convert unittest → pytest
- [ ] Remove legacy CLI entries after legacy retirement (section 7)

**Dependency decisions (already made — do not revisit):**
jsonschema not needed, Jinja2 not adding, pytest recommended.

---

## 7. Legacy retirement

Unlocked once maps and decorations are migrated (section 4). Final
cleanup that makes the project fully "v2."

### Legacy modules

- [ ] Archive `askee_ds/components.py` (after tests rewritten)
- [ ] Archive `askee_ds/decorations.py` (after decorations migrated)
- [ ] Archive `askee_ds/maps.py` (after maps relocated)
- [ ] Archive `askee_ds/box_drawing.py` (after box-drawing consolidated)
- [ ] Archive `askee_ds/_paths.py` (after all legacy modules archived)


### Legacy tools

- [ ] Archive `tools/parse_components.py` + `tools/test_parse_components.py`
- [ ] Archive `tools/parse_decorations.py` + `tools/test_parse_decorations.py`
- [ ] Archive `tools/parse_maps.py` + `tools/test_parse_maps.py`
- [ ] Archive `tools/render_demo.py`

### Legacy CLI + other cleanup

- [ ] Remove `askee-ds-validate`, `askee-ds-export`, `askee-ds-demo` from `pyproject.toml`
- [ ] Delete `design/readme-examples.json` (orphaned)
- [ ] Remove `design/ascii/README.md` + `design/ascii/` directory
- [ ] Archive `examples/map_preview.py`
- [ ] Remove `tests/test_package.py` (legacy parser tests)
- [ ] Decide on `VERSION` file vs `pyproject.toml`-only versioning

---

## Suggested build order

- [x] **1. Batch A specialized renderers** — done (51/63 renderable)
- [x] **2. Examples: `quick_start.py` and `all_components.py`** — done
- [x] **3. Batch B specialized renderers** — done (59/63, 94%)
- [ ] **4. Maps and decorations migration** — unblocks `decoration.placeholder`, clears `design/ascii/`
- [ ] **5. Composer** — depends on Batch B layout render specs
- [ ] **6. Rich adapter** — depends on Renderer mostly complete
- [ ] **7. Textual adapter + `textual_app.py`** — depends on Rich adapter
- [ ] **8. `full_screen.py` example** — depends on Composer
- [ ] **9. Packaging and release** (`0.2.0`) — when framework is stable
- [ ] **10. Legacy retirement** — archive remaining legacy after maps/decorations migrated
