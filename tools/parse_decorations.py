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
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

DELIMITER = "\u241f"  # U+241F SYMBOL FOR UNIT SEPARATOR
ART_PREFIX = DELIMITER * 3 + " ART: "
META_PREFIX = DELIMITER + " "
MAX_LINE_LENGTH = 80

_ID_RE = re.compile(r"^decoration\.[a-z0-9_.]+$")


def parse_decorations(content: str) -> list[dict]:
    """Parse decoration catalog text into a list of decoration dicts."""
    decorations: list[dict] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(ART_PREFIX):
            art_id = line[len(ART_PREFIX) :].strip()
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
            while i < len(lines) and not lines[i].startswith(ART_PREFIX):
                art_lines.append(lines[i])
                i += 1
            art = "\n".join(art_lines).rstrip("\n")
            decorations.append({"id": art_id, "meta": meta, "art": art})
        else:
            i += 1
    return decorations


def _iter_lines(text: str) -> Iterable[tuple[int, str]]:
    for idx, line in enumerate(text.splitlines(), start=1):
        yield idx, line


def validate_decorations(decorations: list[dict]) -> tuple[list[str], list[str]]:
    """
    Run validation rules for decorations. Returns (errors, warnings).

    Errors are critical (e.g. ␟ in art). Warnings flag issues that should be
    fixed to keep the catalog clean and predictable.
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: Counter[str] = Counter()

    required_meta_keys = ("title", "tags", "source", "license")
    allowed_licenses = {"public-domain", "CC0", "original"}

    for d in decorations:
        art_id = d.get("id", "")
        meta = d.get("meta", {}) or {}
        art = d.get("art", "") or ""

        seen_ids[art_id] += 1

        if not _ID_RE.match(art_id):
            warnings.append(
                f"{art_id or '<missing id>'}: art id should start with 'decoration.' and use dot-separated segments"
            )

        for key in required_meta_keys:
            if not str(meta.get(key, "")).strip():
                warnings.append(f"{art_id}: missing ␟ {key}:")

        tags_raw = str(meta.get("tags", ""))
        if tags_raw:
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            if not tags:
                warnings.append(f"{art_id}: ␟ tags: value could not be parsed into tags")
            else:
                for tag in tags:
                    if " " in tag:
                        warnings.append(
                            f"{art_id}: tag {tag!r} should not contain spaces; use hyphens or separate tags"
                        )

        license_value = str(meta.get("license", "")).strip()
        if license_value and license_value not in allowed_licenses:
            warnings.append(
                f"{art_id}: license {license_value!r} is not one of {sorted(allowed_licenses)}"
            )

        source_value = str(meta.get("source", "")).strip()
        if source_value and not (
            source_value == "original" or source_value.startswith("http://") or source_value.startswith("https://")
        ):
            warnings.append(
                f"{art_id}: source {source_value!r} should be a URL or 'original'"
            )

        if DELIMITER in art:
            errors.append(f"{art_id}: ASCII art must not contain ␟ (U+241F)")

        for line_no, line in _iter_lines(art):
            if len(line) > MAX_LINE_LENGTH:
                warnings.append(
                    f"{art_id}: line {line_no} exceeds {MAX_LINE_LENGTH} chars ({len(line)})"
                )

    for art_id, count in seen_ids.items():
        if count > 1:
            warnings.append(
                f"{art_id}: defined {count} times in merged input; later entries override earlier ones"
            )

    return errors, warnings


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
        paths = [
            Path(__file__).resolve().parent.parent
            / "design"
            / "ascii"
            / "decoration-catalog.txt"
        ]

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
        print(f"Valid: {len(decorations)} decorations ({len(warns)} warnings)", file=sys.stderr)
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

