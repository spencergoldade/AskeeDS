# Changelog

All notable changes to AskeeDS will be documented in this file.

## [Unreleased]

### Added

- **README rewritten**: Fresh README for the YAML-first framework. Covers getting started (CLI + Python API), rendered component examples, how to add components, render types, status lifecycle, and adoption patterns. All references to the old format removed.
- **Framework tests** (`tests/test_framework.py`): 25 tests covering Loader, Renderer, Theme, and Validator — including a test that renders every non-reference component to catch regressions.
- **Schema validator** (`askee_ds/validator.py`): Validates all 63 YAML component definitions against `components/_schema.yaml`. Checks required fields, status values, category prefixes, prop types, render types, border values, and section types.
- **Unified CLI** (`askee-ds`): New `validate`, `preview`, and `list` subcommands using the YAML pipeline. Legacy commands (`askee-ds-validate`, `askee-ds-export`, `askee-ds-demo`) kept for backward compatibility.
- **Validate-on-load**: `Loader(schema_path=...)` optionally runs schema validation when loading components, emitting warnings to stderr.
- **Framework POC** (`poc_renderer.py`): Self-contained proof-of-concept demonstrating the proposed AskeeDS v2 architecture — YAML component definitions with typed props and declarative render specs, a token-based theme system, and a renderer that produces real ASCII output from definition + props + theme. Covers four components (button, status bar, character sheet, room card) spanning inline to complex box layouts with text wrapping, conditional lists, and resource bars.
- **YAML component definitions** (`components/`): All 63 components migrated from the U+241F format to structured YAML, split into 15 category files across `components/core/` (6 files: layouts, buttons, inputs, feedback, navigation, display) and `components/game/` (9 files: hud, inventory, character, exploration, conversation, trackers, notifications, menus, screens). Each component has typed props, status, reference art, and (for 4 proven components) declarative render specs.
- **Design tokens** (`tokens/`): Canonical color roles (`tokens/colors.yaml`), box-drawing character sets (`tokens/box-drawing.yaml`), and typography conventions (`tokens/typography.yaml`) extracted from the old `design/ascii/` files into the new top-level token directory.
- **Migration tool** (`tools/migrate.py`): Converts `components.txt` (U+241F format) to category-split YAML files. Supports dry run, per-component preview, and write modes.
- **Render specs for 46/63 components**: Declarative render specs covering inline, box, join, numbered_list, checked_list, bars, and progress section types. Components render from definition + props + theme without hardcoded branches.
- **New renderer section types**: `join` (inline array join with separator), `numbered_list` (1. 2. 3. prefixes), `checked_list` ([x]/[ ] prefixes), `progress` (single progress bar).
- **Framework package** (`askee_ds/`): Extracted Loader, Theme, and Renderer into the real package. `from askee_ds import Loader, Theme, Renderer` works end-to-end. Legacy parser modules kept for backward compatibility.

- **Renderer audit**: Explicit renderers for 20+ previously unrendered components (notifications, screens, speech bubbles, trackers, panels, grid, radial, nav, header, status icons, spinner, divider, icon placeholder). All now respond to prop edits and randomization in the visual test.
- Intent metadata (purpose, default-view, randomized-view, prop-types, edge-cases) for 6 components that were missing it: `status-icon.row`, `cooldown.badge`, `cooldown.row`, `notification.achievement`, `notification.loot`, `feedback.mixed`.
- **color_role support**: Component visual test applies `color_role` to the preview (background, text, border). Default and random prop values for `color_role`; palette and role list from `design/ascii/askee_ds_tokens.yaml`.
- **AskeeDS token file** (`design/ascii/askee_ds_tokens.yaml`): Canonical source for color role ids and default TUI palette. Values may be copied from local design token files; this file is the only token source committed to the repo.
- Component visual test: approve (A), unapprove (U), and set-status (S) from browser and detail screens; status persisted to `design/ascii/components.txt`.
- Component visual test: status picker modal to choose any component status; popup closes after selection.
- Component visual test: toggleable overview pane (O) on detail screen showing purpose, default-view, randomized-view, prop-types, and edge-cases in a scrollable pane.
- Component visual test TUI for interactive preview of components and props.
- Component statuses and component count tooling.
- Decoration extension; component descriptions and examples in the manifest.
- Mapping modules for map tiles and decorations.
- Responsive capability for box-contained items in the visual test.
- Package-level tests and CI run of package tests.
- Decoration validation; unified component art block parsing.
- Ko-fi funding option in README.
- Figlet and color support in the visual test.

