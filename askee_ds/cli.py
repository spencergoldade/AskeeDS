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

    Validate components, decorations, and maps. By default, runs against the
    repo layout (design/ascii, etc.). For non-repo layouts, pass explicit
    paths.
    """
    parser = argparse.ArgumentParser(description="Validate AskeeDS design assets.")
    parser.add_argument(
        "--kind",
        choices=["components", "decorations", "maps", "all"],
        default="all",
        help="Which assets to validate (default: all)",
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

    Export components, decorations, and maps as JSON to stdout.
    """
    parser = argparse.ArgumentParser(description="Export AskeeDS assets as JSON.")
    parser.add_argument(
        "--kind",
        choices=["components", "decorations", "maps"],
        default="components",
        help="Which assets to export (default: components)",
    )
    args = parser.parse_args(argv)

    if args.kind == "components":
        comps = comp_mod.load_default_components()
        out = {"components": comps}
    elif args.kind == "decorations":
        decos = deco_mod.load_default_decorations()
        out = {"decorations": decos}
    else:
        _, _, maps = maps_mod.load_and_validate_default_maps()
        out = {"maps": maps}

    print(json.dumps(out, indent=2))
    return 0


def demo_main(argv: list[str] | None = None) -> int:  # noqa: ARG001
    """
    askee-ds-demo

    Render a small selection of canonical components as a structural reference.
    """
    root = _default_root()
    path = root / "design" / "ascii" / "components.txt"
    content = path.read_text(encoding="utf-8")
    comps = comp_mod.parse_components(content)
    index = {c["name"]: c for c in comps}

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

