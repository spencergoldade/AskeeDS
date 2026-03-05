"""
AskeeDS renderer — component + props + theme = ASCII output.

Takes a Component definition, a props dict, and a Theme, and produces a
rendered ASCII string. The renderer interprets the component's declarative
render spec (sections like header, text, list, bars, etc.) without any
component-specific hardcoded branches.

    from askee_ds import Loader, Theme, Renderer

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)
    print(renderer.render(components["room-card.default"], {...}))
"""

from __future__ import annotations

import re
import textwrap

from .loader import Component
from .theme import Theme


class Renderer:

    def __init__(self, theme: Theme):
        self.theme = theme

    def render(self, component: Component, props: dict) -> str:
        spec = component.render
        rtype = spec.get("type", "inline")
        if rtype == "inline":
            return self._render_inline(spec, props)
        if rtype == "join":
            return self._render_join(spec, props)
        if rtype == "box":
            return self._render_box(spec, props)
        return component.art.rstrip("\n")

    # -- inline ---------------------------------------------------------

    def _render_inline(self, spec: dict, props: dict) -> str:
        return self._interpolate(spec.get("template", ""), props)

    # -- join -----------------------------------------------------------

    def _render_join(self, spec: dict, props: dict) -> str:
        items = props.get(spec.get("over", ""), [])
        sep = spec.get("separator", "  ")
        tmpl = spec.get("template", "{label}")
        prefix = spec.get("prefix", "")
        parts = [self._interpolate(tmpl, item) for item in items]
        return prefix + sep.join(parts)

    # -- box ------------------------------------------------------------

    def _render_box(self, spec: dict, props: dict) -> str:
        width = spec.get("width", 40)
        bd = self.theme.border(spec.get("border", "single"))
        inner = width - 2
        lines: list[str] = []

        lines.append(bd["tl"] + bd["h"] * inner + bd["tr"])

        for section in spec.get("sections", []):
            lines.extend(self._render_section(section, props, inner, bd))

        lines.append(bd["bl"] + bd["h"] * inner + bd["br"])
        return "\n".join(lines)

    def _render_section(
        self, section: dict, props: dict, inner: int, bd: dict
    ) -> list[str]:
        stype = section.get("type", "text")
        lines: list[str] = []

        if stype == "header":
            text = self._interpolate(section["text"], props)
            lines.append(self._row(f" {text}", inner, bd))

        elif stype == "divider":
            lines.append(bd["tj_right"] + bd["h"] * inner + bd["tj_left"])

        elif stype == "text":
            text = self._interpolate(section["text"], props)
            lines.append(self._row(text, inner, bd))

        elif stype == "wrap":
            raw = self._interpolate(section["text"], props)
            indent = section.get("indent", 0)
            prefix = " " * indent
            wrapped = textwrap.wrap(
                raw, width=inner - indent * 2, break_long_words=False,
            )
            for wline in wrapped or [""]:
                lines.append(self._row(f"{prefix}{wline}", inner, bd))

        elif stype == "blank":
            lines.append(self._row("", inner, bd))

        elif stype == "list":
            items = props.get(section.get("over", ""), [])
            if not items and section.get("if_empty") == "hide":
                return lines
            label = section.get("label", "")
            tmpl = section.get("template", "  {label}")
            if label:
                lines.append(self._row(f" {label}:", inner, bd))
            for item in items:
                if isinstance(item, str):
                    text = self._interpolate(tmpl, {"": item, "label": item})
                else:
                    text = self._interpolate(tmpl, item)
                lines.append(self._row(text, inner, bd))

        elif stype == "bars":
            bar_width = section.get("bar_width", 10)
            tmpl = section.get(
                "template", " {label} [{bar}] {current}/{max}"
            )
            filled_ch, empty_ch = self.theme.bar_chars()
            for item in props.get(section.get("over", ""), []):
                cur = item.get("current", 0)
                mx = item.get("max", 1)
                ratio = cur / mx if mx else 0
                n = round(ratio * bar_width)
                bar_str = filled_ch * n + empty_ch * (bar_width - n)
                text = self._interpolate(tmpl, {**item, "bar": bar_str})
                lines.append(self._row(text, inner, bd))

        elif stype == "progress":
            bar_width = section.get("bar_width", 20)
            tmpl = section.get(
                "template", " {label} [{bar}] {value}/{max}"
            )
            filled_ch, empty_ch = self.theme.bar_chars()
            val = props.get(section.get("value_prop", "value"), 0)
            mx = props.get(section.get("max_prop", "max"), 1)
            ratio = val / mx if mx else 0
            n = round(ratio * bar_width)
            bar_str = filled_ch * n + empty_ch * (bar_width - n)
            merged = {**props, "bar": bar_str}
            text = self._interpolate(tmpl, merged)
            lines.append(self._row(text, inner, bd))

        elif stype == "numbered_list":
            items = props.get(section.get("over", ""), [])
            tmpl = section.get("template", " {label}")
            for i, item in enumerate(items, 1):
                text = self._interpolate(f" {i}. {tmpl.lstrip()}", item)
                lines.append(self._row(text, inner, bd))

        elif stype == "checked_list":
            items = props.get(section.get("over", ""), [])
            check_prop = section.get("check_prop", "checked")
            tmpl = section.get("template", "{label}")
            for item in items:
                mark = "x" if item.get(check_prop) else " "
                text = f" [{mark}] " + self._interpolate(tmpl, item)
                lines.append(self._row(text, inner, bd))

        return lines

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _row(text: str, inner_width: int, bd: dict) -> str:
        return bd["v"] + text.ljust(inner_width)[:inner_width] + bd["v"]

    @staticmethod
    def _interpolate(template: str, props: dict) -> str:
        def _replace(m: re.Match) -> str:
            key, fmt = m.group(1), m.group(2)
            val = props.get(key, m.group(0))
            return format(val, fmt) if fmt else str(val)
        return re.sub(r"\{(\w+)(?::([^}]+))?\}", _replace, template)
