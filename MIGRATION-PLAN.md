# AskeeDS v2 Migration Plan

Tracks the restructuring from the U+241F monolith format to the YAML-first
framework architecture. Check items off as they are completed.

For full context on decisions, trade-offs, and the user's answers to strategic
questions, refer to the chats:
- [AskeeDS v2 restructure](a32bb85b-95ca-4c2f-8e46-8e7ddc56dc0a) — original
  Phase 1 assessment, user Q&A, architectural decisions, and Phase 2/3 build.
- [AskeeDS v2 continuation](9a993808-7acd-40f4-818e-d6cb7d3888a5) — Phase 4
  schema work, framework buildout plan, and post-migration roadmap.

---

## Context for new agents

**What is AskeeDS?** An ASCII-based design system and component framework for
TUI/text-based games. It defines game UI components (menus, HUD, inventory,
character sheets, exploration screens, etc.) as structured data with typed props
and reference ASCII art. A Python framework (the `askee_ds` package) loads
these definitions, resolves a theme, and renders real ASCII output.

**What is Askee?** A separate game engine (not in this repo) that will consume
AskeeDS. The name "Askee" is reserved for the engine; the design system
package is `askee_ds` to avoid collision.

**Key decisions made (do not revisit):**
- The old U+241F delimiter format in `design/ascii/components.txt` is being
  replaced by YAML component definitions under `components/`.
- Components are split by category into `components/core/` (6 files, 25
  components) and `components/game/` (9 files, 38 components).
- Design tokens live in `tokens/` (colors.yaml, box-drawing.yaml,
  typography.yaml).
- The framework has three core classes: `Loader`, `Theme`, `Renderer`.
  Import via `from askee_ds import Loader, Theme, Renderer`.
- The old parser modules (`askee_ds/components.py`, `decorations.py`,
  `maps.py`) are kept for backward compatibility but are being superseded.
- 46 of 63 components have declarative render specs. The 17 reference-only
  components need specialized renderers (trees, grids, speech bubbles, radial
  menus, minimaps, figlet, animation).

**Current file structure (new v2 files):**
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
  cli.py                        # unified CLI (validate, preview, list) + legacy commands
  components.py                 # OLD: U+241F parser (legacy, still works)
  decorations.py                # OLD: decoration parser (legacy)
  maps.py                       # OLD: map parser (legacy)
  box_drawing.py                # OLD: box-drawing loader (legacy)
  banner.py                     # OLD: Figlet banner (still useful)
  _paths.py                     # OLD: repo root helper
_archive/                       # archived files
  poc_renderer.py               # POC (replaced by askee_ds package)
tools/migrate.py                # one-time migration tool (can be archived)
MIGRATION-PLAN.md               # this file
```

**Files not yet migrated (still in design/ascii/):**
```
design/ascii/maps/              # map layouts and index (not migrated yet)
design/ascii/map-tiles.yaml     # tileset definitions (not migrated yet)
design/ascii/box-drawing.yaml   # legacy box-drawing (askee_ds/box_drawing.py uses it)
design/ascii/decoration-catalog.txt  # decorations (not migrated yet)
```

**Legacy tools still active:**
```
tools/parse_components.py       # old parser CLI (legacy, not in CI)
tools/parse_decorations.py      # decoration CLI (still in CI)
tools/parse_maps.py             # map CLI (still in CI)
tools/render_demo.py            # old demo renderer (functional)
tools/test_parse_*.py           # tests for legacy parsers
```

**Archived:**
```
_archive/README.md              # archive index
_archive/poc_renderer.py        # POC (replaced by askee_ds package)
_archive/design-ascii/          # old U+241F format files (components.txt, etc.)
_archive/design-ascii/README.md # context: what, why, when to delete
_archive/tools/                 # retired tools (visual test, migration scripts)
_archive/tools/README.md        # context: what, why, when to delete
```

**How to verify things work:**
```bash
# Validate all YAML components against the schema
python3 -m askee_ds.cli validate

# Preview a specific component
python3 -m askee_ds.cli preview room-card.default \
    --props '{"title":"Test Room","description_text":"A test room.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'

# List approved components
python3 -m askee_ds.cli list --status approved

