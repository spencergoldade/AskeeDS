"""
AskeeDS render output — structured result for adapters and alternate back ends.

The renderer produces plain ASCII. For adapters (Rich, Textual, or future
HTML/JSON), we expose a small structured type so consumers can work with
lines and optional style hints without parsing the string.

    from askee_ds import Renderer, RenderOutput

    output = renderer.render_output(component, props)
    for line in output.lines:
        ...
    text = output.to_string()
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderOutput:
    """Structured result of rendering a component.

    Attributes:
        lines: Rendered output as a list of strings (one per line).
        styles: Optional per-line or per-segment style hints for adapters.
            None for plain ASCII; future use for semantic regions.
    """

    lines: list[str]
    styles: list | None = None

    def to_string(self) -> str:
        """Return the content as a single newline-separated string."""
        return "\n".join(self.lines)
