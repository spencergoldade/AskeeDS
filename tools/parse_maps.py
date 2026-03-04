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

This script delegates to askee_ds.maps for loading and validation.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from askee_ds.maps import load_map_index, load_tilesets, validate_maps


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

    tiles_path = ROOT / "design" / "ascii" / "map-tiles.yaml"
    index_path = ROOT / "design" / "ascii" / "maps" / "index.yaml"
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

    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
