# AskeeDS Framework Roadmap

Feature work to evolve AskeeDS from a component library into a full
framework. The v2 migration (YAML format, package extraction, validator,
CI, tests, README) is complete — see `MIGRATION-PLAN.md` for that history.

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
  map_preview.py                # uses old askee_ds.maps API (needs replacing)
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
- **46 renderable** via declarative render specs (inline, join, box).
- **17 reference-only** — fall back to displaying their `art:` block.
- **49 tests** (30 framework + package, 19 legacy tools).
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

46/63 components render from their declarative specs. The remaining 17 need
new section types, render types, or custom logic in the Renderer. Each
requires updating `_schema.yaml` with the new type and adding tests.

### Batch A — Low-hanging fruit (new section/render types)

These can be implemented as straightforward extensions to the existing
Renderer without architectural changes.

| Component | New type | What to build |
|-----------|----------|---------------|
| `nav.vertical` | `active_list` section | Render items from an array prop, placing a `>` marker on the item whose `id` matches an `active_id` prop. Simlar to the existing `list` section but with selection state. |
| `tracker.clock` | `clock` render type | Render `filled` of `segments` as filled/empty circle characters (e.g. `●○○○`). Single-line output; straightforward string building. |
| `tracker.front` | `stage_track` render type | Render `stages[]` as `[ label ]` boxes joined by `─`, with a `^` marker under `current_stage_index`. Multi-line output (boxes on line 1, marker on line 2). |
| `typography.banner` | `banner` render type | Wire the existing `askee_ds/banner.py` module into the Renderer. When pyfiglet is installed, render Figlet text; otherwise fall back to the reference art. The banner module already handles font selection, width limits, and height truncation. |
| `spinner.loading` | `frames` render type | Return the first frame from a `frames` list in the render spec. Actual animation is a runtime concern — the Renderer's job is to produce a single static frame. Document that consumers should cycle frames on a timer. |

**After Batch A**: 51/63 components renderable (81%).

### Batch B — New layout primitives

These need more involved rendering logic but are still self-contained
within the Renderer.

| Component | New type | What to build |
|-----------|----------|---------------|
| `table.fourcolumn` | `table` section | Column headers + data rows. Accept `columns` (array of header labels) and `rows` (array of arrays or array of objects). Auto-calculate column widths from content, pad cells, draw header separator. Support left/right alignment per column. |
| `speech-bubble.left`, `speech-bubble.right` | `bubble` render type | Wrap text into a bordered bubble shape and add a directional tail (`<` on left, `>` on right). The tail side is a parameter on the render spec, not two separate render types. Bubble width adapts to text length up to a max. |
| `tree.compact`, `tree.relationships` | `tree` section | Recursive rendering with indentation. Walk a nested `children` array, prefixing each level with `├── `, `└── `, and `│   ` connectors. The tree data comes from a prop (e.g. `nodes`); each node has `label` and optional `children`. |
| `inventory.grid` | `grid` section | Arrange `slots[]` into rows of `columns` width. Each cell is a bordered mini-box `[ label ]`. Empty slots render as `[     ]`. The grid width is `columns * cell_width`. |
| `minimap.default` | `charmap` section | Render a 2D `grid` (array of arrays of single characters) directly. Add an optional `legend` (list of `{char, label}` pairs) rendered below the grid. |
| `decoration.placeholder` | `art_lookup` render type | Look up art from the decoration catalog by `art_id`, crop or center it to `width × height`. Requires the decoration catalog to be loadable (see section 4 below). Until decorations are migrated, this can fall back to the reference art. |

**After Batch B**: 62/63 components renderable (98%).

### Batch C — Likely stays reference

| Component | Reasoning |
|-----------|-----------|
| `quick-select.radial` | Spatial compass-rose layout is hard to generalize into a reusable section type. Consumers who need this will build custom rendering. It can stay as `reference` — the art block shows the intended shape, and a consumer implements it in their runtime. |

**Schema updates**: Each new section type or render type must be added to
`components/_schema.yaml` under `render.section_types` or
`render.type_values` so validation passes. Update tests to cover the new
types.

---

## 2. Component composition (`askee_ds/composer.py`)

