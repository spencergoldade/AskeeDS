"""
Minimal reference runtime for AskeeDS maps.

This script uses the packaged `askee_ds.maps` helpers to load and validate the
canonical maps, then prints a simple text preview with titles and usage.
"""

from __future__ import annotations

from pathlib import Path

from askee_ds import maps as maps_mod

# Consistent line length for report-style output
LINE_WIDTH = 60


def main() -> int:
    errors, warnings, parsed_maps = maps_mod.load_and_validate_default_maps()
    root = Path(__file__).resolve().parent.parent
    maps_path = root / "maps"

    # 1. Report title and status-first summary
    print("AskeeDS Map Preview")
    print()
    n_errors = len(errors)
    n_warnings = len(warnings)
    print(f"Maps: {len(parsed_maps)} loaded. Errors: {n_errors}. Warnings: {n_warnings}.")
    if parsed_maps:
        print(f"From: {maps_path}")
    print()

    # 2. Grouped errors and warnings
    if errors:
        print("Errors")
        print("-" * LINE_WIDTH)
        for e in errors:
            print(e)
        print()
    if warnings:
        print("Warnings")
        print("-" * LINE_WIDTH)
        for w in warnings:
            print(w)
        print()

    # 3. Maps section with card-like blocks
    if parsed_maps:
        print("Maps")
        print("=" * LINE_WIDTH)
        print()
        for i, m in enumerate(parsed_maps):
            width = m.get("width", 0)
            height = m.get("height", 0)
            header = (
                f"{m['id']}  (tileset={m['tileset_id']}, usage={m.get('usage')}, "
                f"{width}×{height})"
            )
            print(header)
            if m.get("title"):
                print(m["title"])
            if m.get("description"):
                print(m["description"])
            print("-" * LINE_WIDTH)
            for row in m["rows"]:
                print(row)
            if i < len(parsed_maps) - 1:
                print()
                print("-" * 40)
                print()

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