### Changed

- **Old format archived**: `components.txt`, `format-spec.md`, `prop_shapes.yaml`, `askee_ds_tokens.yaml`, `manifest.yaml`, and related files moved to `_archive/design-ascii/`. Maps, decorations, and box-drawing remain in `design/ascii/` (not yet migrated).
- **Retired tools archived**: Visual test TUI, migration scripts, and manifest updater moved to `_archive/tools/`. Legacy parsers (`parse_components.py`, `parse_maps.py`, `parse_decorations.py`) kept for now.
- **Archive READMEs**: Each archive folder documents what was archived, why, and when it is safe to delete.
- **CI updated**: Primary validation uses `askee-ds validate` (YAML pipeline). Added render-all step. Removed old component validation. Path triggers updated.
- **npm removed**: `package.json` deleted; all scripts covered by Python CLI.
- **Component status reset**: 53 non-approved components reset from `in-review` to `ideated`. 10 approved components unchanged. Components re-enter the lifecycle from the earliest state.
- **POC archived**: `poc_renderer.py` moved to `_archive/`; the real `askee_ds` package now covers all its functionality.
- **CLI rewritten**: `askee_ds/cli.py` now has a unified `askee-ds` entry point alongside the legacy commands.
- README and instructional updates.
- Component, prop, and control model and docs; major prop wiring and minor prop research.
- General refactor and readability improvements; experimental CLI.
- `update_manifest` now uses `askee_ds.components` (T-8).
- Map typing normalized to Python 3.9+ style (T-7).
- `parse_decorations` and `parse_maps` delegated to `askee_ds` (T-5, T-6).
- Added `askee_ds._paths.repo_root` and use in package modules.
- Map preview and visual test UX improvements.
- Testing tool updates.
- Resolved `components.txt` and project-agnostic color token wording (merge).

### Changed

- `tracker.objective` spec updated to use `label`/`checked` keys (matching implementation and `prop_shapes.yaml`).
- `cooldown.badge` renderer now shows `label` before the badge when provided.
- `counter.score` reference art corrected to show a single instance.
- `toast.inline` renderer now uses `variant` prop to show a prefix symbol.
- `room-card.default` renderer now wires `entity_list[]` into the preview.

### Fixed

- Visual test crash (`BadIdentifier`) when components use informal prop notation with parentheses; prop widget IDs are now sanitized.
- `cooldown.badge` preview not reflecting `turns_left` prop changes (missing renderer branch).
- `counter.score` now formats numeric values with thousands-separator commas matching reference art.
- `divider.horizontal` and `spinner.loading` props cleaned up from informal `(none or style)` notation to proper `style_hint_optional`.
- `decoration.placeholder` gains `art_id` prop so art is loaded from the decoration catalog and cropped to `width`/`height`.
- Parser treating section headings as part of the previous component.
- Manifest and components getting out of sync.
- Table component border and minor component display issues in visual test.
- Visual test: removed Props fallback, value-only substitution, and padding behavior.
- Git: added `setup-local-git.sh` and commit wrapper to avoid trailer/alias errors.

### Removed / Ignored

- Stopped tracking various local-only config and design paths; added to `.gitignore`.
- Ignore Python bytecode and `__pycache__`.

### Documentation

- Marked `add_component_status` as historical (T-10).

---

## [0.1.0] - Initial design-system extraction

- Establish `design/ascii/` as the source of truth for the AskeeDS ASCII design system (components, box-drawing, map tiles, manifest, format spec).
- Add local design token guidance for TUI semantic color roles.
- Add parser/validator and JSON export (`tools/parse_components.py`) plus demo and tests.
- Define adoption and update strategy (see README and CHANGELOG).