The three layout components (`layout.app.shell`, `layout.two-column`,
`layout.stack`) are **compositional** — they take other rendered components
as slot content. Without composition, consumers have to manually stitch
rendered strings together. With it, they describe a tree of components and
the framework produces the final output.

This is what turns AskeeDS from a "component library" into a "framework."

### How it works

1. The consumer describes a tree: a layout component with child components
   as slot values.
2. The Composer renders children first (bottom-up), producing strings.
3. Those strings are passed as props to the layout component.
4. The layout's render spec arranges them (stack = vertical concatenation,
   two-column = side-by-side with padding, app.shell = header + sidebar +
   content grid).

### Proposed API

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

### Layout render specs

The layout components currently have `render: { type: reference }`. They
need actual render specs that the Composer can execute. Proposed:

- **`layout.stack`**: New `stack` render type. Takes a `blocks` prop (list
  of pre-rendered strings). Concatenates vertically with no gap.
- **`layout.two-column`**: New `columns` render type. Takes `left_content`
  and `right_content` (pre-rendered strings). Places side-by-side, padding
  shorter column to match height, separated by a border column.
- **`layout.app.shell`**: New `shell` render type. Takes `header`, `nav`,
  and `content` (pre-rendered strings). Arranges as a header row spanning
  full width, then a two-column body (nav on left, content on right).

### Dependencies

- Requires **Batch B** specialized renderers to be useful (so child
  components like `nav.vertical` can render).
- Should be built after the Renderer extensions are stable.

### What to export

- `from askee_ds import Composer`
- Add `compose` subcommand to the CLI (takes a JSON tree description).

---

## 3. Runtime adapters

Adapters translate AskeeDS output into runtime-native widgets. These are
optional and live under `askee_ds/adapters/`.

### `askee_ds/adapters/rich.py`

A Rich `Renderable` that produces styled Rich output from AskeeDS
components. Applies the Theme's color roles as Rich markup (foreground,
background, bold), and uses Rich's built-in box-drawing for borders.

This is the simplest adapter because Rich is a string-level library —
it adds ANSI styling to the same text the Renderer already produces.

**When to build**: After the Renderer extensions are done (so the adapter
has complete output to style).

### `askee_ds/adapters/textual.py`

A Textual `Widget` subclass that renders AskeeDS components inside a
Textual app. Uses the Rich adapter internally for text styling, and adds
Textual CSS for layout, scrolling, and interactivity.

The old visual test TUI (archived at `_archive/tools/component_visual_test.py`)
was a 2317-line Textual app. The adapter should be much simpler — a single
widget that takes a Component + props + Theme and renders it. A new example
app (`examples/textual_app.py`) would demonstrate using it to build a
game-like TUI.

**When to build**: After the Rich adapter exists.

### Game engine adapters

Not in this repo. The Askee engine (separate project) will consume
AskeeDS's YAML definitions and JSON exports directly. Document the
expected integration pattern:

1. Load `components/*.yaml` and `tokens/*.yaml` with the engine's YAML
   parser.
2. Resolve props from game state.
3. Render using the engine's own text/UI system, following the render specs
   as a contract.

A JSON export command (`askee-ds export --format json`) would help engines
that prefer JSON over YAML. This could be added to the CLI as part of this
work.

---

## 4. Maps and decorations migration

Maps and decorations are still in `design/ascii/` in their original
formats. The legacy parsers (`askee_ds/maps.py`, `askee_ds/decorations.py`)
and their CLI tools (`tools/parse_maps.py`, `tools/parse_decorations.py`)
are still active and in CI.

### Maps

Maps are already YAML/text and need relocation, not format conversion:

- Move `design/ascii/maps/` to `maps/` (top level, alongside `components/`
  and `tokens/`).
- Move `design/ascii/map-tiles.yaml` into `maps/` (or into `tokens/` as
  `tokens/map-tiles.yaml` — tilesets are arguably tokens).
- Update `askee_ds/maps.py` to look in the new location (with fallback to
  `design/ascii/maps/` during transition).
- Update CI to validate maps from the new path.
- Archive `design/ascii/maps/` once the move is confirmed.

### Decorations

