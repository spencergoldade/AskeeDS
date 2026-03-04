"""
Render typography.banner (Figlet-style) text to ASCII lines.

Use only for content explicitly designated as banner/special (the typography.banner
component). All other TUI text remains plain. Requires the optional dependency:
pip install pyfiglet or pip install -e ".[banner]"
"""

from __future__ import annotations

from pathlib import Path

# style_hint -> pyfiglet font name (splash = larger, section = default, compact = smaller)
# Use fonts that are commonly available in pyfiglet; fallback to "standard" on error.
STYLE_HINT_FONTS: dict[str, str] = {
    "splash": "big",
    "section": "standard",
    "compact": "standard",
}

MAX_WIDTH = 80
MAX_HEIGHT_SPLASH = 10


def get_approved_fonts(path: Path | None = None) -> list[str]:
    """
    Return the list of approved Figlet font names (one per line) from a file.
    Used by tooling and docs; when path is None, returns [] so the package
    does not depend on repo layout. Callers (e.g. testing tool) pass the path
    to tools/figlet_approved_fonts.txt.
    """
    if path is None or not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [f.strip() for f in lines if f.strip()]
    except Exception:
        return []


def get_figlet_fonts() -> list[str] | None:
    """
    Return a sorted list of available pyfiglet font names, or None if pyfiglet
    is not installed. Use for font browsers and approval workflows.
    """
    try:
        import pyfiglet
        return sorted(pyfiglet.FigletFont.getFonts())
    except (ImportError, AttributeError):
        return None


def render_banner_text(
    text: str,
    style_hint: str = "splash",
    *,
    font: str | None = None,
    max_width: int = MAX_WIDTH,
    max_height: int | None = None,
) -> str | None:
    """
    Render text as Figlet-style ASCII art for typography.banner.

    Returns a multi-line string (with trailing newline), or None if pyfiglet
    is not installed. Callers should fall back to static component art when
    None is returned.

    Args:
        text: The string to render (e.g. game title, chapter name).
        style_hint: One of "splash", "section", "compact"; maps to Figlet font size (ignored if font= is set).
        font: If set, use this pyfiglet font name directly (for browsers and previews).
        max_width: Max characters per line (default 80 per AskeeDS typography).
        max_height: Optional max lines; if set, art is truncated to this many lines.

    Returns:
        ASCII art string, or None if pyfiglet is not available.
    """
    try:
        import pyfiglet
    except ImportError:
        return None

    use_font = font if (font is not None and str(font).strip()) else None
    font = use_font if use_font else STYLE_HINT_FONTS.get(style_hint, "standard")
    # Some fonts may not exist; fall back to standard
    try:
        result = pyfiglet.figlet_format(
            text,
            font=font,
            width=max_width,
        )
    except Exception:
        result = pyfiglet.figlet_format(text, font="standard", width=max_width)

    if not result:
        return None
    result = result.rstrip("\n") + "\n"
    if max_height is not None:
        lines = result.splitlines()
        if len(lines) > max_height:
            result = "\n".join(lines[:max_height]) + "\n"
    return result
