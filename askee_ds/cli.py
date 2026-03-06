"""
Command-line entry points for the AskeeDS Python package.

    askee-ds validate          Validate YAML component definitions against the schema.
    askee-ds preview           Render a named component with sample props.
    askee-ds list              List all component names.
    askee-ds compose           Render a screen from a YAML screen definition.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .composer import Composer
from .loader import Loader
from .renderer import Renderer
from .theme import Theme
from .validator import Validator


def _default_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ── New YAML-based commands ─────────────────────────────────────────


def _resolve_paths(
    args: argparse.Namespace,
) -> tuple[Path, Path, Path, Path]:
    """Resolve component dir, token dir, schema file, and themes dir from args or defaults."""
    root = _default_root()
    comp_dir = Path(args.components) if args.components else root / "components"
    tok_dir = Path(args.tokens) if args.tokens else root / "tokens"
    schema = Path(args.schema) if args.schema else comp_dir / "_schema.yaml"
    themes_dir = Path(args.themes) if getattr(args, "themes", None) else root / "themes"
    return comp_dir, tok_dir, schema, themes_dir


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
    parser.add_argument(
        "--themes", metavar="DIR",
        help="Path to theme YAML directory (default: themes/)",
    )


def _add_theme_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--theme", metavar="NAME",
        choices=["dark", "light", "high-contrast", "experimental"],
        help="Theme variant: dark, light, high-contrast (grayscale), or experimental (color).",
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
    _add_theme_arg(prev_parser)

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

    # -- compose --------------------------------------------------------
    compose_parser = sub.add_parser(
        "compose",
        help="Render a screen from a YAML screen definition.",
    )
    compose_parser.add_argument(
        "screen",
        help="Path to a screen YAML file (e.g. screens/examples/adventure_main.yaml).",
    )
    compose_parser.add_argument(
        "--width", metavar="N", type=int,
        help="Override available width (default: from screen YAML or 100).",
    )
    _add_path_args(compose_parser)
    _add_theme_arg(compose_parser)

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
    if args.command == "compose":
        return _cmd_compose(args)

    parser.print_help()
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    comp_dir, _, schema_path, _ = _resolve_paths(args)
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
    comp_dir, tok_dir, _, themes_dir = _resolve_paths(args)
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
    if getattr(args, "theme", None) and themes_dir.is_dir():
        overlay = loader.load_theme(args.theme, themes_dir)
        if overlay:
            tokens = {**tokens, **overlay}
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
    comp_dir, _, _, _ = _resolve_paths(args)
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


def _cmd_compose(args: argparse.Namespace) -> int:
    comp_dir, tok_dir, _, themes_dir = _resolve_paths(args)
    screen_path = Path(args.screen)

    if not screen_path.is_file():
        print(f"Error: screen file not found: {screen_path}", file=sys.stderr)
        return 1
    if not comp_dir.is_dir():
        print(f"Error: component directory not found: {comp_dir}", file=sys.stderr)
        return 1

    loader = Loader()
    components = loader.load_components_dir(comp_dir)
    tokens = loader.load_tokens_dir(tok_dir) if tok_dir.is_dir() else {}
    if getattr(args, "theme", None) and themes_dir.is_dir():
        overlay = loader.load_theme(args.theme, themes_dir)
        if overlay:
            tokens = {**tokens, **overlay}
    theme = Theme(tokens)
    renderer = Renderer(theme)
    composer = Composer(renderer, components)

    width = args.width if hasattr(args, "width") and args.width else None
    output = composer.compose_screen(screen_path, available_width=width)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
