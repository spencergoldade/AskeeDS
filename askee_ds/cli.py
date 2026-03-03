"""
Command-line entry points for the AskeeDS Python package.

These commands are intentionally minimal and designed to work both from a
checkout of the repo and, with explicit paths, from installed environments.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import components as comp_mod
from . import decorations as deco_mod
from . import maps as maps_mod


def _default_root() -> Path:
    return Path(__file__).resolve().parent.parent


def validate_main(argv: list[str] | None = None) -> int:
    """
    askee-ds-validate

    Validate components, decorations, and maps.

    This is the quickest way for authors to check that edits to
    design/ascii/ files are structurally sound before wiring them into
    a game or tool.
    """
    parser = argparse.ArgumentParser(
        description="Validate AskeeDS design assets (components, maps, decorations)."
    )
    parser.add_argument(
        "--kind",
        choices=["components", "decorations", "maps", "all"],
        default="all",
        help=(
            "Which assets to validate (default: all). "
            "Use 'components' after editing components.txt, 'maps' after editing maps/, "
            "or 'decorations' after editing decoration-catalog.txt."
        ),
    )
    args = parser.parse_args(argv)

    root = _default_root()
    exit_code = 0

    if args.kind in ("components", "all"):
        comps = comp_mod.load_default_components()
        cerrs, cwarns = comp_mod.validate(comps)
        for e in cerrs:
            print("Component error:", e, file=sys.stderr)
        for w in cwarns:
            print("Component warning:", w, file=sys.stderr)
        if cerrs:
            exit_code = 1

    if args.kind in ("decorations", "all"):
        decos = deco_mod.load_default_decorations()
        derrs, dwarns = deco_mod.validate_decorations(decos)
        for e in derrs:
            print("Decoration error:", e, file=sys.stderr)
        for w in dwarns:
            print("Decoration warning:", w, file=sys.stderr)
        if derrs:
            exit_code = 1

    if args.kind in ("maps", "all"):
        try:
            merrs, mwarns, _ = maps_mod.load_and_validate_default_maps()
        except Exception as exc:  # pragma: no cover - environment dependent
            print(f"Map validation error: {exc}", file=sys.stderr)
            return 1
        for e in merrs:
            print("Map error:", e, file=sys.stderr)
        for w in mwarns:
            print("Map warning:", w, file=sys.stderr)
        if merrs:
            exit_code = 1

    return exit_code


def export_main(argv: list[str] | None = None) -> int:
    """
    askee-ds-export

    Export components, decorations, and maps as JSON to stdout, or list component
    names for quick discovery.
    """
    parser = argparse.ArgumentParser(
        description="Export AskeeDS assets as JSON or list component names."
    )
    parser.add_argument(
        "--kind",
        choices=["components", "decorations", "maps"],
        default="components",
        help="Which assets to export (default: components)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "When used with --kind components, print component names (and optional "
            "descriptions) as plain text instead of JSON."
        ),
    )
    args = parser.parse_args(argv)

    if args.kind == "components":
        comps = comp_mod.load_default_components()
        if args.list:
            for c in comps:
                meta = c.get("meta") or {}
                desc = meta.get("description", "").strip()
                if desc:
                    print(f"{c['name']}: {desc}")
                else:
                    print(c["name"])
            return 0
        out = {"components": comps}
    elif args.kind == "decorations":
        decos = deco_mod.load_default_decorations()
        out = {"decorations": decos}
    else:
        _, _, maps = maps_mod.load_and_validate_default_maps()
        out = {"maps": maps}

    print(json.dumps(out, indent=2))
    return 0


def demo_main(argv: list[str] | None = None) -> int:
    """
    askee-ds-demo

    Render a small selection of canonical components as a structural reference.

    By default this prints a curated sample; you can also choose specific
    components or filter by name prefix.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Render example AskeeDS components as ASCII for quick visual inspection."
        )
    )
    parser.add_argument(
        "--component",
        "-c",
        action="append",
        dest="components",
        help=(
            "Component name to render (for example room-card.default). "
            "May be provided multiple times."
        ),
    )
    parser.add_argument(
        "--prefix",
        "-p",
        action="append",
        dest="prefixes",
        help=(
            "Render all components whose names start with this prefix "
            "(for example game --prefix inventory. --prefix screen.)."
        ),
    )
    args = parser.parse_args(argv)

    root = _default_root()
    path = root / "design" / "ascii" / "components.txt"
    content = path.read_text(encoding="utf-8")
    comps = comp_mod.parse_components(content)
    index = {c["name"]: c for c in comps}

    demo_names: list[str]
    if args.components or args.prefixes:
        demo_names = []
        if args.components:
            demo_names.extend(args.components)
        if args.prefixes:
            for name in sorted(index.keys()):
                if any(name.startswith(prefix) for prefix in args.prefixes):
                    demo_names.append(name)
        # Deduplicate while preserving order.
        seen: set[str] = set()
        unique: list[str] = []
        for name in demo_names:
            if name in seen:
                continue
            seen.add(name)
            unique.append(name)
        demo_names = unique
    else:
        demo_names = [
            "layout.app.shell",
            "room-card.default",
            "status-bar.default",
        ]

    for name in demo_names:
        comp = index.get(name)
        if not comp:
            continue
        print("=" * 80)
        print(name)
        print("-" * 80)
        art = comp.get("art", "") or ""
        print(art)
        print()

    return 0


if __name__ == "__main__":  # pragma: no cover
    # Allow `python -m askee_ds.cli` for local testing.
    raise SystemExit(validate_main())

