# AskeeDS Integration Guide

This guide is for developers wiring AskeeDS into a Python project,
game engine, or TUI application. It covers installation, the Python
API, CLI commands, adapters, and how to extend the system.

For component design and YAML authoring, see [GUIDE.md](GUIDE.md). For
field and token lookup, see [REFERENCE.md](REFERENCE.md).

---

## Install

AskeeDS requires Python 3.11+ and PyYAML.

```bash
git clone <repo-url>
cd askeeDS
pip install -e .
```

### Optional extras

```bash
pip install -e ".[rich]"      # Rich adapter (ANSI-colored output)
pip install -e ".[textual]"   # Textual adapter (TUI widgets)
pip install -e ".[banner]"    # pyfiglet for typography.banner
pip install -e ".[dev]"       # pytest for running tests
```

---

## Python API

Five core classes handle loading, theming, rendering, composing, and
validating.

### Quick start

```python
from askee_ds import Loader, Theme, Renderer

loader = Loader()
components = loader.load_components_dir("components/")
tokens = loader.load_tokens_dir("tokens/")
theme = Theme(tokens)
renderer = Renderer(theme)

output = renderer.render(components["status-bar.default"], {
    "hp_current": 85,
    "hp_max": 100,
    "location": "The Clearing",
    "turn_count": 12,
})
print(output)
```

### Loader

`Loader` reads YAML files and returns structured data.

```python
loader = Loader()

# Load all components from a directory (recursively)
components = loader.load_components_dir("components/")

# Load all token files from a directory
tokens = loader.load_tokens_dir("tokens/")

# Load with schema validation (prints warnings for invalid components)
loader = Loader(schema_path="components/_schema.yaml")
components = loader.load_components_dir("components/")
```

Each component is a `Component` dataclass with fields: `name`,
`category`, `description`, `status`, `props`, `render`, `art`,
`default_color_role`, `interaction`.

### Theme

`Theme` resolves tokens (colors, borders, bar glyphs) into concrete
values used by the renderer.

```python
theme = Theme(tokens)

palette = theme.colors("danger")
# {"bg": "#2d1b1b", "fg": "#f48771", "border": "#8b3a3a", "accent": "#f48771"}

border = theme.border("single")
# {"h": "-", "v": "|", "tl": "+", "tr": "+", ...}
```

### Renderer

`Renderer` takes a component and props and produces ASCII output.

```python
renderer = Renderer(theme)

output = renderer.render(component, props)
```

#### Adaptive sizing

Pass `available_width` and `available_height` to control how adaptive
components (those with `width: fill` or `width: content`) size
themselves:

```python
output = renderer.render(
    components["room-card.default"],
    {"title": "Cavern", "description_text": "A dark cave.",
     "items": [], "npcs": [], "exits": []},
    available_width=60,
)
```

Components with fixed integer widths ignore `available_width`.
Components with `min_width` / `max_width` constraints clamp the result.

### Composer

`Composer` assembles layout components (stacks, columns, shells) from
child components.

```python
from askee_ds import Composer

composer = Composer(renderer, components)

output = composer.compose("layout.stack", {
    "blocks": [
        ("status-bar.default", {"hp_current": 85, "hp_max": 100,
                                "location": "Cavern", "turn_count": 5}),
        ("room-card.default",  {"title": "Cavern",
                                "description_text": "A dark cave.",
                                "items": [], "npcs": [],
                                "exits": [{"id": "n", "label": "north"}]}),
        ("command-input.default", {"prompt": ">"}),
    ],
})
print(output)
```

#### Composing screens from YAML

Load and render a complete screen definition:

```python
output = composer.compose_screen("screens/examples/adventure_main.yaml")
print(output)

# Override width
output = composer.compose_screen(
    "screens/examples/adventure_main.yaml",
    available_width=60,
)
```

Sizing propagates through nested layouts — the composer passes
`available_width` to each child component.

### Validator

`Validator` checks components against the schema.

```python
from askee_ds import Validator

validator = Validator.from_schema_file("components/_schema.yaml")

# Validate one component
errors = validator.validate(component)
for name, msg in errors:
    print(f"{name}: {msg}")

# Validate all loaded components
errors = validator.validate_all(components)
```

---

## CLI reference

All commands accept `--components DIR`, `--tokens DIR`, and
`--schema FILE` to override default paths.

If `askee-ds` is not found (common on macOS when the pip script directory
is not on your PATH), use: `python3 -m askee_ds.cli <subcommand>` — for
example, `python3 -m askee_ds.cli validate`.

### `askee-ds validate`

Validate all YAML component definitions against the schema.

```bash
askee-ds validate
# OK — 56 components validated, 0 errors.
```

### `askee-ds preview`

Render a named component with sample props.

```bash
askee-ds preview room-card.default \
  --props '{"title":"Cavern","description_text":"A dark cave.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
```

