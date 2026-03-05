#!/usr/bin/env python3
"""
AskeeDS component library parser and validator.
Reads design/ascii/components.txt (or given path), parses components, validates,
and optionally outputs JSON.

Usage:
  python tools/parse_components.py [paths...]
  python tools/parse_components.py --json [paths...]
  python tools/parse_components.py --validate [paths...]

When multiple paths are provided, components are merged in order; later files
override earlier ones by component name (use this for project-specific
overrides files).

This script delegates to askee_ds.components for parsing and validation so
tools and package stay in sync.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from askee_ds.components import (
    COMPONENT_STATUSES,
    DELIMITER,
    parse_components,
    parse_props_meta,
    validate,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse and optionally validate/export AskeeDS component library."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Component file paths (default: design/ascii/components.txt)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--validate", action="store_true", help="Run validator; exit 1 if any errors"
    )
    args = parser.parse_args()

    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [ROOT / "design" / "ascii" / "components.txt"]

    for path in paths:
        if not path.exists():
            print(f"Error: not found: {path}", file=sys.stderr)
            return 1

    merged: dict = {}
    order: list = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        comps = parse_components(content)
        for c in comps:
            name = c["name"]
            if name not in merged:
                order.append(name)
            merged[name] = c

    components = [merged[name] for name in order]
    if args.validate:
        errs, warns = validate(components)
        for e in errs:
            print("Error:", e, file=sys.stderr)
        for w in warns:
            print("Warning:", w, file=sys.stderr)
        if errs:
            return 1
        print(
            f"Valid: {len(components)} components ({len(warns)} warnings)",
            file=sys.stderr,
        )
        return 0
    if args.json:
        out = {
            "components": [
                {"name": c["name"], "meta": c["meta"], "art": c["art"]}
                for c in components
            ]
        }
        print(json.dumps(out, indent=2))
        return 0
    # Default: parse and report
    errs, warns = validate(components)
    for e in errs:
        print("Error:", e, file=sys.stderr)
    for w in warns:
        print("Warning:", w, file=sys.stderr)
    print(f"Parsed {len(components)} components", file=sys.stderr)
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