The decoration catalog (`design/ascii/decoration-catalog.txt`) uses the
same U+241F delimiter format that was just retired for components. It
contains approximately 20 named art entries with metadata (title, tags,
source, license, notes).

Migration plan:
- Convert to YAML. Each art entry becomes a keyed block in
  `decorations/catalog.yaml` (or `decorations/*.yaml` if splitting by
  theme/tag makes sense). Structure:

```yaml
decoration.skull.small:
  title: Small skull
  tags: [skull, spooky]
  source: "https://commons.wikimedia.org/wiki/..."
  license: public-domain
  notes: "Approx 9x5; fits inside card.simple"
  art: |2
    ...ASCII art...
```

- Add a `DecorationLoader` to `askee_ds/loader.py` (or a small
  `askee_ds/decoration_loader.py`) that loads decoration YAML.
- Wire `decoration.placeholder` component's `art_lookup` render type to
  use the loaded catalog.
- Update `askee_ds/decorations.py` (legacy) to fall back to archive path.
- Archive `design/ascii/decoration-catalog.txt` to
  `_archive/design-ascii/`.
- Update CI.

### Box-drawing consolidation

`design/ascii/box-drawing.yaml` is still in place because
`askee_ds/box_drawing.py` (legacy) loads from it. The new framework uses
`tokens/box-drawing.yaml`. Once the legacy `box_drawing.py` module is no
longer referenced by any active code:

- Archive `design/ascii/box-drawing.yaml` to `_archive/design-ascii/`.
- Remove or deprecate `askee_ds/box_drawing.py`.

### After migration

Once maps, decorations, and box-drawing are migrated:
- `design/ascii/` will be empty (or can be removed entirely).
- The legacy modules (`askee_ds/components.py`, `askee_ds/decorations.py`,
  `askee_ds/maps.py`, `askee_ds/box_drawing.py`) can be archived.
- Legacy CLI commands (`askee-ds-validate`, `askee-ds-export`,
  `askee-ds-demo`) can be removed from `pyproject.toml`.
- Legacy tools (`tools/parse_components.py`, `tools/parse_decorations.py`,
  `tools/parse_maps.py`, `tools/render_demo.py` and their tests) can be
  archived.

---

## 5. Examples

The `examples/` directory currently contains only `map_preview.py`, which
uses the old `askee_ds.maps` API. It still works but doesn't demonstrate
the new framework.

### `examples/quick_start.py`

Minimal "hello world" — load one component, render it, print it. 10–15
lines. Replace `map_preview.py` with this as the primary example.

```python
from askee_ds import Loader, Theme, Renderer

loader = Loader()
components = loader.load_components_dir("components/")
tokens = loader.load_tokens_dir("tokens/")
theme = Theme(tokens)
renderer = Renderer(theme)

print(renderer.render(components["room-card.default"], {
    "title": "The Clearing",
    "description_text": "Sunlight filters through the canopy.",
    "items": [{"label": "old map"}],
    "npcs": [],
    "exits": [{"id": "n", "label": "north"}, {"id": "e", "label": "east"}],
}))
```

### `examples/textual_app.py`

A small Textual app that uses AskeeDS components to build a game-like TUI
(status bar + room card + input). Depends on the Textual adapter (section
3 above).

### `examples/full_screen.py`

Uses the Composer (section 2 above) to build a full game screen from a
composed layout tree. Depends on the Composer and at least `layout.stack`.

### `examples/all_components.py`

Renders every non-reference component with sample props and prints them
all. Useful as a visual catalog and a smoke test.

---

## 6. Packaging and release

### pyproject.toml updates

Several updates are needed now that the migration is complete:

- **Description**: Change from `"AskeeDS ASCII design system tools and
  parsers."` to something like `"AskeeDS — ASCII design system and
  component framework for TUI games."`.
- **Version**: Bump to `0.2.0`. The format change is significant (YAML
  replaces U+241F, new framework classes, new CLI).
- **Remove `visual-test` extra**: The visual test TUI has been archived.
  The `visual-test` optional dependency group
  (`textual>=0.47.0, pyfiglet>=0.8.0`) is no longer needed.
- **Add `dev` extra**: `pytest` for testing. Convert existing unittest
  tests to pytest when ready.
