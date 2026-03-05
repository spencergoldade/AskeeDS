# Archived: design/ascii/ (old format files)

## What this was

These files formed the original AskeeDS component library, which used a
custom U+241F (␟) delimiter format to define components as freeform ASCII art
blocks with inline metadata. The ecosystem around it included:

- **components.txt** — The 2257-line monolith containing all 63 component
  definitions in the U+241F format. Each component had meta lines (description,
  props, status) followed by ASCII art.
- **components.txt.bak** — Backup copy created during migration.
- **format-spec.md** — Formal grammar for the U+241F format (component
  boundaries, meta lines, art blocks).
- **prop_shapes.yaml** — Separate file defining prop shapes for array and
  object props, referenced by components.
- **askee_ds_tokens.yaml** — Color role IDs and default TUI palette. This
  was the committed token source before `tokens/` was created.
- **manifest.yaml** — List of component names for tooling discovery.
- **PROP-INTENT-AND-TEST-DATA-PLAN.md** — Planning doc for prop intent
  metadata and test data generation.
- **version.txt** — Version tracking for the old format.
- **README.md** — The original README describing how to parse and author
  components in the U+241F format.

## Why it was archived

The U+241F format was replaced by structured YAML component definitions
under `components/` (15 files, 63 components with typed props and
declarative render specs). The new format is:

- Machine-readable without a custom parser
- Validated against a schema (`components/_schema.yaml`)
- Directly consumed by the `askee_ds` framework (Loader, Renderer, Theme)

The old format's responsibilities are now covered by:

| Old file | Replaced by |
|----------|-------------|
| components.txt | `components/core/*.yaml` + `components/game/*.yaml` |
| format-spec.md | `components/_schema.yaml` (machine-enforced) |
| prop_shapes.yaml | Inline `props:` blocks in each component YAML |
| askee_ds_tokens.yaml | `tokens/colors.yaml`, `tokens/box-drawing.yaml`, `tokens/typography.yaml` |
| manifest.yaml | Directory structure is the manifest; `askee-ds list` for discovery |

## Files NOT archived (still in design/ascii/)

- **maps/** — Map layouts and index. Maps have not been migrated yet.
- **map-tiles.yaml** — Tileset definitions for maps. Still in use.
- **box-drawing.yaml** — Legacy box-drawing loader (`askee_ds/box_drawing.py`)
  still reads from this path. Replaced by `tokens/box-drawing.yaml` for the
  new framework, but kept until the legacy module is retired.
- **decoration-catalog.txt** — Decoration definitions. Decorations have not
  been migrated yet.

## When it is safe to delete this folder

This archive can be deleted when all of the following are true:

1. No code in `askee_ds/` references `design/ascii/components.txt` at its
   old or archived path (check `askee_ds/components.py`).
2. CI no longer runs `parse_components.py --validate` against the old format.
3. Maps and decorations have been migrated to their own YAML structure.
4. You are confident no one needs the old format as a historical reference.

At that point, the old `askee_ds/components.py` legacy parser module can also
be removed.
