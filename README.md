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

## Quick start

Pick the guide that matches your role:

- **I'm a designer** — Read [GUIDE.md](GUIDE.md) to learn concepts,
  vocabulary, and how to author components and screens in YAML.
- **I'm a developer** — Read [INTEGRATING.md](INTEGRATING.md) for the
  Python API, CLI, adapters, and how to extend the system.
- **I need to look something up** — Open [REFERENCE.md](REFERENCE.md)
  for render types, section types, tokens, and every field definition.

### Install

```bash
git clone <this-repo-url>
cd askeeDS
pip install -e .
```

### Try it

```bash
askee-ds validate
askee-ds list --status approved
askee-ds preview room-card.default \
  --props '{"title":"Cavern","description_text":"A dark cave.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
askee-ds compose screens/examples/adventure_main.yaml
```

---

## What you get

```
components/                 YAML component definitions (the product)
  _schema.yaml              meta-schema enforced by the validator
  core/                     20 components: buttons, inputs, display, feedback, navigation, layouts
  game/                     38 components: HUD, inventory, character, exploration, conversation, etc.
tokens/                     design tokens
  colors.yaml               10 semantic color roles (neutral, danger, arcane, nature, ...)
  borders.yaml              3 border character sets (single, heavy, double)
  typography.yaml           Figlet font conventions, line width rules
  sizing.yaml               terminal defaults for adaptive width/height
screens/                    YAML screen definitions (full-screen layouts)
  _schema.yaml              meta-schema for screen files
  examples/                 example screens
askee_ds/                   Python package
  loader.py                 loads YAML components and tokens
  composer.py               composes layout components and screens from YAML
  render_types/             modular render type registry (16 built-in types)
  adapters/rich.py          Rich adapter: ANSI-colored output
  adapters/textual.py       Textual adapter: AskeeWidget for TUI apps
  renderer.py               renders components from definitions
  theme.py                  resolves tokens to concrete values
  validator.py              validates components against _schema.yaml
  cli.py                    CLI: validate, preview, list, compose
tests/                      framework and legacy tests
examples/
  quick_start.py            minimal hello-world
  all_components.py         visual catalog of all renderable components
  full_screen.py            composed game screen using Composer
  textual_app.py            live TUI demo using Textual adapter
```

58 components total. 10 are approved (proven core); 48 are ideated
(defined but not yet individually proven). All 58 render from
declarative specs.

---

## What AskeeDS does not do

AskeeDS is focused on **defining and rendering game UI**. These are
explicitly outside its scope:

- **Game logic or state management.** AskeeDS produces ASCII output from
  data you provide. It does not manage HP, inventory, turn order, or
  any game state — that is the engine's job.
- **Input handling or event loops.** Components can declare interaction
  specs (focusable, keyboard bindings), but AskeeDS does not capture
  keystrokes or run an event loop. The consumer wires interaction to
  their runtime.
- **Animation playback.** Components like `spinner.loading` declare
  frames, but cycling through them at runtime is the consumer's
  responsibility.
- **Pixel graphics, images, or GPU rendering.** AskeeDS is pure
  text/ASCII. No bitmaps, no shaders, no terminal graphics protocols.
- **Networking or multiplayer.** No server communication, no
  synchronization. If your game is multiplayer, the engine manages that.
- **Audio or sound.** No sound effects, no music. Pair AskeeDS with a
  separate audio library if needed.
- **Persistence or save/load.** AskeeDS does not read or write save
  files. The engine owns data storage.
- **Content generation.** AskeeDS does not generate levels, stories,
  items, or NPCs. It provides the UI components to *display* them.

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

Run `askee-ds list` to see all 58 components, `askee-ds preview <name>`
to render any of them, or `python examples/all_components.py` to see
every renderable component at once.

---

## Tools and dependencies

| Name | Use | Required? |
|------|-----|-----------|
| [PyYAML](https://pyyaml.org/) | Parse YAML definitions and tokens. | Yes |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Figlet banner text for `typography.banner`. | Optional (`pip install -e ".[banner]"`) |
| [Rich](https://github.com/Textualize/rich) | ANSI-colored output via the Rich adapter. | Optional (`pip install -e ".[rich]"`) |
| [Textual](https://github.com/Textualize/textual) | TUI widgets via the Textual adapter. | Optional (`pip install -e ".[textual]"`) |

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
