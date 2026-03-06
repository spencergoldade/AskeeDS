# AskeeDS Integration Guide

This guide is for developers wiring AskeeDS into a Python project,
game engine, or TUI application. It covers installation, the Python
API, CLI commands, adapters, and how to extend the system.

For component design and YAML authoring, see [GUIDE.md](GUIDE.md). For
field and token lookup, see [REFERENCE.md](REFERENCE.md).

---

## Install

AskeeDS requires Python 3.12+ and PyYAML.

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

AskeeDS targets **modern terminals and equipment** (not retro hardware).
Default width is 100 columns; the look is retro (ASCII aesthetic), the
target is modern. Pass `available_width` and `available_height` to
control how adaptive components (those with `width: fill` or
`width: content`) size themselves:

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

#### What the renderer produces

- **`render(component, props, ...)`** returns a **single string**: the full
  ASCII output with newlines between lines. So `output.splitlines()` gives
  you one string per line. No embedded style metadata — just characters.

- **`render_output(component, props, ...)`** returns a **`RenderOutput`**
  object: `lines` (list of strings, one per line) and optional `styles`
  (reserved for future use). Use this when you want structured output for
  an adapter or alternate back end (e.g. HTML, JSON). Call
  `output.to_string()` to get the same string as `render()`.

Adapters (Rich, Textual) currently work from the string; they can
optionally use `render_output().lines` for line-by-line processing.

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
| `available_width` | int | Available terminal width (default 100). |
| `available_height` | int or None | Available terminal height. |

---

## Mod and adventure extension contract

Engines that support mods (e.g. per-adventure content) can let a mod
**override** or **extend** AskeeDS themes and components without
forking the package. This section documents the intended contract so
engine and mod authors can rely on consistent behavior.

### Theme and token override

Tokens (colors, borders, bar glyphs) are merged into a single dict
before building a `Theme`. Merge order determines precedence: **later
sources override earlier ones** for the same top-level key.

1. **Base tokens** — Load from the AskeeDS `tokens/` directory (or your copy).
2. **Base theme** (optional) — Load a theme file with
   `Loader.load_theme(name, themes_dir)` and merge over base tokens
   (e.g. `dark`, `light`, `high-contrast`).
3. **Mod theme** (optional) — Load a theme file from the mod’s directory
   and merge again over the result.

**Merge semantics:** Shallow merge at the top level. If the mod theme
defines `color_roles`, that entire key replaces the previous
`color_roles`. To change only one role, the mod can either supply a
full `color_roles` dict or the engine can deep-merge `color_roles` and
`sets` (borders) so that per-role or per-style keys are overridden
individually.

Example (engine builds one Theme for a mod):

```python
loader = Loader()
tokens = loader.load_tokens_dir(askee_tokens_dir)
overlay = loader.load_theme("dark", askee_themes_dir)
tokens = {**tokens, **overlay}
if mod_themes_dir:
    mod_overlay = loader.load_theme("adventure_xyz", mod_themes_dir)
    tokens = {**tokens, **mod_overlay}
theme = Theme(tokens)
```

Mod theme files use the same shape as AskeeDS theme files: YAML with
top-level keys such as `color_roles`, `sets` (border styles), and
`bar` (filled/empty glyphs). See `themes/*.yaml` in the repo for
reference.

### Component override and extension

Components are stored in a single `dict[str, Component]`. The loader
adds or overwrites by component **name** (e.g. `room-card.default`,
`status-bar.default`). Load order matters: **later load wins** for the
same name.

1. **Base components** — Load from the AskeeDS `components/` directory
   (or your copy).
2. **Mod components** — Load from the mod’s component directory. Same
   name = override (replace). New name = extension (add).

Example:

```python
components = loader.load_components_dir(askee_components_dir)
if mod_components_dir:
    mod_components = loader.load_components_dir(mod_components_dir)
    components = {**components, **mod_components}
```

Mod component YAML must conform to the same schema as base components
(`components/_schema.yaml`). Validate with `askee-ds validate
--components <mod_components_dir>` (or your engine’s validator) so
that render specs, props, and categories remain valid.

### Suggested mod layout

A mod (adventure) can ship:

| Path (relative to mod root) | Purpose |
|-----------------------------|---------|
| `components/*.yaml`         | Override or add components. Same filename/component name = override. |
| `themes/<name>.yaml`        | Theme overlay. Engine loads by name (e.g. `adventure_xyz`) and merges over base theme. |
| `screens/*.yaml`            | Screen definitions that reference components (base or mod). |

The engine decides how to resolve mod root (e.g. by adventure id or
manifest). AskeeDS does not dictate the manifest format or
directory name; it only defines how to merge theme dicts and component
dicts once paths are known.

### Custom render types

If a mod introduces components that use a custom render type, the
engine must **register** that render type before rendering (e.g. with
`from askee_ds.render_types import register`). Load order is
unchanged: load base components, then mod components, then build
renderer/composer with the merged component dict. Register any custom
render types before the first `render` or `compose` call.

### Summary

| Concern              | Contract |
|----------------------|----------|
| Theme override       | Merge token dicts: base → base theme → mod theme. Shallow merge; later wins per top-level key. |
| Component override   | Merge component dicts: base then mod. Same name = replace; new name = add. |
| Mod layout           | Engine-defined. Suggested: `components/`, `themes/`, `screens/` under mod root. |
| Schema               | Mod components must satisfy the same component schema as base. |
| Custom render types  | Engine registers them before rendering; mod can use them in its component YAML. |

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
