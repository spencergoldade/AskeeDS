"""
Minimal reference runtime for AskeeDS maps.

This script uses the packaged `askee_ds.maps` helpers to load and validate the
canonical maps, then prints a simple text preview with titles and usage.
"""

from __future__ import annotations

from pathlib import Path

from askee_ds import maps as maps_mod


def main() -> int:
    errors, warnings, parsed_maps = maps_mod.load_and_validate_default_maps()
    root = Path(__file__).resolve().parent.parent

    for w in warnings:
        print(f"[warning] {w}")
    for e in errors:
        print(f"[error] {e}")

    print()
    print(f"Loaded {len(parsed_maps)} maps from {root / 'design' / 'ascii' / 'maps'}")
    print()

    for m in parsed_maps:
        print("=" * 80)
        header = f"{m['id']}  (tileset={m['tileset_id']}, usage={m.get('usage')})"
        print(header)
        if m.get("title"):
            print(m["title"])
        if m.get("description"):
            print(m["description"])
        print("-" * 80)
        for row in m["rows"]:
            print(row)
        print()

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

