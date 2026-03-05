# AskeeDS

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20the%20project-FF5E5B?style=flat&logo=ko-fi)](https://ko-fi.com/spencerg1350)

AskeeDS is an ASCII design system and component framework for TUI and
text-based games. It defines game UI components — menus, HUDs, inventory
screens, room cards, character sheets, and more — as structured YAML with
typed props and declarative render specs. A Python framework loads these
definitions, resolves a theme (colors, borders, bar glyphs), and produces
real ASCII output.

```
+------------------------------------------+
| The Undercroft                           |
+------------------------------------------+
| A low-ceilinged stone chamber. Water     |
| drips from the walls and the air smells  |
| of damp earth.                           |
|                                          |
| Items:                                   |
|  rusty key                               |
|  torch (lit)                             |
| NPCs:                                    |
|  hooded figure                           |
+------------------------------------------+
| Exits:                                   |
|  north                                   |
|  east                                    |
+------------------------------------------+
```

---

## Who is this for?

- **Game designers**: Define screens and components as YAML + ASCII art.
  The framework enforces prop types and validates your work.
- **Developers**: Wire AskeeDS into a Python TUI, game engine, or any
  runtime that consumes structured data. The YAML definitions are the
  contract; the renderer is a reference implementation.
- **The Askee engine**: AskeeDS is the design system that the Askee game
  engine (separate project) will consume.

---

## What you get

```
components/                 YAML component definitions (the product)
  _schema.yaml              meta-schema enforced by the validator
  core/                     25 components: buttons, inputs, display, feedback, navigation, layouts
  game/                     38 components: HUD, inventory, character, exploration, conversation, etc.
tokens/                     design tokens
  colors.yaml               10 semantic color roles (neutral, danger, arcane, nature, ...)
  box-drawing.yaml          3 border character sets (single, heavy, double)
  typography.yaml           Figlet font conventions, line width rules
askee_ds/                   Python package
  loader.py                 loads YAML components and tokens
  renderer.py               renders components from definitions
  theme.py                  resolves tokens to concrete values
  validator.py              validates components against _schema.yaml
  cli.py                    CLI: validate, preview, list
tests/                      framework and legacy tests
```

63 components total. 10 are approved (proven core); 53 are ideated
(defined but not yet individually proven). All load, validate, and render.

---

## Getting started

### Install

```bash
git clone <this-repo-url>
cd askeeDS
pip install -e .
```

Only dependency: [PyYAML](https://pyyaml.org/).

### Validate

```bash
askee-ds validate
# OK — 63 components validated, 0 errors.
```

### Preview a component

```bash
askee-ds preview room-card.default \
  --props '{"title":"Cavern","description_text":"A dark cave.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
```

### List components

```bash
# All approved components
askee-ds list --status approved

# All HUD components
askee-ds list --prefix status-bar
```

### Use the Python API

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
# +------------------------------------------------+
# | HP: 85/100  |  The Clearing  |  Turn 12        |
# +------------------------------------------------+
```

### Validate on load (optional)

```python
loader = Loader(schema_path="components/_schema.yaml")
components = loader.load_components_dir("components/")
# Any schema violations print as warnings to stderr.
```

---

## Component examples

Components are YAML definitions with typed props and a render spec. The
framework turns definition + props + theme into ASCII output.

**status-bar.default** — Single-line HUD showing HP, location, and turn.

```
+------------------------------------------------+
| HP: 85/100  |  The Clearing  |  Turn 12        |
+------------------------------------------------+
```

**character-sheet.compact** — Compact stat block with name header and resource bars.

```
+--------------------------------+
| Kael the Wanderer              |
+--------------------------------+
| HP    [████████░░] 8/10        |
| MP    [██████░░░░] 3/5         |
| Stamina [████████░░] 6/8       |
+--------------------------------+
```

**tracker.objective** — One line per objective; unchecked/checked.

```
+------------------------------+
| [x] Find the key             |
| [x] Talk to the guard        |
| [ ] Open the sealed door     |
+------------------------------+
```

**button.icon** — Button with leading icon.

```
[☆] Star this
```

**breadcrumb.inline** — Inline location path.

```
World > Dungeon > Level 3
```

Run `askee-ds list` to see all 63 components, or `askee-ds preview <name>`
to render any of them.

---

## How to add a new component

1. Pick a category file (e.g. `components/game/hud.yaml`).
2. Add a YAML definition:

```yaml
cooldown.timer:
  category: game/hud
  description: Turn-based ability cooldown display.
  status: ideated
  props:
    label:
      type: string
      required: true
    turns_left:
      type: integer
      required: true
  render:
    type: inline
    template: "{label}: {turns_left} turns"
  art: |2
    Fireball: 3 turns
```

3. Validate: `askee-ds validate`
4. Preview: `askee-ds preview cooldown.timer --props '{"label":"Fireball","turns_left":3}'`

### Component status lifecycle

Components progress through these statuses:

| Status | Meaning |
|--------|---------|
| `ideated` | Defined but not yet proven. Props and render spec may change. |
| `to-do` | Design intent confirmed; implementation planned. |
| `in-progress` | Actively being designed or refined. |
| `in-review` | Ready for review. |
| `approved` | Proven, stable, and ready for engine consumption. |
| `deprecated` | Superseded; will be removed in a future version. |
| `cancelled` | Abandoned; kept for reference only. |

### Render types

| Type | What it does | Example |
|------|-------------|---------|
| `inline` | Single-line template interpolation. | `[☆] Star this` |
| `join` | Joins an array of items with a separator. | `World > Dungeon > Level 3` |
| `box` | Bordered box with sections (header, text, list, bars, etc.). | Room cards, status bars. |
| `reference` | Falls back to the reference ASCII art. Needs a specialized renderer. | Layouts, minimaps, trees. |

---

## How to use AskeeDS in another project

### Option A — Copy the YAML definitions

Copy `components/` and `tokens/` into your project. Parse the YAML with
any language's YAML library. The component definitions are the contract;
build your own renderer for your runtime.

### Option B — Use the Python package

```bash
pip install -e path/to/askeeDS
```

Then use `from askee_ds import Loader, Theme, Renderer` in your code.

### Option C — Git submodule

```bash
git submodule add <this-repo-url> vendor/askee-ds
```

Pin to a tag and update when ready. See [CHANGELOG.md](CHANGELOG.md) for
migration notes between versions.

---

## Validation and testing

```bash
# Validate all YAML components against the schema
askee-ds validate

# Run framework tests (Loader, Renderer, Theme, Validator)
python3 -m unittest discover -s tests -v

# Run legacy tools tests (maps, decorations)
python3 -m unittest discover -s tools
```

The schema (`components/_schema.yaml`) enforces:
- Required fields: `category`, `description`, `status`, `render`
- Valid status values, category prefixes, prop types
- Valid render types, border styles, section types

---

## Tools and dependencies

| Name | Use | Required? |
|------|-----|-----------|
| [PyYAML](https://pyyaml.org/) | Parse YAML definitions and tokens. | Yes |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Figlet banner text for `typography.banner`. | Optional (`pip install -e ".[banner]"`) |

---

## Versioning

AskeeDS uses semantic versioning recorded in [VERSION](VERSION) and
[CHANGELOG.md](CHANGELOG.md).

- **Major**: Breaking changes (renamed/removed components or required props).
- **Minor**: New components, new optional props, new tokens.
- **Patch**: Fixes, documentation, tooling.

---

## Acknowledgments

This README's structure was inspired by
[Best README Template](https://github.com/othneildrew/Best-README-Template).

> **Make something weird and wonderful.** AskeeDS is meant to be copied,
> bent, and remixed — build strange worlds, kind TUIs, tiny tools, or full
> games. If you ship something you're proud of, consider sharing a short
> write-up or screenshot and crediting AskeeDS so others can discover it too.
