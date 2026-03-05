"""
AskeeDS visual catalog — renders every non-reference component.

Generates sample props from each component's prop definitions so
output is meaningful without hardcoded test data.

    python examples/all_components.py
"""

from __future__ import annotations

from askee_ds import Loader, Theme, Renderer


SAMPLE_STRINGS = {
    "title": "Sample Title",
    "name": "Hero",
    "label": "Label",
    "text": "Hello, world!",
    "description_text": "A brief description of the scene.",
    "prompt": "> ",
    "location": "The Clearing",
    "message": "Something happened.",
    "variant": "info",
    "style_hint": "splash",
    "icon": "★",
    "active_id": "a",
    "art_id": "skull",
    "font": "",
}

SAMPLE_NUMBERS = {
    "hp_current": 8, "hp_max": 10,
    "current": 7, "max": 10, "value": 7,
    "turn_count": 5, "segments": 4, "filled": 2,
    "current_stage_index": 0, "columns": 3,
    "width": 12, "height": 5,
}


def _sample_element(element_spec: dict) -> dict:
    """Build a single sample object from an element schema."""
    obj: dict = {}
    for key, typ in element_spec.items():
        if typ == "string":
            obj[key] = key.replace("_", " ").title()
        elif typ in ("integer", "number"):
            obj[key] = SAMPLE_NUMBERS.get(key, 3)
        elif typ == "boolean":
            obj[key] = True
    if "id" in obj and "label" not in obj:
        obj["label"] = obj["id"]
    return obj


def _sample_props(component) -> dict:
    """Generate sample prop values from a component's prop definitions."""
    props: dict = {}
    for pname, pdef in component.props.items():
        if pdef.type == "string":
            props[pname] = SAMPLE_STRINGS.get(pname, pname.replace("_", " ").title())
        elif pdef.type in ("integer", "number"):
            props[pname] = SAMPLE_NUMBERS.get(pname, 5)
        elif pdef.type == "boolean":
            props[pname] = True
        elif pdef.type == "array":
            element = getattr(pdef, "element", None)
            element_type = getattr(pdef, "element_type", None)
            if element and isinstance(element, dict):
                a = _sample_element(element)
                b = _sample_element(element)
                if "id" in a:
                    a["id"], b["id"] = "a", "b"
                if "label" in a:
                    a["label"], b["label"] = "Alpha", "Beta"
                if "current" in a:
                    a["current"], b["current"] = 8, 3
                if "max" in a:
                    a["max"], b["max"] = 10, 5
                if "checked" in a:
                    a["checked"], b["checked"] = True, False
                props[pname] = [a, b]
            elif element_type == "string":
                props[pname] = ["|", "/", "-", "\\"]
            else:
                props[pname] = []
    return props


def main() -> int:
    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")
    theme = Theme(tokens)
    renderer = Renderer(theme)

    rendered = 0
    skipped = 0

    for name in sorted(components):
        comp = components[name]
        rtype = comp.render.get("type", "reference")
        if rtype == "reference":
            skipped += 1
            continue

        props = _sample_props(comp)
        output = renderer.render(comp, props)
        print(f"── {name} ({comp.status}) {'─' * max(1, 50 - len(name))}")
        print(output)
        print()
        rendered += 1

    print(f"{'═' * 60}")
    print(f"Rendered: {rendered}  |  Reference-only (skipped): {skipped}"
          f"  |  Total: {len(components)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
