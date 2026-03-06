#!/usr/bin/env python3
"""Regenerate CREDITS_LOGO.txt from pyfiglet (basic font). Run from repo root or any subdir."""

from pathlib import Path

try:
    import pyfiglet
except ImportError:
    raise SystemExit("Install banner extra: pip install -e '.[banner]'")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "CREDITS_LOGO.txt"
FIGLET_FONT = "basic"
WORDMARK_TEXT = "AskeeDS"
SUBTITLE = "An ASCII-based design system by Spencer Goldade"
PERMISSION_NOTE = """You are welcome to display this logo in your game or project credits
when using AskeeDS. No attribution beyond the subtitle is required."""


def main() -> None:
    art = pyfiglet.figlet_format(WORDMARK_TEXT, font=FIGLET_FONT, width=80)
    art = art.rstrip("\n")
    art_lines = art.split("\n")
    while art_lines and not art_lines[-1].strip():
        art_lines.pop()
    art = "\n".join(art_lines)
    max_len = max(len(l) for l in art_lines) if art_lines else 0
    separator = "-" * max_len
    subtitle_centered = SUBTITLE.center(max_len)
    content = art + "\n" + separator + "\n" + subtitle_centered + "\n\n" + PERMISSION_NOTE + "\n"
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
