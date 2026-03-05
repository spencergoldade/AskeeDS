"""
Command-line entry points for the AskeeDS Python package.

New commands (YAML pipeline):
    askee-ds validate          Validate YAML component definitions against the schema.
    askee-ds preview           Render a named component with sample props.

Legacy commands (old U+241F format, still working):
    askee-ds-validate          Validate components.txt, decorations, maps.
    askee-ds-export            Export legacy assets as JSON.
    askee-ds-demo              Render legacy component art.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import components as comp_mod
from . import decorations as deco_mod
from . import maps as maps_mod
from .loader import Loader
from .renderer import Renderer
from .theme import Theme
from .validator import Validator


def _default_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ── New YAML-based commands ─────────────────────────────────────────


def _resolve_paths(
    args: argparse.Namespace,
) -> tuple[Path, Path, Path]:
    """Resolve component dir, token dir, and schema file from args or defaults."""
    root = _default_root()
    comp_dir = Path(args.components) if args.components else root / "components"
    tok_dir = Path(args.tokens) if args.tokens else root / "tokens"
    schema = Path(args.schema) if args.schema else comp_dir / "_schema.yaml"
    return comp_dir, tok_dir, schema


def _add_path_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--components", metavar="DIR",
        help="Path to component YAML directory (default: components/)",
    )
    parser.add_argument(
        "--tokens", metavar="DIR",
        help="Path to token YAML directory (default: tokens/)",
    )
    parser.add_argument(
        "--schema", metavar="FILE",
        help="Path to _schema.yaml (default: components/_schema.yaml)",
    )


def main(argv: list[str] | None = None) -> int:
    """Unified CLI entry point: askee-ds <command>."""
    parser = argparse.ArgumentParser(
        prog="askee-ds",
        description="AskeeDS — ASCII design system framework CLI.",
    )
    sub = parser.add_subparsers(dest="command")

    # -- validate -------------------------------------------------------
    val_parser = sub.add_parser(
        "validate",
        help="Validate YAML component definitions against the schema.",
    )
    _add_path_args(val_parser)

    # -- preview --------------------------------------------------------
    prev_parser = sub.add_parser(
        "preview",
        help="Render a named component with sample props.",
    )
    prev_parser.add_argument(
        "name",
        help="Component name (e.g. room-card.default).",
    )
    prev_parser.add_argument(
        "--props", metavar="JSON",
        help="Props as a JSON string. If omitted, renders with empty/default props.",
    )
    _add_path_args(prev_parser)

    # -- list -----------------------------------------------------------
    list_parser = sub.add_parser(
        "list",
        help="List all component names, optionally filtered by status or prefix.",
    )
    list_parser.add_argument(
        "--status", metavar="STATUS",
        help="Filter to components with this status (e.g. approved).",
    )
    list_parser.add_argument(
        "--prefix", metavar="PREFIX",
        help="Filter to component names starting with this prefix.",
    )
    _add_path_args(list_parser)

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "preview":
        return _cmd_preview(args)
    if args.command == "list":
        return _cmd_list(args)

    parser.print_help()
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    comp_dir, _, schema_path = _resolve_paths(args)
    loader = Loader()

    if not comp_dir.is_dir():
        print(f"Error: component directory not found: {comp_dir}", file=sys.stderr)
        return 1
    if not schema_path.is_file():
        print(f"Error: schema file not found: {schema_path}", file=sys.stderr)
        return 1

    components = loader.load_components_dir(comp_dir)
    validator = Validator.from_schema_file(schema_path)
    errors = validator.validate_all(components)

    if errors:
        for name, msg in errors:
            print(f"  {name}: {msg}", file=sys.stderr)
        print(f"\n{len(errors)} error(s) in {len(components)} components.", file=sys.stderr)
        return 1

    print(f"OK — {len(components)} components validated, 0 errors.")
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    comp_dir, tok_dir, _ = _resolve_paths(args)
    loader = Loader()

    if not comp_dir.is_dir():
        print(f"Error: component directory not found: {comp_dir}", file=sys.stderr)
        return 1

    components = loader.load_components_dir(comp_dir)
    comp = components.get(args.name)
    if not comp:
        print(f"Error: component '{args.name}' not found.", file=sys.stderr)
        print(f"Available: {', '.join(sorted(components.keys()))}", file=sys.stderr)
        return 1

    tokens = loader.load_tokens_dir(tok_dir) if tok_dir.is_dir() else {}
    theme = Theme(tokens)
    renderer = Renderer(theme)

    props: dict = {}
    if args.props:
        try:
            props = json.loads(args.props)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid --props JSON: {exc}", file=sys.stderr)
            return 1

    output = renderer.render(comp, props)
    print(f"── {args.name} ({comp.status}) ──")
    print(output)
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    comp_dir, _, _ = _resolve_paths(args)
    loader = Loader()

    if not comp_dir.is_dir():
        print(f"Error: component directory not found: {comp_dir}", file=sys.stderr)
        return 1

    components = loader.load_components_dir(comp_dir)

    for name in sorted(components.keys()):
        comp = components[name]
        if args.status and comp.status != args.status:
            continue
        if args.prefix and not name.startswith(args.prefix):
            continue
        print(f"{name}  [{comp.status}]  {comp.description}")

    return 0


# ── Legacy commands (old U+241F format) ─────────────────────────────


def validate_main(argv: list[str] | None = None) -> int:
    """
    askee-ds-validate (legacy)

    Validate components, decorations, and maps from design/ascii/ files.
    """
    parser = argparse.ArgumentParser(
        description="[Legacy] Validate AskeeDS design assets (components, maps, decorations)."
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
        except Exception as exc:
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
    askee-ds-export (legacy)

    Export components, decorations, and maps as JSON to stdout.
    """
    parser = argparse.ArgumentParser(
        description="[Legacy] Export AskeeDS assets as JSON or list component names."
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
        help="Print component names as plain text instead of JSON.",
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
        _, _, map_data = maps_mod.load_and_validate_default_maps()
        out = {"maps": map_data}

    print(json.dumps(out, indent=2))
    return 0


def demo_main(argv: list[str] | None = None) -> int:
    """
    askee-ds-demo (legacy)

    Render a small selection of canonical components as ASCII art.
    """
    parser = argparse.ArgumentParser(
        description="[Legacy] Render example AskeeDS components for quick visual inspection."
    )
    parser.add_argument(
        "--component", "-c", action="append", dest="components",
        help="Component name to render. May be provided multiple times.",
    )
    parser.add_argument(
        "--prefix", "-p", action="append", dest="prefixes",
        help="Render all components whose names start with this prefix.",
    )
    args = parser.parse_args(argv)

    root = _default_root()
    path = root / "design" / "ascii" / "components.txt"
    if not path.exists():
        path = root / "_archive" / "design-ascii" / "components.txt"
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
        seen: set[str] = set()
        unique: list[str] = []
        for name in demo_names:
            if name not in seen:
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
        if name == "typography.banner":
            try:
                from askee_ds.banner import render_banner_text
                text = "AskeeDS"
                style_hint = "splash"
                rendered = render_banner_text(text, style_hint=style_hint, max_height=10)
                if rendered is not None:
                    art = rendered
            except ImportError:
                pass
        print(art.rstrip() if art else "")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