If `--props` is omitted, the component renders with empty/default
props.

### `askee-ds list`

List components, optionally filtered.

```bash
askee-ds list                       # All 56 components
askee-ds list --status approved     # Only approved components
askee-ds list --prefix status-bar   # Name prefix filter
```

### `askee-ds compose`

Render a screen from a YAML file.

```bash
askee-ds compose screens/examples/adventure_main.yaml
askee-ds compose screens/examples/adventure_main.yaml --width 60
```

---

## Rich adapter

The Rich adapter converts plain ASCII output into Rich `Text` objects
with ANSI colors based on a color role. Box-drawing characters get
border colors, content gets foreground colors, and highlighted tokens
get accent colors.

```python
from askee_ds.adapters.rich import RichAdapter
from rich.console import Console

adapter = RichAdapter(theme)

# Colorize pre-rendered output
ascii_output = renderer.render(components["room-card.default"], {...})
rich_text = adapter.colorize(ascii_output, "dungeon")
Console().print(rich_text)

# Render and colorize in one step
rich_text = adapter.render_component(renderer, component, props, color_role="danger")
Console().print(rich_text)
```

Requires: `pip install -e ".[rich]"`

---

## Textual adapter

The Textual adapter wraps Rich output as a `Static` widget that can be
mounted in any Textual app. Components with `interaction.focusable:
true` automatically get `can_focus = True` on the widget.

```python
from askee_ds.adapters.textual import AskeeWidget
from textual.app import App

class MyApp(App):
    def compose(self):
        loader = Loader()
        components = loader.load_components_dir("components/")
        tokens = loader.load_tokens_dir("tokens/")
        theme = Theme(tokens)
        renderer = Renderer(theme)

        # From a component
        widget = AskeeWidget.from_component(
            renderer, components["room-card.default"],
            props={...}, theme=theme, color_role="dungeon",
        )
        yield widget

        # From pre-rendered text
        widget = AskeeWidget.from_text(
            ascii_output, theme, color_role="neutral",
        )
        yield widget
```

Requires: `pip install -e ".[textual]"`

---

## Extending render types

AskeeDS uses a pluggable render type registry. You can add custom
render types without modifying the core package.

### Registering a custom render type

```python
from askee_ds.render_types._registry import register, RenderContext

def render_my_type(spec: dict, props: dict, ctx: RenderContext) -> str:
    """Custom render function.

    Args:
        spec: The render spec dict from the component YAML.
        props: The props dict passed at render time.
        ctx: RenderContext with theme, component, decorations,
             available_width, and available_height.

    Returns:
        The rendered ASCII string.
    """
    template = spec.get("template", "")
    return template.format(**props)

register("my_type", render_my_type)
```

After registration, any component with `render.type: my_type` will use
your function.

### RenderContext

Every render function receives a `RenderContext` dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `theme` | Theme | The active theme for color and border lookups. |
| `component` | Component | The component being rendered. |
| `decorations` | dict | Decoration art assets (for `art_lookup`). |
| `available_width` | int | Available terminal width (default 80). |
| `available_height` | int or None | Available terminal height. |

---

## Using AskeeDS in another project

### Option A — Copy the YAML definitions

Copy `components/` and `tokens/` into your project. Parse the YAML
with any language's YAML library. The component definitions are the
contract — build your own renderer for your runtime.

### Option B — Use the Python package

```bash
pip install -e path/to/askeeDS
```

Then `from askee_ds import Loader, Theme, Renderer` in your code.

### Option C — Git submodule

```bash
git submodule add <repo-url> vendor/askee-ds
```

Pin to a tag and update when ready. See [CHANGELOG.md](CHANGELOG.md)
for migration notes between versions.

---

## Validation and testing

```bash
# Validate all YAML components against the schema
askee-ds validate

# Run framework tests
python3 -m pytest tests/ -v
```

The test suite covers the Loader, Renderer, Theme, Validator, Composer,
adapters, CLI, sizing, interaction specs, and screen composition.

---

## Tools and dependencies

| Name | Use | Required? |
|------|-----|-----------|
| [PyYAML](https://pyyaml.org/) | Parse YAML definitions and tokens. | Yes |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Figlet banner text for `typography.banner`. | Optional (`pip install -e ".[banner]"`) |
| [Rich](https://github.com/Textualize/rich) | ANSI-colored output via the Rich adapter. | Optional (`pip install -e ".[rich]"`) |
| [Textual](https://github.com/Textualize/textual) | TUI widgets via the Textual adapter. | Optional (`pip install -e ".[textual]"`) |

---

## License and attribution

AskeeDS is released under the [MIT License](LICENSE).

If you ship a game, tool, or product that uses AskeeDS, please credit:

> AskeeDS by Spencer Goldade

Add this to your credits screen, README, or about page. See
[README.md](README.md) for full details.
