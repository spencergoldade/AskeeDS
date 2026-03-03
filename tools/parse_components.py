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
"""

import argparse
import json
import re
import sys
from pathlib import Path

DELIMITER = "\u241f"  # U+241F SYMBOL FOR UNIT SEPARATOR
COMPONENT_PREFIX = DELIMITER * 3 + " COMPONENT: "
META_PREFIX = DELIMITER + " "
MAX_LINE_LENGTH = 80


def parse_components(content: str) -> list[dict]:
    """Parse component library text into a list of component dicts."""
    components = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(COMPONENT_PREFIX):
            name = line[len(COMPONENT_PREFIX) :].strip()
            meta = {}
            i += 1
            while i < len(lines) and lines[i].startswith(META_PREFIX) and not lines[i].startswith(DELIMITER * 3):
                meta_line = lines[i][len(META_PREFIX) :]
                if ": " in meta_line:
                    key, _, value = meta_line.partition(": ")
                    meta[key.strip()] = value.strip()
                i += 1
            art_lines = []
            while i < len(lines) and not lines[i].startswith(COMPONENT_PREFIX):
                art_lines.append(lines[i])
                i += 1
            art = "\n".join(art_lines) if art_lines else ""
            components.append({"name": name, "meta": meta, "art": art})
        else:
            i += 1
    return components


def validate(components: list[dict]) -> tuple[list[str], list[str]]:
    """Run validation rules. Returns (errors, warnings). Errors are critical (e.g. ␟ in art)."""
    errors = []
    warnings = []
    for c in components:
        name = c["name"]
        meta = c.get("meta", {})
        art = c.get("art", "")
        if not meta.get("description"):
            warnings.append(f"{name}: missing ␟ description:")
        if "props" not in meta and not meta.get("description"):
            warnings.append(f"{name}: missing ␟ props: (or ␟ description:)")
        if DELIMITER in art:
            errors.append(f"{name}: ASCII art must not contain ␟ (U+241F)")
        for j, ln in enumerate(art.splitlines()):
            if len(ln) > MAX_LINE_LENGTH:
                warnings.append(f"{name}: line {j + 1} exceeds {MAX_LINE_LENGTH} chars ({len(ln)})")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and optionally validate/export AskeeDS component library.")
    parser.add_argument("paths", nargs="*", help="Component file paths (default: design/ascii/components.txt)")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--validate", action="store_true", help="Run validator; exit 1 if any errors")
    args = parser.parse_args()

    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [Path(__file__).resolve().parent.parent / "design" / "ascii" / "components.txt"]

    for path in paths:
        if not path.exists():
            print(f"Error: not found: {path}", file=sys.stderr)
            return 1

    merged = {}
    order = []
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
        print(f"Valid: {len(components)} components ({len(warns)} warnings)", file=sys.stderr)
        return 0
    if args.json:
        out = {"components": [{"name": c["name"], "meta": c["meta"], "art": c["art"]} for c in components]}
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
