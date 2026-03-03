# AskeeDS — ASCII design folder

This folder is the **source of truth** for the AskeeDS ASCII-based design system: box-drawing characters, map tiles, component manifest, and the component library.

## Contents

| File | Purpose |
|------|---------|
| **box-drawing.yaml** | Approved border characters (light/heavy/double). Load in code; do not hardcode in component art. |
| **map-tiles.yaml** | Character/role sets for minimap, grid, and world/encounter maps (empty, wall, door, river, player, etc.), plus metadata and adjacency hints for procedural generation. |
| **manifest.yaml** | List of component names for tooling and discovery; points to the component library file. |
| **components.txt** | Component library: consumer/author directions, PROP SHAPES, and all components with meta + ASCII art. |
| **maps/** | Optional ASCII map layouts (`*.txt`) and index/metadata (`index.yaml`) for world maps, dungeons, encounters, and engine-only layouts. |

## How to parse the component library

- **Component start:** Line beginning with three U+241F (␟) then `COMPONENT: ` followed by the component name (e.g. `layout.app.shell`, `room-card.default`).
- **Meta:** Lines beginning with one ␟ then a key and value (e.g. `␟ props: ...`, `␟ description: ...`). Meta applies to the component that follows the previous component boundary.
- **ASCII art:** Everything after the meta block, until the next `␟␟␟` line, is the component's ASCII art.
- **Constraint:** Do not use the character ␟ (U+241F) inside ASCII art. Parsers split on ␟ to find boundaries and meta.

Formal grammar: component boundary = line starting with `␟␟␟ COMPONENT: <name>`; meta = lines starting with `␟ <key>: <value>`; art = everything after the meta block until the next `␟␟␟` or EOF. See [format-spec.md](format-spec.md) for the full format spec.

## How to add components

1. Open **components.txt** and find the right section (atoms, molecules, game — menus, etc.).
2. Add a new block: `␟␟␟ COMPONENT: category.variant`, then meta lines (`␟ description:`, `␟ props:`, etc.), then the ASCII art. Use only characters from **box-drawing.yaml** for borders (or the documented exception for decoration.placeholder).
3. Add the component name to **manifest.yaml**.
4. If you introduce new list/object shapes, add them to the PROP SHAPES section in components.txt (and any `␟ shape:` on the component).

## Maps: tilesets, layouts, and systems

ASCII maps in AskeeDS are split into three concepts:

- **Map tilesets** (`map-tiles.yaml`): Define what each symbol or role id means (for example floor, wall, river, door, player), plus metadata such as walkability, visibility, tags, and adjacency hints for procedural generation.
- **Map layouts** (`maps/*.txt`): Plain-text grids of characters authored by designers. Each file is a rectangular grid that references symbols from one tileset and can be used as a playable area, world overview, encounter template, or engine-only configuration.
- **Map systems** (implementation-side): Code that consumes tilesets and layouts to handle movement, visibility, pathfinding, fog-of-war, and procedural generation. The design folder defines contracts and examples; engines implement behavior.

Recommended file structure for maps:

- `design/ascii/map-tiles.yaml` — canonical tilesets and symbol metadata.
- `design/ascii/maps/` — folder for map layouts and metadata:
  - `design/ascii/maps/index.yaml` — optional index mapping map ids to filenames, tilesets, and usage (`engine_only`, `ui_minimap`, `world_map`, and so on).
  - `design/ascii/maps/*.txt` — ASCII map layouts (80×N or smaller). Lines are raw grid data; avoid using the ␟ delimiter in map bodies.

Engines are encouraged to:

- Validate that every character in a layout has a corresponding tile definition in `map-tiles.yaml`.
- Treat map files as **data**, not code: parse into a 2D array plus metadata that can be consumed from any language.
- Optionally use the adjacency hints from `map-tiles.yaml` to drive procedural generation or validation (for example ensure rivers connect and walls are contiguous).

## Overrides and project-specific components

- Treat `components.txt` as the **core, upstream AskeeDS file**. Avoid editing it directly in consumer projects.
- Put project-specific components and overrides in a separate file (for example `design/ascii/overrides.txt` or `design/ascii/project-components.txt`).
- When parsing or validating, load core first and overrides second so overrides win for duplicate names (for example: `python tools/parse_components.py --validate design/ascii/components.txt design/ascii/overrides.txt`).

In the future, `manifest.yaml` and tooling can list multiple sources (for example `sources: [components.txt, project-components.txt]`) to formalize this layering pattern.


## Related docs

- [docs/ascii-design-system.md](../../docs/ascii-design-system.md) — AskeeDS overview, features, component groups.
- [docs/ascii-reference.txt](../../docs/ascii-reference.txt) — ASCII code point reference (U+0000–U+007F) and design-system delimiter note.
- [design/tokens/colors.md](../tokens/colors.md) — Semantic color tokens for the TUI.
- [tools/parse_components.py](../../tools/parse_components.py) — Parser/validator and JSON export (`python tools/parse_components.py --validate` or `--json`).
- [tools/render_demo.py](../../tools/render_demo.py) — Minimal reference renderer (prints a few components to stdout).
- [tools/test_parse_components.py](../../tools/test_parse_components.py) — Parser tests (`python tools/test_parse_components.py`).
