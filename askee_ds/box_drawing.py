"""
Library access to AskeeDS box-drawing character set.

Load design/ascii/box-drawing.yaml in code; do not hardcode border characters
in component art. Use this module when implementing TUI borders.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - environment dependent
    yaml = None  # type: ignore[assignment]


def repo_root() -> Path:
    """Best-effort repository root when running from a package."""
    return Path(__file__).resolve().parent.parent


def load_box_drawing(root: Path | None = None) -> dict[str, Any]:
    """
    Load box-drawing character set from design/ascii/box-drawing.yaml.

    Returns the raw YAML structure: keys include "default" (e.g. "light"),
    "sets" (e.g. sets["light"]["horizontal"] == "-"). Use the "default" set
    unless the caller requests another (e.g. "heavy", "double").

    For installed packages, pass an explicit root path; when root is None,
    uses repo_root() (valid for development checkouts).
    """
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to load box-drawing. Install with `pip install pyyaml`."
        )
    if root is None:
        root = repo_root()
    path = root / "design" / "ascii" / "box-drawing.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))  # type: ignore[arg-type]
    return data if isinstance(data, dict) else {}
