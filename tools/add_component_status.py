#!/usr/bin/env python3
"""
One-off migration: add ␟ component-status: In Review to every component in
design/ascii/components.txt that does not already have component-status.

Idempotent: skips components that already have component-status. Run from repo root.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = ROOT / "design" / "ascii" / "components.txt"
DELIMITER = "\u241f"
COMPONENT_PREFIX = DELIMITER * 3 + " COMPONENT: "
META_PREFIX = DELIMITER + " "
STATUS_LINE = META_PREFIX + "component-status: In Review\n"


def main() -> int:
    if not COMPONENTS_PATH.exists():
        print(f"Error: not found {COMPONENTS_PATH}", file=__import__("sys").stderr)
        return 1
    lines = COMPONENTS_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    result: list[str] = []
    i = 0
    added = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        if line.startswith(COMPONENT_PREFIX):
            # Start of a new component; collect meta to see if we need to add status
            i += 1
            first_meta_idx = None
            has_status = False
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith(META_PREFIX) and not next_line.startswith(DELIMITER * 3):
                    if first_meta_idx is None:
                        first_meta_idx = len(result)
                    if ": " in next_line:
                        key = next_line.split(": ", 1)[0].strip().lstrip(DELIMITER).strip()
                        if key == "component-status":
                            has_status = True
                    result.append(next_line)
                    i += 1
                else:
                    break
            if not has_status and first_meta_idx is not None:
                # Insert after first meta line
                result.insert(first_meta_idx + 1, STATUS_LINE)
                added += 1
            continue
        i += 1
    COMPONENTS_PATH.write_text("".join(result), encoding="utf-8")
    print(f"Added component-status: In Review to {added} components", file=__import__("sys").stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
