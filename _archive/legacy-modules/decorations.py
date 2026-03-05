"""
Library access to the AskeeDS decorative ASCII art catalog.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from askee_ds._paths import repo_root

DELIMITER = "\u241f"  # U+241F SYMBOL FOR UNIT SEPARATOR
ART_PREFIX = DELIMITER * 3 + " ART: "
META_PREFIX = DELIMITER + " "
MAX_LINE_LENGTH = 80

_ID_RE = re.compile(r"^decoration\.[a-z0-9_.]+$")

ALLOWED_LICENSES = {"public-domain", "CC0", "original"}


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
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: Counter[str] = Counter()

    required_meta_keys = ("title", "tags", "source", "license")

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
        if license_value and license_value not in ALLOWED_LICENSES:
            warnings.append(
                f"{art_id}: license {license_value!r} is not one of {sorted(ALLOWED_LICENSES)}"
            )

        source_value = str(meta.get("source", "")).strip()
        if source_value and not (
            source_value == "original"
            or source_value.startswith("http://")
            or source_value.startswith("https://")
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


def load_default_decorations() -> list[dict]:
    root = repo_root()
    path = root / "design" / "ascii" / "decoration-catalog.txt"
    if not path.exists():
        path = root / "_archive" / "design-ascii" / "decoration-catalog.txt"
    content = path.read_text(encoding="utf-8")
    return parse_decorations(content)


def validate_default_decorations() -> tuple[list[str], list[str]]:
    decos = load_default_decorations()
    return validate_decorations(decos)

