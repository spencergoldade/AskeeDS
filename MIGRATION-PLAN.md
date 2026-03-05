# AskeeDS v2 Migration Plan

Tracks the restructuring from the U+241F monolith format to the YAML-first
framework architecture. Check items off as they are completed.

For full context on decisions, trade-offs, and the user's answers to strategic
questions, refer to the chat titled [AskeeDS v2 restructure](a32bb85b-95ca-4c2f-8e46-8e7ddc56dc0a).

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
  _schema.yaml                  # meta-schema (written, not yet enforced)
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
  __init__.py                   # exports Loader, Theme, Renderer + legacy
  loader.py                     # NEW: loads YAML components and tokens
  renderer.py                   # NEW: renders components from definitions
  theme.py                      # NEW: resolves tokens to concrete values
  cli.py                        # OLD: needs updating to use new loader
  components.py                 # OLD: U+241F parser (legacy, still works)
  decorations.py                # OLD: decoration parser (legacy)
  maps.py                       # OLD: map parser (legacy)
  box_drawing.py                # OLD: box-drawing loader (legacy)
  banner.py                     # OLD: Figlet banner (still useful)
  _paths.py                     # OLD: repo root helper
poc_renderer.py                 # POC (to be archived once package works)
tools/migrate.py                # one-time migration tool (can be archived)
MIGRATION-PLAN.md               # this file
```

**Old files still in place (to be archived in Phase 5):**
```
design/ascii/components.txt     # 2257-line monolith (U+241F format)
design/ascii/format-spec.md     # grammar for the old format
design/ascii/prop_shapes.yaml   # old separate prop shapes file
design/ascii/askee_ds_tokens.yaml  # old tokens (replaced by tokens/)
design/ascii/manifest.yaml      # old manifest (replaced by YAML structure)
design/ascii/box-drawing.yaml   # old box-drawing (replaced by tokens/)
design/ascii/decoration-catalog.txt
design/ascii/maps/              # maps (still valid, not migrated yet)
tools/component_visual_test.py  # 2317-line retired TUI
tools/parse_components.py       # old parser CLI (delegates to askee_ds/)
tools/parse_decorations.py      # old decoration CLI
tools/parse_maps.py             # old map CLI
tools/render_demo.py            # old demo renderer
tools/update_manifest.py        # old manifest updater
tools/update_readme_examples.py # old README example updater
tools/add_component_status.py   # one-off migration script
tools/merge_intent_into_components.py  # one-off migration script
```

**How to verify things work:**
```bash
# Load all components through the new framework
python3 -c "
from askee_ds import Loader, Theme, Renderer
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
- [ ] **Update `askee_ds/cli.py`**: Point CLI commands at new YAML loader.
      Currently cli.py uses the old `askee_ds.components` parser to validate
      the U+241F format. It needs a new `validate` command that loads
      `components/` via Loader and checks against `_schema.yaml`, plus a
      `preview` command that renders a named component with sample props.
      Keep the old validate/export/demo commands working for now but mark
      them as legacy.
- [ ] **Remove or archive `poc_renderer.py`**: Move to `_archive/`. The real
      package replaces it. The POC's embedded YAML definitions and demo()
      function are no longer needed.

## Phase 4 — Schema and validation

`components/_schema.yaml` has been written but is not yet enforced. It
defines valid field names, status values, prop types, render types, and
section types.

- [x] **`components/_schema.yaml`**: Written. Defines the meta-schema for
      component YAML files.
- [ ] **Schema validator** (`askee_ds/validator.py`): A module that reads
      `_schema.yaml` and validates component dicts against it. Should check:
      - Required fields present (category, description, status, render).
      - Status value is one of the allowed values.
      - Category starts with an allowed prefix (core/, game/).
      - All props have type and required fields.
      - Prop types are valid (string, integer, number, boolean, array).
      - Render type is valid (inline, join, box, reference).
      - Box sections use valid section types.
      - Returns a list of (component_name, error_message) tuples.
- [ ] **CLI integration**: Add `askee-ds-validate-yaml` command or update
      the existing `askee-ds-validate` to also validate the YAML structure.
- [ ] **Validate on load**: Optionally, the Loader can run validation and
      emit warnings (not errors) when loading components.

## Phase 5 — Prune and archive

The user said ~20-30 components are core and proven; the rest are speculative.
The user has NOT yet identified which specific components to keep vs archive.
**Ask the user** before pruning — do not decide unilaterally.

- [ ] **Identify core vs speculative**: Present the user with the full list
      of 63 components grouped by category and ask them to mark which are
      core. Alternatively, use the `status` field: `approved` components
      (currently 7: button.icon, breadcrumb.inline, card.simple,
      character-sheet.compact, choice-wheel.inline, counter.ammo,
      cooldown.row) are definitely core.
