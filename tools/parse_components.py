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
from collections import Counter
from pathlib import Path

DELIMITER = "\u241f"  # U+241F SYMBOL FOR UNIT SEPARATOR
COMPONENT_PREFIX = DELIMITER * 3 + " COMPONENT: "
META_PREFIX = DELIMITER + " "
MAX_LINE_LENGTH = 80

COMPONENT_STATUSES = {
    "Ideated",
    "To Do",
    "In Progress",
    "In Review",
    "Approved",
    "Cancelled",
    "Deprecated",
}

_NAME_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)+$")


def _parse_props_meta(raw: str) -> list[dict]:
    """
    Parse a ␟ props: meta value into a structured list.

    The raw format is a comma‑separated list, e.g.:
      "title, body_text_optional, items[]"

    Each entry is converted into:
      {
        "name": "body_text",
        "optional": True,
        "is_array": False,
        "raw": "body_text_optional",
      }
    """
    props: list[dict] = []
    if not raw:
        return props
    for token in (part.strip() for part in raw.split(",") if part.strip()):
        optional = False
        is_array = False
        base = token
        if base.endswith("[]"):
            is_array = True
            base = base[:-2]
        if base.endswith("_optional"):
            optional = True
            base = base[: -len("_optional")]
        if not base:
            continue
        props.append(
            {
                "name": base,
                "optional": optional,
                "is_array": is_array,
                "raw": token,
            }
        )
    return props


def parse_props_meta(raw: str) -> list[dict]:
    """Public alias for _parse_props_meta; used by tools such as component_visual_test."""
    return _parse_props_meta(raw)


def parse_components(content: str) -> list[dict]:
    """Parse component library text into a list of component dicts."""
    components = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(COMPONENT_PREFIX):
            name = line[len(COMPONENT_PREFIX) :].strip()
            meta: dict[str, str] = {}
            i += 1
            while i < len(lines) and lines[i].startswith(META_PREFIX) and not lines[i].startswith(DELIMITER * 3):
                meta_line = lines[i][len(META_PREFIX) :]
                if ": " in meta_line:
                    key, _, value = meta_line.partition(": ")
                    meta[key.strip()] = value.strip()
                i += 1
            art_lines: list[str] = []
            while i < len(lines):
                candidate = lines[i]
                # Stop art block at the next component boundary.
                if candidate.startswith(COMPONENT_PREFIX):
                    break
                # Stop art block at section headers like "---------- Templates ----------"
                # so they are not treated as part of the previous component's example.
                if candidate.startswith("---------- ") and candidate.rstrip().endswith("----------"):
                    break
                art_lines.append(candidate)
                i += 1
            art = "\n".join(art_lines) if art_lines else ""
            components.append({"name": name, "meta": meta, "art": art})
        else:
            i += 1
    return components


def validate(components: list[dict]) -> tuple[list[str], list[str]]:
    """
    Run validation rules. Returns (errors, warnings).

    Errors are critical (e.g. ␟ in art). Warnings flag issues that should be
    fixed for high‑quality implementations but do not necessarily break parsers.
    """
    errors = []
    warnings = []
    seen_names: Counter[str] = Counter()

    for c in components:
        name = c["name"]
        meta = c.get("meta", {})
        art = c.get("art", "")

        # Component name quality
        seen_names[name] += 1
        if not _NAME_RE.match(name):
            warnings.append(
                f"{name}: component name should use dot notation like category.variant "
                "(lowercase, no spaces)"
            )

        # Required meta
        description = meta.get("description", "").strip()
        props_raw = meta.get("props", "").strip()
        if not description:
            warnings.append(f"{name}: missing ␟ description:")
        if not props_raw:
            warnings.append(f"{name}: missing ␟ props: (or explicit 'none')")

        # Component status
        status = meta.get("component-status", "").strip()
        if status and status not in COMPONENT_STATUSES:
            errors.append(
                f"{name}: invalid component-status {status!r}; must be one of: "
                + ", ".join(sorted(COMPONENT_STATUSES))
            )
        if status == "Deprecated" and not meta.get("replaced-by", "").strip():
            errors.append(
                f"{name}: component-status Deprecated requires ␟ replaced-by: <component name>"
            )
        if not status:
            warnings.append(f"{name}: missing ␟ component-status:")

        # Structured props parsing – catches obvious authoring mistakes.
        parsed_props = _parse_props_meta(props_raw)
        if props_raw and not parsed_props:
            warnings.append(f"{name}: ␟ props: could not be parsed into prop entries")
        for p in parsed_props:
            prop_name = p["name"]
            if " " in p["raw"]:
                warnings.append(
                    f"{name}: prop token {p['raw']!r} should not contain spaces; "
                    "use comma‑separated snake_case names"
                )
            if not re.fullmatch(r"[a-z0-9_]+", prop_name):
                warnings.append(
                    f"{name}: prop name {prop_name!r} should be snake_case (lowercase, digits, underscores)"
                )

        # Art constraints
        if DELIMITER in art:
            errors.append(f"{name}: ASCII art must not contain ␟ (U+241F)")
        for j, ln in enumerate(art.splitlines()):
            if len(ln) > MAX_LINE_LENGTH:
                warnings.append(f"{name}: line {j + 1} exceeds {MAX_LINE_LENGTH} chars ({len(ln)})")

    # Duplicate components (usually from merged overrides) should be intentional.
    for comp_name, count in seen_names.items():
        if count > 1:
            warnings.append(f"{comp_name}: defined {count} times in merged input; later entries override earlier ones")

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
