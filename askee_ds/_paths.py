"""
Internal path helpers for the AskeeDS package.

Best-effort repo root when running from a development checkout. For installed
packages, callers should pass explicit paths instead of relying on repo_root().
"""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """
    Best-effort guess of the repository root when running from a package.

    For installed packages, callers should pass explicit paths instead of
    relying on this helper.
    """
    return Path(__file__).resolve().parent.parent
