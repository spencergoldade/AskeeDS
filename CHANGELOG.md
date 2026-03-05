# Changelog

All notable changes to AskeeDS will be documented in this file.

## [Unreleased]

### Added

- **Framework POC** (`poc_renderer.py`): Self-contained proof-of-concept demonstrating the proposed AskeeDS v2 architecture — YAML component definitions with typed props and declarative render specs, a token-based theme system, and a renderer that produces real ASCII output from definition + props + theme. Covers four components (button, status bar, character sheet, room card) spanning inline to complex box layouts with text wrapping, conditional lists, and resource bars.

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
