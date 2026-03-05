# Changelog

All notable changes to AskeeDS will be documented in this file.

## [Unreleased]

### Added

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

### Fixed

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
