"""Shared helpers used by multiple render type modules."""

from __future__ import annotations

import re


def interpolate(template: str, props: dict) -> str:
    """Interpolate {prop} and {prop:format} placeholders in a template string."""
    def _replace(m: re.Match) -> str:
        key, fmt = m.group(1), m.group(2)
        val = props.get(key, m.group(0))
        return format(val, fmt) if fmt else str(val)
    return re.sub(r"\{(\w+)(?::([^}]+))?\}", _replace, template)


def row(text: str, inner_width: int, bd: dict) -> str:
    """Produce a single bordered row: |text        |"""
    return bd["v"] + text.ljust(inner_width)[:inner_width] + bd["v"]
