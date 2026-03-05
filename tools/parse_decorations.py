#!/usr/bin/env python3
"""
AskeeDS decorative ASCII art catalog parser and validator.

Reads design/ascii/decoration-catalog.txt (or given path), parses entries, validates,
and optionally outputs JSON.

Usage:
  python tools/parse_decorations.py [paths...]
  python tools/parse_decorations.py --json [paths...]
  python tools/parse_decorations.py --validate [paths...]

When multiple paths are provided, entries are merged in order; later files
override earlier ones by art id.

This script delegates to askee_ds.decorations for parsing and validation.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from askee_ds.decorations import parse_decorations, validate_decorations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse and optionally validate/export AskeeDS decoration catalog."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Decoration catalog paths (default: design/ascii/decoration-catalog.txt)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--validate", action="store_true", help="Run validator; exit 1 if any errors"
    )
    args = parser.parse_args()

    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        default = ROOT / "design" / "ascii" / "decoration-catalog.txt"
        if not default.exists():
            default = ROOT / "_archive" / "design-ascii" / "decoration-catalog.txt"
        paths = [default]

    for path in paths:
        if not path.exists():
            print(f"Error: not found: {path}", file=sys.stderr)
            return 1

    merged: dict[str, dict] = {}
    order: list[str] = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        entries = parse_decorations(content)
        for entry in entries:
            art_id = entry["id"]
            if art_id not in merged:
                order.append(art_id)
            merged[art_id] = entry

    decorations = [merged[art_id] for art_id in order]

    if args.validate:
        errs, warns = validate_decorations(decorations)
        for e in errs:
            print("Error:", e, file=sys.stderr)
        for w in warns:
            print("Warning:", w, file=sys.stderr)
        if errs:
            return 1
        print(
            f"Valid: {len(decorations)} decorations ({len(warns)} warnings)",
            file=sys.stderr,
        )
        return 0

    if args.json:
        out = {
            "decorations": [
                {"id": d["id"], "meta": d.get("meta", {}), "art": d.get("art", "")}
                for d in decorations
            ]
        }
        print(json.dumps(out, indent=2))
        return 0

    errs, warns = validate_decorations(decorations)
    for e in errs:
        print("Error:", e, file=sys.stderr)
    for w in warns:
        print("Warning:", w, file=sys.stderr)
    print(f"Parsed {len(decorations)} decorations", file=sys.stderr)
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
