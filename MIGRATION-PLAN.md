# AskeeDS v2 Migration Plan

Tracks the restructuring from the U+241F monolith format to the YAML-first
framework architecture. Check items off as they are completed.

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

## Phase 3 — Package extraction

- [ ] **Extract `askee_ds/loader.py`**: Move the Loader class from the POC into
      the real package so `from askee_ds import Loader` works.
- [ ] **Extract `askee_ds/renderer.py`**: Move the Renderer class into the
      package.
- [ ] **Extract `askee_ds/theme.py`**: Move the Theme class into the package.
- [ ] **Extract `askee_ds/layout.py`**: Box-drawing, text flow, alignment,
      padding utilities used by the renderer.
- [ ] **Update `askee_ds/cli.py`**: Point CLI commands (validate, export, demo)
      at the new YAML-based loader and renderer.
- [ ] **Update `pyproject.toml`**: Ensure entry points and dependencies reflect
      the new package structure.
- [ ] **Remove or archive `poc_renderer.py`**: The POC is replaced by the real
      package.

## Phase 4 — Schema and validation

- [ ] **`components/_schema.yaml`**: Meta-schema defining what a valid component
      YAML definition looks like. Enables validation without custom code.
- [ ] **Schema validator**: A tool or CLI command that validates all component
      YAML files against the schema.
- [ ] **Validate on load**: The Loader warns or errors when a component
      definition doesn't match the schema.

## Phase 5 — Prune and archive

- [ ] **Identify core vs speculative**: Review all 63 components. Mark ~20-30
      as core (proven, well-defined) and the rest as speculative.
- [ ] **Move speculative to `_archive/`**: Speculative components move out of
      `components/` into `_archive/components/` for reference.
- [ ] **Archive old format files**: Move `design/ascii/components.txt` and
      related old-format files to `_archive/`.
- [ ] **Archive retired tools**: Move `tools/component_visual_test.py` and
      one-off scripts to `_archive/tools/`.

## Phase 6 — Update tooling and CI

- [ ] **Update CI** (`.github/workflows/tests.yml`): Validate the new YAML
      component files and tokens instead of (or in addition to) the old format.
- [ ] **Update or replace validators**: Point `parse_components.py` and related
      tools at the new YAML structure, or replace with schema-based validation.
- [ ] **Update tests**: Ensure `tests/` and `tools/test_*.py` cover the new
      loader, renderer, and YAML structure.
- [ ] **Remove npm dependency**: Drop `package.json` if all scripts are
      covered by Python CLI commands.

## Phase 7 — README and documentation

- [ ] **Rewrite README.md**: Fresh README reflecting the new project structure,
      the YAML component format, the framework architecture, and updated
      getting-started instructions. Remove all references to the old U+241F
      format, old tooling, and retired workflows.
- [ ] **Update `design/ascii/README.md`**: Either remove or redirect to the
      new structure.
- [ ] **Update CHANGELOG.md**: Ensure all migration work is documented under
      Unreleased.

---

## Principles

- **Foundations first**: Get the format, loader, and renderer right before
  scaling to all components.
- **Scale**: Write render specs for all components once the renderer is proven.
- **Test**: Validate everything loads, renders, and roundtrips correctly.
- **Iterate**: Prune, archive, and clean up after the new system is solid.
- **Complete**: Update README and docs last, when the project is stable.