- [ ] **Move speculative to `_archive/components/`**: Components the user
      marks as speculative get moved. Keep the YAML format so they can be
      restored later.
- [ ] **Archive old format files**: Move `design/ascii/components.txt`,
      `design/ascii/format-spec.md`, `design/ascii/prop_shapes.yaml`,
      `design/ascii/askee_ds_tokens.yaml`, and `design/ascii/manifest.yaml`
      to `_archive/design-ascii/`. Keep `design/ascii/README.md` temporarily
      (update it to redirect to the new structure, or remove it).
      Keep `design/ascii/maps/` in place (maps are not migrated yet).
      Keep `design/ascii/box-drawing.yaml` in place temporarily (old tools
      may still reference it, and `askee_ds/box_drawing.py` loads from it).
      Keep `design/ascii/decoration-catalog.txt` in place (decorations are
      not migrated yet).
- [ ] **Archive retired tools**: Move to `_archive/tools/`:
      `component_visual_test.py`, `add_component_status.py`,
      `merge_intent_into_components.py`, `update_manifest.py`,
      `update_readme_examples.py`. Keep `parse_components.py`,
      `parse_decorations.py`, `parse_maps.py`, `render_demo.py` for now
      (they still work and CI uses them).

## Phase 6 — Update tooling and CI

- [ ] **Update CI** (`.github/workflows/tests.yml`):
      - Add a step that validates YAML component files (either via the new
        schema validator or just loading them all via Loader and checking
        for errors).
      - Add a step that renders all components with render specs and checks
        for runtime errors.
      - Keep old validation steps until old format files are archived.
      - Remove `docs/**` from the workflow path trigger (docs/ is gitignored).
- [ ] **Update or replace validators**: Once the schema validator exists,
      the old `parse_components.py --validate` can be replaced or kept as
      legacy. The new CLI should be the primary validation path.
- [ ] **Update tests** (`tests/test_package.py`):
      - Add tests for Loader (load_components_dir, load_tokens_dir).
      - Add tests for Renderer (render each section type, edge cases).
      - Add tests for Theme (color resolution, border resolution).
      - Add a test that loads all 63 components and renders those with
        render specs, asserting no exceptions.
      - Keep old tests working until old format is fully retired.
- [ ] **Add `tools/test_framework.py`**: Unit tests for the new framework
      modules (loader, renderer, theme, validator).
- [ ] **Remove npm dependency**: Drop `package.json` if all scripts are
      covered by Python CLI commands. The npm scripts were only convenience
      wrappers (`update:manifest`, `update:readme-examples`, `test`). If
      `update_manifest.py` is archived and the test command is just
      `python3 -m unittest discover`, package.json is no longer needed.

## Phase 7 — README and documentation

Do this LAST, when everything else is stable.

- [ ] **Rewrite README.md**: The current README (303 lines) describes the
      old project structure, old commands, and old format. Write a fresh
      README that covers:
      - What AskeeDS is (ASCII design system + framework for TUI games).
      - Who it's for (game designers, developers, Askee engine consumers).
      - The new file structure (components/, tokens/, askee_ds/).
      - Getting started: `from askee_ds import Loader, Theme, Renderer`.
      - How to add a new component (write YAML, add render spec).
      - How to validate (`askee-ds-validate` or equivalent).
      - How to use AskeeDS in another project (copy components/ + tokens/,
        or pip install, or git submodule).
      - Component examples (rendered output, not raw YAML).
      - Tools and dependencies (PyYAML, Textual optional, pyfiglet optional).
      - Versioning and changelog.
      - Remove ALL references to the U+241F format, `components.txt`,
        old tools, old workflows. The README should look like a fresh
        project.
- [ ] **Update or remove `design/ascii/README.md`**: If old format files are
      archived, this README should either redirect to the new structure or
      be removed/archived.
- [ ] **Update CHANGELOG.md**: Ensure all migration work is documented under
      Unreleased with user-facing language. When the migration is complete,
      consider bumping to `0.2.0` since the format change is significant
      (though not breaking for anyone using the Python API, which is
      experimental).

---

## Principles

- **Foundations first**: Get the format, loader, and renderer right before
  scaling to all components.
- **Scale**: Write render specs for all components once the renderer is proven.
- **Test**: Validate everything loads, renders, and roundtrips correctly.
- **Iterate**: Prune, archive, and clean up after the new system is solid.
- **Complete**: Update README and docs last, when the project is stable.

## Commit history (this migration)

```
b4edd13 feat(package): extract Loader, Theme, Renderer into askee_ds package
bee4d9d feat(framework): render specs for 46/63 components and new section types
c01e443 feat(framework): migrate 63 components to YAML and establish new structure
085d9ac feat(framework): add POC renderer proving YAML-first component architecture
```
