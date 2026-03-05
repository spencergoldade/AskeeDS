"""
AskeeDS theme system — resolves tokens to concrete values.

The Theme wraps a merged token dict (from Loader.load_tokens_dir) and provides
lookup methods for colors, box-drawing characters, and bar glyphs.

    from askee_ds import Loader, Theme

    loader = Loader()
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    theme.colors("danger")  # -> {"bg": "#2d1b1b", "fg": "#f48771", ...}
"""

from __future__ import annotations


class Theme:

    def __init__(self, tokens: dict):
        self._tokens = tokens
        self._colors = self._build_colors(tokens)
        self._borders = self._build_borders(tokens)
        self._bar = tokens.get("bar", {"filled": "\u2588", "empty": "\u2591"})

    def colors(self, role: str) -> dict:
        """Resolve a color role to its palette dict (bg, fg, border, accent)."""
        return self._colors.get(role, self._colors.get("neutral", {}))

    def border(self, style: str = "single") -> dict:
        """Resolve a border style to its character dict (h, v, tl, tr, ...)."""
        return self._borders.get(style, self._borders.get("single", {}))

    def bar_chars(self) -> tuple[str, str]:
        """Return (filled_char, empty_char) for bar rendering."""
        return self._bar["filled"], self._bar["empty"]

    @property
    def color_roles(self) -> list[str]:
        """List available color role names."""
        return list(self._colors.keys())

    @property
    def border_styles(self) -> list[str]:
        """List available border style names."""
        return list(self._borders.keys())

    @staticmethod
    def _build_colors(tokens: dict) -> dict[str, dict]:
        raw = tokens.get("color_roles", {})
        out: dict[str, dict] = {}
        for role, vals in raw.items():
            if isinstance(vals, dict):
                out[role] = {k: v for k, v in vals.items() if k != "description"}
        return out

    @staticmethod
    def _build_borders(tokens: dict) -> dict[str, dict]:
        raw = tokens.get("sets", {})
        out: dict[str, dict] = {}
        for name, vals in raw.items():
            if isinstance(vals, dict):
                out[name] = {k: v for k, v in vals.items() if k != "description"}
        return out
