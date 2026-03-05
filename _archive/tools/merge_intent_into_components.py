#!/usr/bin/env python3
"""
One-off merge: copy intent (purpose, default-view, randomized-view, prop-types,
edge-cases) from design/ascii/PROP-INTENT-AND-TEST-DATA-PLAN.md into each
matching component block in design/ascii/components.txt.

Uses multi-line meta: first line is "␟ key: value", continuation lines are
"␟   text". Run from repo root. Backs up components.txt to components.txt.bak
before writing.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DELIMITER = "\u241f"
COMPONENT_PREFIX = DELIMITER * 3 + " COMPONENT: "
META_PREFIX = DELIMITER + " "
MAX_META_LINE = 72  # wrap long lines; continuation is "␟   " (4 chars)


def _wrap(text: str, width: int = MAX_META_LINE) -> list[str]:
    """Split into lines; long lines wrapped at word boundaries."""
    out: list[str] = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        words = paragraph.split()
        line = ""
        for w in words:
            if line and len(line) + 1 + len(w) > width:
                out.append(line)
                line = w
            else:
                line = f"{line} {w}".strip() if line else w
        if line:
            out.append(line)
    return out


def _to_meta_lines(key: str, value: str) -> list[str]:
    """Turn a key and multi-line value into ␟ key: first line and ␟   rest."""
    value = value.strip()
    if not value:
        return []
    lines = _wrap(value)
    out = [f"{META_PREFIX}{key}: {lines[0]}"]
    for L in lines[1:]:
        out.append(f"{META_PREFIX}  {L}")
    return out


def parse_plan(path: Path) -> dict[str, dict[str, str]]:
    """Extract per-component intent: purpose, default-view, randomized-view, prop-types, edge-cases."""
    text = path.read_text(encoding="utf-8")
    # Sections: **1. Purpose**, **2. Default View**, **3. Randomized View**, **4. Prop Types/Shapes**, **5. Edge Cases**
    section_headers = [
        ("**1. Purpose**", "purpose"),
        ("**2. Default View**", "default-view"),
        ("**3. Randomized View**", "randomized-view"),
        ("**4. Prop Types/Shapes**", "prop-types"),
        ("**5. Edge Cases**", "edge-cases"),
    ]
    intent_by_name: dict[str, dict[str, str]] = {}
    # Find each ### `name` block
    block_re = re.compile(r"^### `([^`]+)`\s*$", re.MULTILINE)
    pos = 0
    while True:
        m = block_re.search(text, pos)
        if not m:
            break
        name = m.group(1).strip()
        start = m.end()
        # Next ### or ## or --- at start of line ends this block
        end_m = re.search(r"\n(---|\n### `|\n## Chunk)", text[start:])
        end = start + end_m.start(0) if end_m else len(text)
        block = text[start:end]
        pos = end

        sections: dict[str, str] = {}
        for i, (header, key) in enumerate(section_headers):
            pattern = re.escape(header)
            match = re.search(pattern, block)
            if not match:
                continue
            section_start = match.end()
            # Section ends at next section header or end of block
            next_headers = [re.escape(h) for h, _ in section_headers if h != header]
            next_re = re.compile("|".join(next_headers))
            next_m = next_re.search(block[section_start:])
            section_end = section_start + next_m.start(0) if next_m else len(block)
            body = block[section_start:section_end].strip()
            # Drop leading **Props:** line if present (only in first section sometimes)
            if body.startswith("**Props:**"):
                body = re.sub(r"^\*\*Props:\*\*[^\n]*\n?", "", body).strip()
            sections[key] = body
        if sections:
            intent_by_name[name] = sections
    return intent_by_name


def main() -> None:
    plan_path = REPO_ROOT / "design" / "ascii" / "PROP-INTENT-AND-TEST-DATA-PLAN.md"
    comp_path = REPO_ROOT / "design" / "ascii" / "components.txt"
    if not plan_path.is_file():
        raise SystemExit(f"Plan file not found: {plan_path}")
    if not comp_path.is_file():
        raise SystemExit(f"Components file not found: {comp_path}")

    intent_by_name = parse_plan(plan_path)
    lines = comp_path.read_text(encoding="utf-8").splitlines()
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        # Start of a component block: ␟␟␟ COMPONENT: <name>
        if line.startswith(COMPONENT_PREFIX):
            name = line[len(COMPONENT_PREFIX) :].strip()
            i += 1
            last_meta_idx = -1
            while i < len(lines):
                next_line = lines[i]
                # Meta: starts with one ␟ and space; not three ␟
                if next_line.startswith(META_PREFIX) and not next_line.startswith(DELIMITER * 3):
                    result.append(next_line)
                    last_meta_idx = len(result) - 1
                    i += 1
                    continue
                # Blank or start of art or next component
                break

            if name in intent_by_name and last_meta_idx >= 0:
                new_lines: list[str] = []
                for key in ("purpose", "default-view", "randomized-view", "prop-types", "edge-cases"):
                    value = intent_by_name[name].get(key)
                    if value:
                        new_lines.extend(_to_meta_lines(key, value))
                if new_lines:
                    result = result[: last_meta_idx + 1] + new_lines + result[last_meta_idx + 1 :]

            # Drain rest of block (blank, art) but do not append next COMPONENT line
            while i < len(lines):
                candidate = lines[i]
                if candidate.startswith(COMPONENT_PREFIX):
                    break
                result.append(candidate)
                i += 1
            continue
        i += 1

    backup = comp_path.with_suffix(comp_path.suffix + ".bak")
    backup.write_text(comp_path.read_text(encoding="utf-8"), encoding="utf-8")
    comp_path.write_text("\n".join(result) + "\n", encoding="utf-8")
    print(f"Merged intent for {len(intent_by_name)} components into {comp_path}. Backup: {backup}")


if __name__ == "__main__":
    main()
