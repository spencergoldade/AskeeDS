# Changelog

All notable changes to AskeeDS will be documented in this file.

## [Unreleased]

### Added

- **Declarative sizing model**: Components can now declare adaptive width and height via their render spec. `width: fill` expands to available space, `width: content` sizes to content, and integer values remain fixed (backwards-compatible). Optional `min_width`, `max_width`, `min_height`, `max_height` constraints clamp the result. New `askee_ds/sizing.py` resolver, `tokens/sizing.yaml` with terminal defaults, `available_width`/`available_height` on `RenderContext`, and Renderer/Composer pass-through. 25 new sizing tests.
- **Interaction spec**: Components can now declare interaction behavior via an `interaction` block: `focusable`, `actions` (with named keyboard bindings), and `scrollable`. Three approved interactive components annotated (`button.text`, `button.icon`, `choice-wheel.inline`). Validator enforces valid fields, key names, and action structure. Textual adapter reads `focusable` and sets `can_focus` on widgets. Replaces the old boolean `interactive` field. 11 new tests (98 total, all green).
- **Component catalog audit**: Reviewed all 53 ideated components against stated game genres. Archived 3 speculative components (`icon.placeholder`, `quick-select.radial`, `decoration.placeholder`). Consolidated 4 near-duplicates into 2 (`notification.inline` replaces achievement+loot; `hint-bar.contextual` absorbs interactions variant). Updated `menu.main` to use proper `interaction` block. Defined proving criteria for `ideated → approved` promotion. 58 components total (10 approved, 48 ideated).
- **16 example game screens** composed as YAML under `screens/examples/`: 3 title screens (centered, bordered, left-aligned), 2 conversation views (full-width, split with stats), 3 adventure play screens (stacked, two-column, shell), 3 open world play screens (map-dominant, split, with entities), 2 credits screens (single card, stacked sections), 3 game menu tabs (items, stats, quests). Each demonstrates a different layout approach using the same approved components.
- **14 components proved and promoted to approved**: `layout.stack`, `layout.two-column`, `narrative-log.pane`, `entity-list.room`, `minimap.default`, `menu.main`, `nav.vertical`, `inventory.list`, `speech-bubble`, `hint-bar.contextual`, `feedback.success`, `feedback.error`, `typography.banner`, `tracker.objective`. Each has focused tests and a snapshot golden file. 24 approved components total (from 10). 157 total tests.
- **Snapshot testing**: Golden-file visual regression tests for all 24 approved components. Each renders with canonical props and compares against a `.txt` file in `tests/snapshots/`. Regenerate with `UPDATE_SNAPSHOTS=1`. 119 total tests (109 functional + 10 snapshots).
- **Declarative screen composition**: Designers can now define full game screens as YAML files (`screens/`) that reference layout components and fill their slots with component references, nested layouts, or plain text. New `Composer.compose_screen()` loads and renders screen YAML. CLI `askee-ds compose` renders screens from the terminal. Example screen `screens/examples/adventure_main.yaml` demonstrates a complete text adventure layout. 11 new tests (109 total, all green).

### Fixed

