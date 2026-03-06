# AskeeDS

```
 .d8b.  .d8888. db   dD d88888b d88888b d8888b. .d8888. 
d8' `8b 88'  YP 88 ,8P' 88'     88'     88  `8D 88'  YP 
88ooo88 `8bo.   88,8P   88ooooo 88ooooo 88   88 `8bo.   
88~~~88   `Y8b. 88`8b   88~~~~~ 88~~~~~ 88   88   `Y8b. 
88   88 db   8D 88 `88. 88.     88.     88  .8D db   8D 
YP   YP `8888Y' YP   YD Y88888P Y88888P Y8888D' `8888Y' 
--------------------------------------------------------
    An ASCII-based design system by Spencer Goldade
```

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20the%20project-FF5E5B?style=flat&logo=ko-fi)](https://ko-fi.com/spencerg1350)

**AskeeDS is a design system for text-based games and TUIs**
56 components, declarative YAML, themes, and a Python renderer that turns structured data into real ASCII output.

It's the UI layer your game engine doesn't have to build. You pass in the data; AskeeDS handles the look.

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

> **Make something weird and wonderful.** AskeeDS is meant to be copied, bent, and remixed. Build strange worlds, kind TUIs, tiny tools, or full games. If you ship something: [find me on Bluesky](https://bsky.app/profile/monkeyslunch.bsky.social) or [Mastodon](https://mstdn.ca/@monkeyslunch). I'd genuinely love to see it.

---

## What it looks like in practice

Components are defined in YAML with typed props. The framework resolves your theme and renders real ASCII, with no manual string-building required.

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

Run `askee-ds list` to see all 56, `askee-ds preview <name>` to render any of them, or `python examples/all_components.py` for the full visual catalog.

---

## Who is this for?

**Game designers** — Define screens and components as YAML + ASCII art. The framework enforces prop types and validates your work so you catch mistakes before runtime, not during.

**Developers** — Wire AskeeDS into a Python TUI, game engine, or any runtime that consumes structured data. The YAML definitions are the contract; the renderer is a reference implementation you can swap out.

**The Askee engine** — AskeeDS is the design system the [Askee game engine](https://github.com/spencergoldade) (separate project) will consume. It's extracted and open so other projects can use it too.

---

## Quick start

Pick the guide that fits where you're coming from:

- **I'm a designer** — [GUIDE.md](GUIDE.md): concepts, vocabulary, authoring components and screens in YAML.
- **I'm a developer** — [INTEGRATING.md](INTEGRATING.md): the Python API, CLI, adapters, and how to extend the system.
- **I need a reference** — [REFERENCE.md](REFERENCE.md): every render type, section type, token, and field definition.

### Install

```bash
git clone <this-repo-url>
cd askeeDS
pip install -e .
```

> **macOS tip:** If `askee-ds` isn't found after install, use a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`, then re-run `pip install -e .`. Alternatively, prefix every command with `python3 -m askee_ds.cli`.

### Try it

```bash
askee-ds validate
askee-ds list --status approved
askee-ds preview room-card.default \
  --props '{"title":"Cavern","description_text":"A dark cave.","items":[],"npcs":[],"exits":[{"id":"n","label":"north"}]}'
askee-ds compose screens/examples/adventure_main.yaml
```

---

## AskeeDS handles the look. Your engine handles the rest.

This boundary is intentional. AskeeDS is a design system, not a game engine. It gives you the UI layer so you don't have to build it yourself.

| AskeeDS | Your engine |
|---|---|
| 56 UI components (menus, HUDs, cards, sheets) defined in YAML | Game state — HP, inventory, turn order, quests |
| Rendering ASCII output from data you pass in | Deciding *what* to show and *when* |
| Interaction specs (focusable fields, key bindings) | The actual event loop and keystroke handling |
| Animation frame declarations (spinners, etc.) | Cycling frames at your chosen speed |
| Color roles, border styles, themes | Audio, sound effects, music |
| Screen layout from component definitions | Save/load, persistence, networking |
| Schema validation for components and screens | Level generation, story, NPCs, content |

---

## What's included

```
components/          56 YAML component definitions (the product)
  core/              19 components: buttons, inputs, display, feedback, navigation, layouts
  game/              37 components: HUD, inventory, character, exploration, conversation, etc.

tokens/              Design tokens
  colors.yaml        10 semantic color roles (neutral, danger, arcane, nature, ...)
  borders.yaml       3 border character sets (single, heavy, double)
  typography.yaml    Figlet font conventions, line width rules
  sizing.yaml        Terminal defaults — modern 100×30, not legacy hardware

themes/              dark.yaml · light.yaml · high-contrast.yaml · experimental.yaml

screens/             17 example full-screen game layouts (title, adventure, conversation, etc.)

askee_ds/            Python package: loader, renderer, composer, theme resolver,
                     validator, CLI, Rich adapter, Textual adapter, 16 render types
```

All 56 components are approved and render from declarative specs. 24 have snapshot golden files for visual regression testing.

---

## Dependencies

| Library | Purpose | Required? |
|---|---|---|
| [PyYAML](https://pyyaml.org/) | Parse component and token definitions | Yes |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Figlet banner text (`typography.banner`) | `pip install -e ".[banner]"` |
| [Rich](https://github.com/Textualize/rich) | ANSI-colored terminal output | `pip install -e ".[rich]"` |
| [Textual](https://github.com/Textualize/textual) | TUI widgets via `AskeeWidget` | `pip install -e ".[textual]"` |

---

## Versioning

Tracked in [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md), following semantic versioning:

- **Major** — Breaking changes (renamed/removed components or required props)
- **Minor** — New components, new optional props, new tokens
- **Patch** — Fixes, documentation, tooling

---

## Contributing

Contributions are welcome. Before opening a pull request:

1. Run `askee-ds validate` to check YAML components.
2. Run `python3 -m pytest tests/ -v` to confirm all tests pass.
3. Follow the component lifecycle — new components start as `ideated`.
4. Update `CHANGELOG.md` under **Unreleased**.

---

## License and attribution

Released under the [MIT License](LICENSE). Use it freely in personal and commercial projects.

If AskeeDS powers something you ship, please credit it:

> AskeeDS by Spencer Goldade

A line in your credits screen, README, or about page is all it takes. You're also welcome to use the ASCII wordmark from `CREDITS_LOGO.txt` directly in your game's credits. It's not a legal requirement, it's just how open source stays discoverable.