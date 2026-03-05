# design/ascii/

Most of the original files in this folder have been archived to
`_archive/design-ascii/`. The component library now lives in `components/`
as structured YAML, and design tokens live in `tokens/`.

## What remains here

| File / Folder | Status |
|---------------|--------|
| **maps/** | Active. Map layouts and index. Not yet migrated. |
| **map-tiles.yaml** | Active. Tileset definitions for maps. |
| **box-drawing.yaml** | Legacy. Still loaded by `askee_ds/box_drawing.py`. Replaced by `tokens/box-drawing.yaml` for the new framework. |
| **decoration-catalog.txt** | Active. Decoration definitions. Not yet migrated. |

## Where things moved

| Old location | New location |
|-------------|-------------|
| `components.txt` | `components/core/*.yaml` + `components/game/*.yaml` |
| `askee_ds_tokens.yaml` | `tokens/colors.yaml`, `tokens/box-drawing.yaml`, `tokens/typography.yaml` |
| `manifest.yaml` | No longer needed; use `askee-ds list` |
| `format-spec.md` | `components/_schema.yaml` (machine-enforced) |
| `prop_shapes.yaml` | Inline `props:` in each component YAML |