- **Layout junction characters**: `render_stack` now uses shared separator borders (`├`/`┤`) between blocks instead of double top/bottom corners. `render_columns` and `render_shell` use proper junction characters (`┬`/`┴`) at column splits. Correct rendering for all three border styles (single, heavy, double).
- **`narrative-log.pane`**: Fixed broken template `" {}"` → `" {label}"` so list items are actually interpolated.
- **`progress-bar.horizontal`**: Changed from broken `inline` type (which can't compute bar fill) to `box` with a `progress` section that correctly renders the bar.
- **`hint-bar.contextual`**: `join` renderer now interpolates the `prefix` field against props, so `prefix: "{prefix}"` correctly resolves to the prop value.
- **`element_type` on `PropDef`**: Added `element_type` field to `PropDef` and parsing in the Loader. Components using `element_type` (e.g. `table.fourcolumn`, `spinner.loading`, `narrative-log.pane`) now generate correct sample data in `all_components.py`.

### Changed

- **Layout render types are now responsive**: `render_stack`, `render_columns`, and `render_shell` use `ctx.available_width` via `resolve_width` instead of sizing from content. Layouts propagate available width to children for proper responsive behavior.
- **8 components migrated to adaptive sizing**: `status-bar.default`, `room-card.default`, `narrative-log.pane`, `entity-list.room`, `modal.overlay`, `character-sheet.compact`, `menu.main`, `card.simple` now use `width: fill` with `min_width`/`max_width` constraints instead of fixed integers. They reflow to the available terminal width while staying within readable bounds.
- **Consolidated `speech-bubble.left` + `speech-bubble.right`** into a single `speech-bubble` component with a `tail` prop (`left` or `right`, defaults to `left`). Bubble renderer reads tail from props first, spec as fallback.
- **Removed `menu.pause`** — `menu.main` with `title: "Paused"` handles this case identically. 56 components total (24 approved, 32 ideated).
- **Renamed `tokens/box-drawing.yaml` → `tokens/borders.yaml`** for clarity.

### Documentation

- **README**: Replaced "What AskeeDS does not do" list with a designer-centric comparison table ("AskeeDS handles the look / Your engine handles the logic"). Updated component counts (56 total, 24 approved) and file tree (17 example screens).
- **GUIDE.md**: Updated component counts, added adaptive sizing details for the 8 migrated components, and noted the 17 example screens across 6 gameplay contexts.
- **REFERENCE.md**: Expanded `element_type` documentation and added adaptive sizing note.
- **Private sizing guide**: Created `docs/sizing-guide.md` (gitignored) — a plain-language walkthrough for the designer explaining when and how to use `fill`, `content`, fixed widths, and min/max constraints.

### Documentation

- **Documentation restructured into audience-specific guides**: Split the monolithic README into four root-level files. `GUIDE.md` is a designer-first walkthrough (concepts, vocabulary, step-by-step tutorials — zero Python, YAML only). `REFERENCE.md` is a structured lookup for all 16 render types, 11 section types, 10 color roles, interaction fields, and every component/prop/screen field. `INTEGRATING.md` is the developer guide covering Python API, CLI reference, Rich and Textual adapters, render type extension, and project adoption patterns. `README.md` slimmed to a concise landing page with Quick Start links by role.
- Deleted stale `design/README.md` (referenced archived files).
- Added "What AskeeDS does not do" section to README (8 explicit scope boundaries).
- Rewrote ROADMAP.md for v3 direction: completed items summary and prioritized next steps.

- **Registry-based renderer**: Refactored the monolithic 520-line `renderer.py` into a thin dispatcher backed by a pluggable render type registry (`askee_ds/render_types/`). Each of the 16 render types is now a standalone module. Consumers can register custom render types via `Renderer.register_type()` or `from askee_ds.render_types import register` without modifying framework source. Zero regressions — all 62 renderable components produce identical output.
- **Pytest test suite**: Migrated from unittest to pytest. Split the monolithic 574-line `test_framework.py` into 7 focused modules (`test_loader`, `test_theme`, `test_renderer`, `test_composer`, `test_validator`, `test_adapters`, `test_cli`). Added `conftest.py` with session-scoped fixtures. 62 tests (9 new CLI tests), runs in ~0.6s. CI updated to use pytest.

### Removed

- **Maps and decorations evicted**: `maps/` and `decorations/` archived to `_archive/` — these are game content, not design system primitives. The render capabilities (`charmap`, `art_lookup`) remain and accept any data passed at runtime. `load_decorations()` removed from Loader. CI path triggers updated.
- **Validated color roles**: Replaced free-form `color_hint` (e.g. `status.good/warning/danger`) with `default_color_role` — a validated field that must reference an actual color role from `tokens/colors.yaml` (neutral, danger, arcane, nature, frost, success, rare, legendary, dungeon, forest). Schema, Validator, Loader, and Rich adapter all updated. Components can still accept a runtime `color_role` prop to override the default.

---

## [0.2.0] — 2026-03-05

### Added

- **Batch A specialized renderers**: 5 new render/section types — `active_list` (nav with selection marker), `clock` (segment progress), `stage_track` (multi-stage horizontal track), `banner` (Figlet text with fallback), `frames` (static frame from animation sequence). 51/63 components (81%) now renderable.
- **6 new framework tests** for the Batch A render types; 36 framework + package tests total.
- **Batch B specialized renderers**: 6 new render types — `table` (auto-width columns), `bubble` (speech bubbles with directional tail), `tree` (recursive tree with `├──`/`└──`/`│` connectors), `grid` (bordered inventory cells), `charmap` (2D character grid + legend), `art_lookup` (decoration art fallback). 59/63 components (94%) now renderable.
- **7 new framework tests** for Batch B render types; 43 framework + package tests total.
- **`examples/quick_start.py`**: Minimal hello-world demonstrating the YAML-first framework (Loader → Theme → Renderer).
- **`examples/all_components.py`**: Visual catalog rendering all 59 non-reference components with auto-generated sample props.

- **Composer** (`askee_ds/composer.py`): New `Composer` class renders child components bottom-up and passes the results as props to layout components. Supports string pass-through, `(component_name, props)` tuples, and lists of either. Exported from `askee_ds`.
- **Layout render types**: 3 new render types — `stack` (vertically stacked bordered blocks), `columns` (side-by-side panes with border), `shell` (header + sidebar + content). All 3 layout components now renderable; 62/63 components render from declarative specs (98%).
- **8 new tests** for layout render types and Composer (5 Composer, 3 renderer); 52 total tests.
- **Rich adapter** (`askee_ds/adapters/rich.py`): Colorizes rendered ASCII output using Theme color roles. Box-drawing chars get border color, content text gets foreground color, highlighted tokens (HP:, Exits:, checkboxes) get accent color. Optional dependency: `pip install askee-ds[rich]`.
- **`examples/full_screen.py`**: Composed full-screen game UI using the Composer — demonstrates `layout.app.shell` and `layout.stack` with nested child components.
- **4 new tests** for Rich adapter; 56 total tests.
- **Textual adapter** (`askee_ds/adapters/textual.py`): `AskeeWidget` wraps themed Rich output as a Textual `Static` widget. Factory methods `from_component()` and `from_text()` for quick mounting. Optional dependency: `pip install askee-ds[textual]`.
- **`examples/textual_app.py`**: Live TUI demo with sidebar nav, quest tracker, status bar, room card, and command input — all themed AskeeDS widgets in a Textual layout.
- **2 new tests** for Textual adapter; 58 total tests.

### Changed

- **Version 0.2.0**: Bumped from 0.1.0 to 0.2.0 — the framework is now the primary API.

- **Maps relocated**: `design/ascii/maps/` moved to top-level `maps/`; `design/ascii/map-tiles.yaml` moved to `maps/tiles.yaml`. The maps parser, CLI tool, and example all use the new paths with legacy fallback.
- **Decorations converted to YAML**: `design/ascii/decoration-catalog.txt` (U+241F format, 23 decorations) converted to `decorations/catalog.yaml`. New `Loader.load_decorations()` method loads the catalog. The `art_lookup` render type now looks up art by `art_id` from the catalog with width/height cropping.
- **Box-drawing consolidated**: `askee_ds/box_drawing.py` now loads from `tokens/box-drawing.yaml` instead of the archived legacy file.
- **`design/ascii/` eliminated**: All three remaining files archived to `_archive/design-ascii/`; the directory no longer exists.
- **Decoration catalog typo fixed**: `decoration.shield.simple` used U+27DF instead of U+241F for the notes line; fixed before conversion.

### Documentation

- **README updated** to reflect current state: render types table expanded from 4 to 14 entries, component counts updated (59/63 renderable), examples directory added to file tree, `all_components.py` mentioned alongside CLI preview commands.
- **Commit rule expanded** to assess `README.md` alongside `CHANGELOG.md` before every commit, keeping shipped documentation in sync with code changes.

- **Framework roadmap** (`ROADMAP.md`): Feature plan with full agent context, principles, file structure, verification commands, and workspace rules. Covers specialized renderers (batches A/B/C), component composition, runtime adapters, maps/decorations migration, examples, packaging, and legacy retirement.
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

### Removed

- **Legacy modules archived**: `askee_ds/components.py`, `askee_ds/decorations.py`, `askee_ds/maps.py`, `askee_ds/box_drawing.py`, `askee_ds/_paths.py` moved to `_archive/legacy-modules/`. The framework API (`Loader`, `Renderer`, `Theme`, `Composer`) replaces all of these.
- **Legacy tools archived**: `tools/parse_components.py`, `tools/parse_decorations.py`, `tools/parse_maps.py`, `tools/render_demo.py`, and their tests moved to `_archive/tools/`. The `tools/` directory removed.
- **Legacy CLI entries removed**: `askee-ds-validate`, `askee-ds-export`, `askee-ds-demo` removed from `pyproject.toml`. Only `askee-ds` CLI remains.
- **Legacy imports removed**: `__init__.py` no longer re-exports `components`, `decorations`, `maps`, `box_drawing`.
- **`tests/test_package.py` removed**: Legacy parser tests; framework tests in `test_framework.py` cover all current functionality.
- **`design/readme-examples.json` deleted**: Orphaned file from the old format.
- **`visual-test` optional dependency group removed**: Archived with the visual test TUI.
- **`examples/map_preview.py` archived**: Used the legacy maps API; moved to `_archive/tools/`.
- **Migration plan deleted**: `MIGRATION-PLAN.md` removed — all 7 phases complete, context preserved in `ROADMAP.md` and git history.

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
