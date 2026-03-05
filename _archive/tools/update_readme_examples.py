#!/usr/bin/env python3
"""
Update the main README.md with a small set of example components
rendered from design/ascii/components.txt.

Rules:
- Use tools/parse_components.py to load components.
- Select up to maxExamples components based on design/readme-examples.json.
- Prefer diverse, high-signal components (templates, organisms, game UI).
- Replace content between COMPONENT_EXAMPLES markers in README.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = ROOT / "design" / "ascii" / "components.txt"
CONFIG_PATH = ROOT / "design" / "readme-examples.json"
README_PATH = ROOT / "README.md"
PARSE_SCRIPT = ROOT / "tools" / "parse_components.py"

MARKER_START = "<!-- COMPONENT_EXAMPLES:START -->"
MARKER_END = "<!-- COMPONENT_EXAMPLES:END -->"


@dataclass
class Component:
    name: str
    meta: dict[str, Any]
    art: str
    group: str


def load_components() -> list[Component]:
    # Reuse the existing parser via Python import.
    import importlib.util  # type: ignore

    spec = importlib.util.spec_from_file_location("parse_components", PARSE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import parser from {PARSE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    with COMPONENTS_PATH.open("r", encoding="utf-8") as f:
        content = f.read()

    raw_components = module.parse_components(content)  # type: ignore[attr-defined]

    current_group = "Uncategorized"
    result: list[Component] = []
    for c in raw_components:
        name = c["name"]
        meta = c.get("meta", {})
        art = c.get("art", "")
        # Group is derived from inline section headers in components.txt
        if name.startswith("layout.") or name.startswith("table.") or name.startswith("room-card."):
            # These live inside higher-level sections in the file, but we also
            # want to bias them as templates / organisms / game core.
            if name.startswith("layout."):
                current_group = "Templates"
            elif name.startswith("room-card."):
                current_group = "Game — screens"
        group = meta.get("group", current_group)
        result.append(Component(name=name, meta=meta, art=art, group=group))
    return result


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {"maxExamples": 3, "preferredGroups": [], "pinnedExamples": [], "allowInteractive": True}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def score_component(c: Component, preferred_groups: list[str], allow_interactive: bool) -> tuple[int, int, str]:
    """
    Return a sort key:
    - primary: group preference (lower is better)
    - secondary: negative art length (more content first)
    - tertiary: name (lexicographic)
    """
    group_index = preferred_groups.index(c.group) if c.group in preferred_groups else len(preferred_groups)
    interactive = c.meta.get("interactive", "").lower() == "true"
    if interactive and not allow_interactive:
        group_index += 10
    art_len = len(c.art.splitlines())
    return (group_index, -art_len, c.name)


def select_examples(components: list[Component], config: dict[str, Any]) -> list[Component]:
    max_examples = int(config.get("maxExamples", 3)) or 3
    preferred_groups = list(config.get("preferredGroups", []))
    pinned = list(config.get("pinnedExamples", []))
    allow_interactive = bool(config.get("allowInteractive", True))

    by_name = {c.name: c for c in components}
    chosen: list[Component] = []

    # 1) Use pinned examples first, in order, if they still exist.
    for name in pinned:
        c = by_name.get(name)
        if c:
            chosen.append(c)
        if len(chosen) >= max_examples:
            return chosen

    # 2) Fill remaining slots with best-scoring diverse components.
    remaining = [c for c in components if c.name not in {x.name for x in chosen}]
    remaining.sort(key=lambda c: score_component(c, preferred_groups, allow_interactive))

    used_groups: set[str] = {c.group for c in chosen}
    for c in remaining:
        if len(chosen) >= max_examples:
            break
        # Try to maximize group diversity first.
        if c.group not in used_groups or len(used_groups) < max_examples:
            chosen.append(c)
            used_groups.add(c.group)

    # If we still have fewer than max_examples and ran out of new groups,
    # just top up with the next best components.
    if len(chosen) < max_examples:
        remaining2 = [c for c in components if c.name not in {x.name for x in chosen}]
        remaining2.sort(key=lambda c: score_component(c, preferred_groups, allow_interactive))
        for c in remaining2:
            if len(chosen) >= max_examples:
                break
            chosen.append(c)

    return chosen


def render_examples_markdown(examples: list[Component], total_count: int) -> str:
    if not examples:
        return "_No components available yet._"

    lines: list[str] = []
    lines.append(f"Here are a few examples of the {total_count}+ components from AskeeDS:")
    lines.append("")
    for c in examples:
        desc = c.meta.get("description", "").strip()
        group = c.group
        heading = f"- **`{c.name}`**"
        if group:
            heading += f" · {group}"
        if desc:
            heading += f" — {desc}"
        lines.append(heading)
        lines.append("")
        lines.append("```text")
        lines.append(c.art.rstrip())
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_readme_block(readme_text: str, block_text: str) -> str:
    if MARKER_START not in readme_text or MARKER_END not in readme_text:
        raise SystemExit(
            "README.md is missing COMPONENT_EXAMPLES markers.\n"
            f"Add them where you want the examples to appear:\n\n{MARKER_START}\n{MARKER_END}\n"
        )
    pre, _, rest = readme_text.partition(MARKER_START)
    _, _, post = rest.partition(MARKER_END)
    new_block = f"{MARKER_START}\n\n{block_text}\n{MARKER_END}"
    return pre + new_block + post


def main() -> int:
    if not COMPONENTS_PATH.exists():
        raise SystemExit(f"Missing components file: {COMPONENTS_PATH}")
    if not README_PATH.exists():
        raise SystemExit(f"Missing README: {README_PATH}")

    components = load_components()
    config = load_config()
    examples = select_examples(components, config)
    block = render_examples_markdown(examples, total_count=len(components))

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = update_readme_block(readme_text, block)
    README_PATH.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

