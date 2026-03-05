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

    def __init__(self, theme: Theme, decorations: dict[str, dict] | None = None):
        self.theme = theme
        self._decorations = decorations or {}

    def render(self, component: Component, props: dict) -> str:
        spec = component.render
        rtype = spec.get("type", "inline")
        if rtype == "inline":
            return self._render_inline(spec, props)
        if rtype == "join":
            return self._render_join(spec, props)
        if rtype == "box":
            return self._render_box(spec, props)
        if rtype == "clock":
            return self._render_clock(spec, props)
        if rtype == "stage_track":
            return self._render_stage_track(spec, props)
        if rtype == "banner":
            return self._render_banner(spec, props, component)
        if rtype == "frames":
            return self._render_frames(spec, props)
        if rtype == "table":
            return self._render_table(spec, props)
        if rtype == "bubble":
            return self._render_bubble(spec, props)
        if rtype == "tree":
            return self._render_tree(spec, props)
        if rtype == "grid":
            return self._render_grid(spec, props)
        if rtype == "charmap":
            return self._render_charmap(spec, props)
        if rtype == "art_lookup":
            return self._render_art_lookup(spec, props, component)
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

        elif stype == "active_list":
            items = props.get(section.get("over", ""), [])
            active_id = props.get(
                section.get("active_prop", "active_id"), ""
            )
            marker = section.get("marker", ">")
            tmpl = section.get("template", "{label}")
            pad = " " * len(marker)
            for item in items:
                item_id = item.get("id", "")
                prefix = marker if item_id == active_id else pad
                text = f" {prefix} " + self._interpolate(tmpl, item)
                lines.append(self._row(text, inner, bd))

        return lines

    # -- clock ----------------------------------------------------------

    def _render_clock(self, spec: dict, props: dict) -> str:
        label = props.get("label", "")
        segments = props.get("segments", 0)
        filled = props.get("filled", 0)
        clock = "●" * filled + "○" * max(0, segments - filled)
        return f"{label}\n[{clock}]   {filled} / {segments}"

    # -- stage_track ----------------------------------------------------

    def _render_stage_track(self, spec: dict, props: dict) -> str:
        label = props.get("label", "")
        stages = props.get("stages", [])
        current = props.get("current_stage_index", 0)
        boxes: list[str] = []
        centers: list[int] = []
        pos = 0
        for i, stage in enumerate(stages):
            stage_label = stage.get("label", stage.get("id", ""))
            box = f"[ {stage_label} ]"
            if i > 0:
                boxes.append("\u2500")
                pos += 1
            centers.append(pos + (len(box) - 1) // 2)
            boxes.append(box)
            pos += len(box)
        track_line = "".join(boxes)
        marker_line = ""
        if 0 <= current < len(centers):
            marker_line = " " * centers[current] + "^"
        lines: list[str] = []
        if label:
            lines.append(f"{label}:")
        if track_line:
            lines.append(track_line)
        if marker_line:
            lines.append(marker_line)
        return "\n".join(lines)

    # -- banner ---------------------------------------------------------

    def _render_banner(
        self, spec: dict, props: dict, component: Component
    ) -> str:
        from .banner import render_banner_text

        text = props.get("text", "")
        style_hint = props.get("style_hint", "splash")
        font = props.get("font")
        result = render_banner_text(text, style_hint, font=font)
        if result is not None:
            return result.rstrip("\n")
        return component.art.rstrip("\n")

    # -- frames ---------------------------------------------------------

    def _render_frames(self, spec: dict, props: dict) -> str:
        frames = props.get(spec.get("prop", "frames"), [])
        if frames:
            return str(frames[0])
        return ""

    # -- table ----------------------------------------------------------

    def _render_table(self, spec: dict, props: dict) -> str:
        columns = props.get(spec.get("columns_prop", "columns"), [])
        rows = props.get(spec.get("rows_prop", "rows"), [])
        if not columns:
            return ""

        col_widths = [len(str(h)) for h in columns]
        for row in rows:
            for i, cell in enumerate(row if isinstance(row, list) else []):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        def _sep() -> str:
            return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        def _data_row(cells: list) -> str:
            parts: list[str] = []
            for i, w in enumerate(col_widths):
                val = str(cells[i]) if i < len(cells) else ""
                parts.append(" " + val.ljust(w) + " ")
            return "|" + "|".join(parts) + "|"

        lines = [_sep(), _data_row(columns), _sep()]
        for row in rows:
            cells = row if isinstance(row, list) else []
            lines.append(_data_row(cells))
        lines.append(_sep())
        return "\n".join(lines)

    # -- bubble ---------------------------------------------------------

    def _render_bubble(self, spec: dict, props: dict) -> str:
        text = props.get("text", "")
        tail = spec.get("tail", "left")
        max_width = spec.get("max_width", 40)
        inner = max_width - 4
        wrapped = textwrap.wrap(
            text, width=inner, break_long_words=False,
        ) or [""]
        content_w = max(len(line) for line in wrapped)
        w = content_w + 2
        sep = "+" + "-" * w + "+"

        lines = [sep]
        for i, wline in enumerate(wrapped):
            padded = " " + wline.ljust(content_w) + " "
            if tail == "left" and i == 0:
                lines.append("/" + padded + "|")
            elif tail == "right" and i == len(wrapped) - 1:
                lines.append("|" + padded + "\\")
            else:
                lines.append("|" + padded + "|")
        lines.append(sep)
        return "\n".join(lines)

    # -- tree -----------------------------------------------------------

    def _render_tree(self, spec: dict, props: dict) -> str:
        nodes = props.get(spec.get("prop", "nodes"), [])
        tmpl = spec.get("template", "{label}")
        lines: list[str] = []
        self._tree_walk(nodes, tmpl, lines, "")
        return "\n".join(lines)

    def _tree_walk(
        self,
        nodes: list,
        tmpl: str,
        lines: list[str],
        prefix: str,
    ) -> None:
        for i, node in enumerate(nodes):
            is_last = i == len(nodes) - 1
            connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
            text = self._interpolate(tmpl, node)
            lines.append(prefix + connector + text)
            children = node.get("children", [])
            if children:
                ext = "    " if is_last else "\u2502   "
                self._tree_walk(children, tmpl, lines, prefix + ext)

    # -- grid -----------------------------------------------------------

    def _render_grid(self, spec: dict, props: dict) -> str:
        slots = list(props.get(spec.get("prop", "slots"), []))
        columns = props.get(spec.get("columns_prop", "columns"), 3)
        cell_width = spec.get("cell_width", 8)
        if columns < 1:
            return ""

        while len(slots) % columns != 0:
            slots.append(None)

        sep = "+" + (("-" * cell_width + "+") * columns)
        lines: list[str] = []
        for start in range(0, len(slots), columns):
            lines.append(sep)
            row = slots[start : start + columns]
            cells: list[str] = []
            for slot in row:
                if slot and isinstance(slot, dict) and slot.get("label"):
                    cells.append((" " + slot["label"]).ljust(cell_width)[:cell_width])
                else:
                    cells.append(" " * cell_width)
            lines.append("|" + "|".join(cells) + "|")
        lines.append(sep)
        return "\n".join(lines)

    # -- charmap --------------------------------------------------------

    def _render_charmap(self, spec: dict, props: dict) -> str:
        grid = props.get(spec.get("prop", "grid"), [])
        legend = props.get(spec.get("legend_prop", "legend_entries"), [])
        if not grid:
            return ""
        width = max(len(row) for row in grid)
        bd = self.theme.border(spec.get("border", "single"))
        lines: list[str] = []
        lines.append(bd["tl"] + bd["h"] * width + bd["tr"])
        for row in grid:
            row_str = "".join(str(c) for c in row).ljust(width)[:width]
            lines.append(bd["v"] + row_str + bd["v"])
        lines.append(bd["bl"] + bd["h"] * width + bd["br"])
        if legend:
            entries = [f"{e.get('char', '?')} {e.get('label', '')}" for e in legend]
            lines.append("  " + "  ".join(entries))
        return "\n".join(lines)

    # -- art_lookup -----------------------------------------------------

    def _render_art_lookup(self, spec: dict, props: dict, component: Component) -> str:
        art_id = str(props.get("art_id", ""))
        entry = self._decorations.get(art_id)
        art_text = entry.get("art", "").rstrip("\n") if entry else ""
        if not art_text:
            art_text = component.art.rstrip("\n")
        width = int(props.get("width", 0))
        height = int(props.get("height", 0))
        if not width and not height:
            return art_text
        lines = art_text.splitlines()
        if height and len(lines) > height:
            lines = lines[:height]
        if width:
            lines = [ln[:width].ljust(width) for ln in lines]
        if height and len(lines) < height:
            pad = width if width else (max(len(ln) for ln in lines) if lines else 0)
            lines.extend([" " * pad] * (height - len(lines)))
        return "\n".join(lines)

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
