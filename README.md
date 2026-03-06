# AskeeDS

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20the%20project-FF5E5B?style=flat&logo=ko-fi)](https://ko-fi.com/spencerg1350)

AskeeDS is an ASCII design system and component framework for TUI and
text-based games. It defines game UI components — menus, HUDs, inventory
screens, room cards, character sheets, and more — as structured YAML with
typed props and declarative render specs. A Python framework loads these
definitions, resolves a theme (colors, borders, bar glyphs), and produces
real ASCII output. **The look is retro (ASCII aesthetic); the target is
modern terminals and equipment** — default sizing assumes contemporary
terminal dimensions, not legacy hardware.

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

Tip: on macOS, the Python that runs `pip` may install the `askee-ds` script
into a directory that is not on your shell `PATH`. If you use a virtual
environment (`python3 -m venv .venv` then `source .venv/bin/activate` before
`pip install -e .`), the script will be on `PATH` while the venv is active.

### Try it

```bash
askee-ds validate
askee-ds list --status approved
askee-ds preview room-card.default \
  --props '{"title":"Cavern","description_text":"A dark cave.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
askee-ds compose screens/examples/adventure_main.yaml
```

If you see `command not found: askee-ds` (common on macOS), run the same
commands via Python: `python3 -m askee_ds.cli validate`, `python3 -m askee_ds.cli list --status approved`, etc.

---

## What you get

```
components/                 YAML component definitions (the product)
  _schema.yaml              meta-schema enforced by the validator
  core/                     19 components: buttons, inputs, display, feedback, navigation, layouts
  game/                     37 components: HUD, inventory, character, exploration, conversation, etc.
tokens/                     design tokens
  colors.yaml               10 semantic color roles (neutral, danger, arcane, nature, ...)
  borders.yaml              3 border character sets (single, heavy, double)
  typography.yaml           Figlet font conventions, line width rules
  sizing.yaml               terminal defaults for adaptive width/height (modern default 100×30)
themes/                     theme variants (override color_roles)
  dark.yaml, light.yaml, high-contrast.yaml (grayscale), experimental.yaml (color)
screens/                    YAML screen definitions (full-screen layouts)
  _schema.yaml              meta-schema for screen files
  examples/                 17 example game screens (title, conversation, adventure, etc.)
askee_ds/                   Python package
  loader.py                 loads YAML components and tokens
  composer.py               composes layout components and screens from YAML
  render_types/             modular render type registry (16 built-in types)
  adapters/rich.py          Rich adapter: ANSI-colored output
  adapters/textual.py       Textual adapter: AskeeWidget for TUI apps
  renderer.py               renders components from definitions
  theme.py                  resolves tokens to concrete values
  validator.py              validates components against _schema.yaml
  cli.py                    CLI: validate, preview, list, compose (--theme for preview/compose)
tests/                      framework and legacy tests
examples/
  quick_start.py            minimal hello-world
  all_components.py         visual catalog of all renderable components
  full_screen.py            composed game screen using Composer
  textual_app.py            live TUI demo using Textual adapter
DESIGNER_SIZING_WORKFLOW.md designer checklist for adaptive sizing (pause point)
```

56 components total. 24 are approved (proven, tested, and snapshot-locked);
32 are ideated (defined but not yet individually proven). All 56 render
from declarative specs. 17 example game screens demonstrate real layouts.

---

## What AskeeDS handles vs. what your engine handles

AskeeDS gives your game its **look** — the layout, components, and
visual structure. Everything else lives in your game engine.

| AskeeDS handles (the look) | Your engine handles (the logic) |
|---|---|
| Defining UI components (menus, HUDs, cards, sheets) as YAML | Managing game state (HP, inventory, turn order, quest progress) |
| Rendering ASCII output from data you pass in | Deciding *what* data to show and *when* to show it |
| Declaring interaction specs (focusable, key bindings) | Capturing keystrokes and running your event loop |
| Declaring animation frames (e.g. spinner) | Cycling through frames at the speed you choose |
| Pure text/ASCII rendering | Any pixel graphics, images, or GPU rendering you want |
| Laying out screens from component definitions | Networking, multiplayer sync, or server communication |
| Providing color roles and border styles | Audio, sound effects, or music |
| Defining component structure and validation | Save/load, persistence, and file storage |
| Offering 56 ready-made UI components | Generating levels, stories, items, NPCs, or any content |

**In short:** AskeeDS is a design system. You define what things look
like. Your engine decides what happens.

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

Run `askee-ds list` to see all 56 components, `askee-ds preview <name>`
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

## License and attribution

AskeeDS is released under the [MIT License](LICENSE). You are free to
use, modify, and distribute it in personal and commercial projects.

**If you use AskeeDS in your game or project, please credit:**

> AskeeDS by Spencer Goldade

Add this to your game's credits screen, README, or about page. The MIT
license requires preserving the copyright notice in source
distributions; crediting AskeeDS in your finished product is a
community expectation, not a legal mandate, but it helps others discover
the project and supports continued development.

---

## Contributing

Contributions are welcome. Before opening a pull request:

1. Run `askee-ds validate` (or `python3 -m askee_ds.cli validate` if the command is not on your PATH) to check YAML components.
2. Run `python3 -m pytest tests/ -v` to confirm all tests pass.
3. Follow the component lifecycle — new components start as `ideated`.
4. Update `CHANGELOG.md` under the **Unreleased** section.

If you ship a game or tool that uses AskeeDS, please include the
attribution above. Forks and derivatives should preserve the credit.

---

## Acknowledgments

This README's structure was inspired by
[Best README Template](https://github.com/othneildrew/Best-README-Template).

> **Make something weird and wonderful.** AskeeDS is meant to be copied,
> bent, and remixed. Build strange worlds, kind TUIs, tiny tools, or full
> games. If you ship something you're proud of: share a short write-up or
> screenshot; I'd love to see it! [Spencer on Bluesky](https://bsky.app/profile/monkeyslunch.bsky.social) [Spencer on Mastodon](https://mstdn.ca/@monkeyslunch)
