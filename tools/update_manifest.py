#!/usr/bin/env python3
"""
Regenerate design/ascii/manifest.yaml from design/ascii/components.txt.

This treats components.txt as the single source of truth for component names
and writes a deterministic manifest file for tooling and discovery.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = ROOT / "design" / "ascii" / "components.txt"
MANIFEST_PATH = ROOT / "design" / "ascii" / "manifest.yaml"


def main() -> int:
    try:
        from tools.parse_components import parse_components  # type: ignore[import]
    except Exception:
        # Fallback to relative import when run via `python3 tools/update_manifest.py`.
        sys.path.insert(0, str(ROOT / "tools"))
        from parse_components import parse_components  # type: ignore[import]

    if not COMPONENTS_PATH.exists():
        print(f"Error: components file not found: {COMPONENTS_PATH}", file=sys.stderr)
        return 1

    content = COMPONENTS_PATH.read_text(encoding="utf-8")
    components = parse_components(content)
    names = sorted({c["name"] for c in components})

    header = """# AskeeDS — Component library manifest
# List of component names for tooling and discovery. Source file is the
# component library (components.txt). If the library is split later, list
# file and section per component here. In the future, `sources: [...]` can be
# used to list multiple component files (for example core + overrides).

source: components.txt

components:
"""
    lines = [header]
    for name in names:
        lines.append(f"  - {name}\n")

    new_contents = "".join(lines)

    # Avoid rewriting the file when contents are identical (idempotent).
    if MANIFEST_PATH.exists():
        current = MANIFEST_PATH.read_text(encoding="utf-8")
        if current == new_contents:
            return 0

    MANIFEST_PATH.write_text(new_contents, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

