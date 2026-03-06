#!/usr/bin/env python3
"""Generate AskeeDS in several pyfiglet fonts for logo selection. Run from repo root."""

import sys

try:
    import pyfiglet
except ImportError:
    print("Install banner extra: pip install -e '.[banner]'", file=sys.stderr)
    sys.exit(1)

TEXT = "AskeeDS"
# Diverse set: classic, bold, rounded, blocky, script-like, tech
FONTS = [
    "standard",
    "big",
    "block",
    "slant",
    "small",
    "banner3",
    "doom",
    "shadow",
    "digital",
    "lean",
    "rectangles",
    "speed",
    "univers",
    "rounded",
    "bubble",
    "larry3d",
]
available = set(pyfiglet.FigletFont.getFonts())
for font in FONTS:
    if font not in available:
        continue
    try:
        art = pyfiglet.figlet_format(TEXT, font=font, width=80)
        print(f"\n{'='*60}\n FONT: {font}\n{'='*60}\n")
        print(art)
    except Exception as e:
        print(f"--- {font}: {e}\n", file=sys.stderr)
