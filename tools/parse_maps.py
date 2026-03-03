#!/usr/bin/env python3
"""
AskeeDS ASCII map parser and validator.

Uses design/ascii/maps/index.yaml and design/ascii/map-tiles.yaml to:
  - Validate authored ASCII maps.
  - Ensure characters map to known tiles.
  - Optionally output JSON for engines and tools.

Usage:
  python tools/parse_maps.py --validate
  python tools/parse_maps.py --json
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - handled gracefully at runtime
    yaml = None  # type: ignore[assignment]


MAX_LINE_LENGTH = 80


@dataclass
class Tileset:
    id: str
    chars_to_tiles: Dict[str, str]


@dataclass
class MapDefinition:
    id: str
    file: Path
    tileset_id: str
    title: str | None
    description: str | None
    usage: str | None
    width_hint: int | None
    height_hint: int | None


def _require_yaml() -> None:
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to parse map index and tiles. Install with `pip install pyyaml`."
        )


def load_tilesets(tiles_path: Path) -> Dict[str, Tileset]:
    """Load tilesets from design/ascii/map-tiles.yaml and validate basic schema."""
    _require_yaml()
    data = yaml.safe_load(tiles_path.read_text(encoding="utf-8"))  # type: ignore[arg-type]
    tilesets: Dict[str, Tileset] = {}

    if not isinstance(data, dict):
        raise RuntimeError("map-tiles.yaml must contain a top-level mapping")

    all_tiles: Dict[str, dict] = data.get("tiles", {}) or {}
    if not isinstance(all_tiles, dict):
        raise RuntimeError("map-tiles.yaml: 'tiles' must be a mapping of tile ids to definitions")

    tilesets_data = data.get("tilesets", {}) or {}
    if not isinstance(tilesets_data, dict):
        raise RuntimeError("map-tiles.yaml: 'tilesets' must be a mapping of tileset ids to configs")

    default_tileset = data.get("default_tileset")
    if default_tileset and default_tileset not in tilesets_data:
        raise RuntimeError(
            f"map-tiles.yaml: default_tileset {default_tileset!r} is not defined in tilesets"
        )

    # Validate tile definitions (minimal schema: single-character 'char').
    for tile_id, tile in all_tiles.items():
        if not isinstance(tile, dict):
            raise RuntimeError(f"map-tiles.yaml: tile {tile_id!r} must be a mapping")
        ch = tile.get("char")
        if not isinstance(ch, str) or len(ch) != 1:
            raise RuntimeError(
                f"map-tiles.yaml: tile {tile_id!r} must define a single-character 'char' field"
            )

    for tileset_id, ts in tilesets_data.items():
        if not isinstance(ts, dict):
            raise RuntimeError(f"map-tiles.yaml: tileset {tileset_id!r} must be a mapping")
        tile_ids: List[str] = ts.get("tiles", []) or []
        if not isinstance(tile_ids, list):
            raise RuntimeError(
                f"map-tiles.yaml: tileset {tileset_id!r} 'tiles' must be a list of tile ids"
            )
        mapping: Dict[str, str] = {}
        for tile_id in tile_ids:
            if tile_id not in all_tiles:
                raise RuntimeError(
                    f"map-tiles.yaml: tileset {tileset_id!r} references unknown tile id {tile_id!r}"
                )
            tile = all_tiles[tile_id]
            ch = tile.get("char")
            # At this point we know 'char' is a valid one-character string from the loop above.
            assert isinstance(ch, str) and len(ch) == 1  # for type checkers
            # If multiple tiles share a char, keep the first and let validation
            # of authored maps warn about ambiguous semantics if needed.
            mapping.setdefault(ch, tile_id)
        tilesets[tileset_id] = Tileset(id=tileset_id, chars_to_tiles=mapping)

    return tilesets


def load_map_index(index_path: Path, maps_dir: Path) -> List[MapDefinition]:
    """Load map definitions from design/ascii/maps/index.yaml with basic schema checks."""
    _require_yaml()
    data = yaml.safe_load(index_path.read_text(encoding="utf-8"))  # type: ignore[arg-type]
    if not isinstance(data, dict):
        raise RuntimeError("maps/index.yaml must contain a top-level mapping")
    maps_section = data.get("maps", {}) or {}
    if not isinstance(maps_section, dict):
        raise RuntimeError("maps/index.yaml: 'maps' must be a mapping of map ids to configs")
    results: List[MapDefinition] = []

    for map_id, cfg in maps_section.items():
        file_rel = cfg.get("file")
        if not file_rel:
            continue
        file_path = maps_dir / file_rel
        results.append(
            MapDefinition(
                id=map_id,
                file=file_path,
                tileset_id=str(cfg.get("tileset") or ""),
                title=cfg.get("title"),
                description=cfg.get("description"),
                usage=cfg.get("usage"),
                width_hint=cfg.get("width"),
                height_hint=cfg.get("height"),
            )
        )

    return results


def parse_map_file(path: Path) -> Tuple[List[str], int, int]:
    """
    Parse a single ASCII map file into rows, width, and height.

    Empty trailing lines are ignored; empty files yield ([], 0, 0).
    """
    text = path.read_text(encoding="utf-8")
    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip() != ""]
    if not lines:
        return [], 0, 0
    width = max(len(ln) for ln in lines)
    height = len(lines)
    return lines, width, height


def validate_maps(
    tilesets: Dict[str, Tileset], maps: List[MapDefinition]
) -> Tuple[List[str], List[str], List[dict]]:
    """
    Validate maps against tilesets and basic layout rules.

    Returns (errors, warnings, parsed_maps_json_ready).
    """
    errors: List[str] = []
    warnings: List[str] = []
    parsed_maps: List[dict] = []

    for m in maps:
        if not m.file.exists():
            errors.append(f"{m.id}: map file not found: {m.file}")
            continue

        if not m.tileset_id:
            warnings.append(f"{m.id}: missing tileset id in index.yaml")
            continue

        tileset = tilesets.get(m.tileset_id)
        if not tileset:
            errors.append(f"{m.id}: tileset {m.tileset_id!r} not defined in map-tiles.yaml")
            continue

        rows, width, height = parse_map_file(m.file)
        if width == 0 or height == 0:
            warnings.append(f"{m.id}: map file {m.file} is empty")
            continue

        if m.width_hint is not None and m.width_hint != width:
            warnings.append(
                f"{m.id}: width hint {m.width_hint} does not match actual width {width}"
            )
        if m.height_hint is not None and m.height_hint != height:
            warnings.append(
                f"{m.id}: height hint {m.height_hint} does not match actual height {height}"
            )

        for row_idx, row in enumerate(rows, start=1):
            if len(row) != width:
                warnings.append(
                    f"{m.id}: row {row_idx} has width {len(row)} but expected {width}; maps should be rectangular"
                )
            if len(row) > MAX_LINE_LENGTH:
                warnings.append(
                    f"{m.id}: row {row_idx} exceeds {MAX_LINE_LENGTH} chars ({len(row)})"
                )
            for col_idx, ch in enumerate(row, start=1):
                if ch == " ":
                    warnings.append(
                        f"{m.id}: row {row_idx}, col {col_idx} contains space; prefer explicit tile chars"
                    )
                    continue
                if ch not in tileset.chars_to_tiles:
                    errors.append(
                        f"{m.id}: row {row_idx}, col {col_idx} uses unknown char {ch!r} "
                        f"for tileset {m.tileset_id}"
                    )

        parsed_maps.append(
            {
                "id": m.id,
                "file": str(m.file),
                "tileset_id": m.tileset_id,
                "title": m.title,
                "description": m.description,
                "usage": m.usage,
                "width": width,
                "height": height,
                "rows": rows,
            }
        )

    return errors, warnings, parsed_maps


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and optionally export AskeeDS ASCII maps."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON description of maps to stdout"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Run validator; exit 1 if any errors"
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    tiles_path = root / "design" / "ascii" / "map-tiles.yaml"
    index_path = root / "design" / "ascii" / "maps" / "index.yaml"
    maps_dir = index_path.parent

    try:
        tilesets = load_tilesets(tiles_path)
        maps = load_map_index(index_path, maps_dir)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    errs, warns, parsed_maps = validate_maps(tilesets, maps)

    if args.validate or not args.json:
        for e in errs:
            print("Error:", e, file=sys.stderr)
        for w in warns:
            print("Warning:", w, file=sys.stderr)

    if args.json:
        print(json.dumps({"maps": parsed_maps}, indent=2))

    if args.validate:
        print(
            f"Valid: {len(parsed_maps)} maps ({len(warns)} warnings)",
            file=sys.stderr,
        )
        return 0 if not errs else 1

    # Default: just validation output and exit code.
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())

