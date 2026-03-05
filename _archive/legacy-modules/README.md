# Archived: Legacy askee_ds Modules

## What these were

These modules formed the original (pre-v2) API for parsing and loading
AskeeDS assets from the old `design/ascii/` directory. They used:

- **components.py** — U+241F delimiter parser for `components.txt`.
- **decorations.py** — U+241F parser for `decoration-catalog.txt`.
- **maps.py** — Map index and tileset loader from `design/ascii/maps/`.
- **box_drawing.py** — Box-drawing character set loader from `design/ascii/`.
- **_paths.py** — `repo_root()` helper used by all of the above.

## Why they were archived

The v2 framework replaces all of these:

| Old module | Replaced by |
|------------|-------------|
| components.py | `askee_ds.loader.Loader.load_components_dir()` |
| decorations.py | `askee_ds.loader.Loader.load_decorations()` |
| maps.py | Maps relocated to `maps/`; still loaded by legacy tools (archived) |
| box_drawing.py | `askee_ds.theme.Theme` loads `tokens/box-drawing.yaml` |
| _paths.py | No longer needed; explicit paths are passed |

## When it is safe to delete

When no external code references `from askee_ds import components` (etc.)
and the `_archive/tools/` legacy scripts are also no longer needed.