- **Legacy CLI entries**: Keep `askee-ds-validate`, `askee-ds-export`,
  `askee-ds-demo` until the legacy modules are fully retired (section 4
  above), then remove them.

### Dependency decisions (already made)

- **jsonschema**: Not needed. The custom `Validator` is simpler and has no
  external dependency.
- **Jinja2**: Not adding. The `{prop}` interpolation with regex is simple
  and sufficient. Jinja2 would add complexity without benefit — ASCII art
  templates need alignment-aware rendering, not general-purpose templating.
- **pytest**: Recommended but not yet added. When added, convert existing
  `unittest.TestCase` classes to plain pytest functions with fixtures.

---

## 7. Legacy retirement

Once maps and decorations are migrated (section 4), everything below can
be archived or removed. This is the final cleanup that makes the project
fully "v2."

### Legacy modules to archive

| Module | Why it still exists | When to archive |
|--------|--------------------|-----------------| 
| `askee_ds/components.py` | Falls back to `_archive/design-ascii/components.txt`. Old `test_package.py` and `tools/test_parse_components.py` still call `load_default_components()`. | When those tests are removed or rewritten. |
| `askee_ds/decorations.py` | Loads `design/ascii/decoration-catalog.txt`. CI runs `parse_decorations.py --validate`. | When decorations are migrated to YAML (section 4). |
| `askee_ds/maps.py` | Loads `design/ascii/maps/`. CI runs `parse_maps.py --validate`. | When maps are relocated (section 4). |
| `askee_ds/box_drawing.py` | Loads `design/ascii/box-drawing.yaml`. | When box-drawing is consolidated (section 4). |
| `askee_ds/_paths.py` | Used by legacy modules. | When legacy modules are archived. |

### Legacy tools to archive

| Tool | When to archive |
|------|-----------------| 
| `tools/parse_components.py` | Already out of CI. Archive when `askee_ds/components.py` is archived. |
| `tools/parse_decorations.py` | When decorations are migrated. |
| `tools/parse_maps.py` | When maps are relocated. |
| `tools/render_demo.py` | When replaced by examples or CLI preview. |
| `tools/test_parse_components.py` | When `parse_components.py` is archived. |
| `tools/test_parse_decorations.py` | When `parse_decorations.py` is archived. |
| `tools/test_parse_maps.py` | When `parse_maps.py` is archived. |

### Legacy CLI entries to remove

`pyproject.toml` still defines `askee-ds-validate`, `askee-ds-export`,
and `askee-ds-demo` pointing at the legacy `validate_main`, `export_main`,
and `demo_main` in `cli.py`. Remove these entries (and the functions) when
the legacy modules are archived.

### Other files to clean up

| File | Action |
|------|--------|
| `design/readme-examples.json` | Orphaned — was generated by the archived `update_readme_examples.py`. Delete. |
| `design/ascii/README.md` | Currently a redirect. Remove when `design/ascii/` is empty. |
| `design/ascii/` | Remove the directory entirely once maps, decorations, and box-drawing are migrated out. |
| `examples/map_preview.py` | Replace with `quick_start.py` (section 5). Archive or delete the old map preview. |
| `tests/test_package.py` | Legacy tests for old parsers. Remove when those parsers are archived. |
| `VERSION` | Consider whether to keep as a file or rely solely on `pyproject.toml` for versioning. |

---

## Suggested build order

The features above have dependencies. Suggested sequence:

1. **Batch A specialized renderers** — no dependencies, immediate value
   (5 more components renderable).
2. **Examples: `quick_start.py` and `all_components.py`** — can be done
   now with the current Renderer.
3. **Batch B specialized renderers** — more complex but still
   self-contained (11 more components).
4. **Maps and decorations migration** — unblocks `decoration.placeholder`
   rendering and clears out `design/ascii/`.
5. **Composer** — depends on layout render specs from Batch B.
6. **Rich adapter** — depends on the Renderer being mostly complete.
7. **Textual adapter + `textual_app.py` example** — depends on the Rich
   adapter.
8. **`full_screen.py` example** — depends on the Composer.
9. **Packaging and release** (`0.2.0`) — do last, when the framework is
   stable.
10. **Legacy retirement** — archive remaining legacy modules and tools
    once maps/decorations are migrated (section 7).
