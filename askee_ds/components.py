"""
Library access to the AskeeDS component library parser and validator.

These functions mirror the behavior of tools/parse_components.py but are
packaged for reuse.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable

DELIMITER = "\u241f"  # U+241F SYMBOL FOR UNIT SEPARATOR
COMPONENT_PREFIX = DELIMITER * 3 + " COMPONENT: "
META_PREFIX = DELIMITER + " "
MAX_LINE_LENGTH = 80

_NAME_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)+$")


def repo_root() -> Path:
    """
    Best-effort guess of the repository root when running from a package.

    For installed packages, callers should pass explicit paths instead of
    relying on this helper.
    """
    return Path(__file__).resolve().parent.parent


def _parse_props_meta(raw: str) -> list[dict]:
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


def parse_components(content: str) -> list[dict]:
    """Parse component library text into a list of component dicts."""
    components: list[dict] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(COMPONENT_PREFIX):
            name = line[len(COMPONENT_PREFIX) :].strip()
            meta: dict[str, str] = {}
            i += 1
            while i < len(lines) and lines[i].startswith(META_PREFIX) and not lines[i].startswith(
                DELIMITER * 3
            ):
                meta_line = lines[i][len(META_PREFIX) :]
                if ": " in meta_line:
                    key, _, value = meta_line.partition(": ")
                    meta[key.strip()] = value.strip()
                i += 1
            art_lines: list[str] = []
            while i < len(lines) and not lines[i].startswith(COMPONENT_PREFIX):
                art_lines.append(lines[i])
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
    errors: list[str] = []
    warnings: list[str] = []
    seen_names: Counter[str] = Counter()

    for c in components:
        name = c["name"]
        meta = c.get("meta", {})
        art = c.get("art", "")

        seen_names[name] += 1
        if not _NAME_RE.match(name):
            warnings.append(
                f"{name}: component name should use dot notation like category.variant "
                "(lowercase, no spaces)"
            )

        description = str(meta.get("description", "")).strip()
        props_raw = str(meta.get("props", "")).strip()
        if not description:
            warnings.append(f"{name}: missing ␟ description:")
        if not props_raw:
            warnings.append(f"{name}: missing ␟ props: (or explicit 'none')")

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

        if DELIMITER in art:
            errors.append(f"{name}: ASCII art must not contain ␟ (U+241F)")
        for j, ln in enumerate(art.splitlines()):
            if len(ln) > MAX_LINE_LENGTH:
                warnings.append(f"{name}: line {j + 1} exceeds {MAX_LINE_LENGTH} chars ({len(ln)})")

    for comp_name, count in seen_names.items():
        if count > 1:
            warnings.append(
                f"{comp_name}: defined {count} times in merged input; later entries override earlier ones"
            )

    return errors, warnings


def load_default_components() -> list[dict]:
    """
    Load the canonical component library from the repository layout.

    This helper assumes the process is running from a checkout of the AskeeDS
    repo. Callers outside that context should pass in their own paths and use
    parse_components() directly.
    """
    path = repo_root() / "design" / "ascii" / "components.txt"
    content = path.read_text(encoding="utf-8")
    return parse_components(content)


def validate_default_components() -> tuple[list[str], list[str]]:
    comps = load_default_components()
    return validate(comps)

