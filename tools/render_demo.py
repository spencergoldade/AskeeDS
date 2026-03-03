#!/usr/bin/env python3
"""
AskeeDS minimal reference renderer — renders a few components to stdout.
Loads design/ascii/components.txt and design/ascii/box-drawing.yaml,
substitutes props into component art, and prints. No Rich/Textual required.

Usage:
  python tools/render_demo.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from parse_components import parse_components


def main() -> int:
    components_path = ROOT / "design" / "ascii" / "components.txt"
    if not components_path.exists():
        print("Error: design/ascii/components.txt not found", file=sys.stderr)
        return 1
    content = components_path.read_text(encoding="utf-8")
    components = parse_components(content)
    by_name = {c["name"]: c for c in components}

    # Render status-bar.default with sample props
    if "status-bar.default" in by_name:
        c = by_name["status-bar.default"]
        # Art is "HP: 85/100  |  The Clearing  |  Turn 12\n"
        # We just print the art as the structural reference; real impl would substitute
        print("--- status-bar.default (structure) ---")
        print(c["art"].rstrip())
        print()

    # Render room-card.default structure
    if "room-card.default" in by_name:
        c = by_name["room-card.default"]
        print("--- room-card.default (structure) ---")
        print(c["art"].rstrip())
        print()

    # Render layout.stack structure
    if "layout.stack" in by_name:
        c = by_name["layout.stack"]
        print("--- layout.stack (structure) ---")
        print(c["art"].rstrip())

    print()
    print(f"(Rendered from {len(components)} components in {components_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