# Load and render via Python API
python3 -c "
from askee_ds import Loader, Theme, Renderer, Validator
loader = Loader()
components = loader.load_components_dir('components/')
tokens = loader.load_tokens_dir('tokens/')
theme = Theme(tokens)
renderer = Renderer(theme)
print(f'{len(components)} components loaded')
print(renderer.render(components['room-card.default'], {
    'title': 'Test Room',
    'description_text': 'A test room.',
    'items': [], 'npcs': [],
    'exits': [{'id': 'n', 'label': 'north'}],
}))
validator = Validator.from_schema_file('components/_schema.yaml')
errors = validator.validate_all(components)
print(f'{len(errors)} validation errors')
"

# Run the old tests (should still pass)
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s tools
```

**Workspace rules to follow:**
- Always update `CHANGELOG.md` before committing (see changelog-before-commit
  rule).
- Commit after major changes (see commit-after-major-changes rule).
- Never reference `.cursor/`, `.mdc`, or gitignored paths from shipped files.
- Use `command git commit` for commits (see scripts/git-commit.sh).

---

## Phase 1 — Foundation (done)

- [x] **POC renderer** (`poc_renderer.py`): Prove the architecture end-to-end
      with Loader, Theme, Renderer pipeline and 4 sample components.
- [x] **Migrate components to YAML** (`components/`): Convert all 63 components
      from `components.txt` to 15 category-split YAML files with typed props.
- [x] **Extract tokens** (`tokens/`): Move color roles, box-drawing, and
      typography conventions to `tokens/`.
- [x] **Migration tool** (`tools/migrate.py`): Reproducible converter with
      dry-run, preview, and write modes.
- [x] **Roundtrip verification**: All 63 components load from YAML and render
      through the POC renderer.

## Phase 2 — Render specs (done)

- [x] **Core render specs**: 20 of 25 core components have render specs.
      5 remain reference-only (nav.vertical, table.fourcolumn,
      typography.banner, spinner.loading, layout.*).
- [x] **Game render specs**: 26 of 38 game components have render specs.
      12 remain reference-only (speech bubbles, trees, minimap, inventory.grid,
      quick-select.radial, tracker.clock, tracker.front, decoration.placeholder).
- [x] **New section types**: Added join (inline), numbered_list, checked_list,
      and progress section types to the renderer. 46/63 components (73%) now
      have working render specs.

## Phase 3 — Package extraction (done)

- [x] **Extract `askee_ds/loader.py`**: Loader class with load_components,
      load_components_dir, load_tokens, load_tokens_dir.
- [x] **Extract `askee_ds/renderer.py`**: Renderer class with all section types
      (header, text, wrap, list, bars, progress, numbered_list, checked_list,
      plus inline and join render types).
- [x] **Extract `askee_ds/theme.py`**: Theme class with colors, border,
      bar_chars, and introspection properties.
- [x] **Update `askee_ds/__init__.py`**: Exports Loader, Theme, Renderer,
      Component, PropDef. Legacy parser modules kept for backward compat.
- [x] **Update `askee_ds/cli.py`**: Unified `askee-ds` CLI with `validate`,
      `preview`, and `list` subcommands using the new YAML Loader + Validator.
      Legacy commands (`askee-ds-validate`, `askee-ds-export`, `askee-ds-demo`)
      kept and marked as legacy.
- [x] **Remove or archive `poc_renderer.py`**: Moved to `_archive/`. The real
      package replaces it.

## Phase 4 — Schema and validation

`components/_schema.yaml` has been written but is not yet enforced. It
defines valid field names, status values, prop types, render types, and
section types.

- [x] **`components/_schema.yaml`**: Written. Defines the meta-schema for
      component YAML files.
- [x] **Schema validator** (`askee_ds/validator.py`): Reads `_schema.yaml`
      and validates component dicts. Checks required fields, status values,
      category prefixes, prop types, render types, box border values, and
      section types. Returns `(component_name, error_message)` tuples.
- [x] **CLI integration**: New unified `askee-ds` CLI with `validate`
      subcommand that loads `components/` via Loader, validates against
      `_schema.yaml`, and reports errors. Also adds `preview` and `list`.
- [x] **Validate on load**: `Loader(schema_path=...)` optionally runs
      validation on every `load_components` call, emitting warnings to
      stderr.

## Phase 5 — Prune and archive

The user said ~20-30 components are core and proven; the rest are speculative.
The user has NOT yet identified which specific components to keep vs archive.
**Ask the user** before pruning — do not decide unilaterally.

- [x] **Identify core vs speculative**: User reviewed all 63 components.
      10 approved components kept as core. 53 in-review components reset
      to `ideated` status (earliest lifecycle state). All data validated
      clean against the schema — no pruning needed.
- [x] **Reset speculative to ideated**: All 53 non-approved components
      kept in place (not archived) with status reset to `ideated`. They
      remain in the same YAML files and will progress through the status
      lifecycle as they are individually designed and proven.
- [x] **Archive old format files**: Moved `components.txt`, `format-spec.md`,
      `prop_shapes.yaml`, `askee_ds_tokens.yaml`, `manifest.yaml`,
      `PROP-INTENT-AND-TEST-DATA-PLAN.md`, `version.txt`, and old `README.md`
      to `_archive/design-ascii/`. Kept `maps/`, `map-tiles.yaml`,
      `box-drawing.yaml`, and `decoration-catalog.txt` in place (not yet
      migrated). Updated `design/ascii/README.md` as a redirect. Legacy
      parser (`askee_ds/components.py`) falls back to archive path.
      Each archive folder has a README explaining context, rationale,
      and safe-to-delete conditions.
- [x] **Archive retired tools**: Moved `component_visual_test.py` (+tcss,
      +tests), `migrate.py`, `add_component_status.py`,
      `merge_intent_into_components.py`, `update_manifest.py`,
      `update_readme_examples.py`, and `figlet_approved_fonts.txt` to
      `_archive/tools/`. Kept `parse_components.py`, `parse_decorations.py`,
      `parse_maps.py`, `render_demo.py` and their tests (still functional).

## Phase 6 — Update tooling and CI (done)

- [x] **Update CI** (`.github/workflows/tests.yml`): Primary validation now
      uses `askee-ds validate` (YAML pipeline). Added a render-all step that
      renders every component with a render spec, checking for exceptions.
      Path triggers updated to include `components/`, `tokens/`, `tests/`.
      Removed old component validation step (`parse_components.py --validate
      design/ascii/components.txt`). Kept map and decoration validation.
- [x] **Update or replace validators**: `askee-ds validate` is the primary
      validation path. Legacy `parse_components.py` kept but no longer in CI.
- [x] **Framework tests** (`tests/test_framework.py`): 25 tests covering
      Loader (load_components_dir, load_tokens_dir, from-string, schema
      skip, validate-on-load), Renderer (inline, join, box, list, bars,
      checked_list, reference fallback, render-all-non-reference), Theme
      (color roles, color resolution, neutral fallback, border styles,
      border resolution, bar chars), Validator (validate-all, bad status,
      bad category, bad render type, bad section type).
- [x] **Old tests updated**: `test_parse_components.py` falls back to
      archive path. `test_package.py` (legacy) still passes. 49 total
      tests (30 framework+package + 19 legacy tools).
- [x] **Remove npm dependency**: `package.json` deleted. All scripts it
      wrapped are either archived or covered by Python CLI commands.

## Phase 7 — README and documentation (done)

- [x] **Rewrite README.md**: Fresh README covering the YAML-first framework:
      what AskeeDS is, who it's for, file structure, getting started (CLI
      and Python API), component examples (rendered output), how to add
      components, render types, status lifecycle, adoption patterns, testing,
      dependencies, and versioning. All references to the old U+241F format,
      components.txt, and old tools removed.
- [x] **Update `design/ascii/README.md`**: Rewritten as a redirect to the
      new structure (done in Phase 5).
- [x] **Update CHANGELOG.md**: All migration work documented under
      Unreleased. Version bump to 0.2.0 recommended when ready to tag.

---

## What's next

The migration is complete. Feature work (specialized renderers, component
composition, runtime adapters, maps/decorations migration, examples, and
packaging) is tracked in **[ROADMAP.md](ROADMAP.md)**.

---

## Commit history (this migration)

```
a64b9b1 docs: rewrite README for the YAML-first framework
eab2e9d feat(framework): archive old format, update CI, add framework tests
51815cf chore(components): reset 53 non-approved components to ideated status
1161576 feat(framework): schema validator, unified CLI, and POC archival
1ac1856 docs: expand migration plan with full context for continuity
b4edd13 feat(package): extract Loader, Theme, Renderer into askee_ds package
bee4d9d feat(framework): render specs for 46/63 components and new section types
c01e443 feat(framework): migrate 63 components to YAML and establish new structure
085d9ac feat(framework): add POC renderer proving YAML-first component architecture
```
