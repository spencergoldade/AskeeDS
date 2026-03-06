# AskeeDS Reference

A structured lookup for every field, render type, section type, token,
and interaction option in AskeeDS. Open this when you need to answer
"what fields can I use here?" or "what does this value mean?"

For tutorials and concepts, see [GUIDE.md](GUIDE.md). For Python API
and developer integration, see [INTEGRATING.md](INTEGRATING.md).

---

## Component fields

Every component YAML entry supports these fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `category` | Yes | string | Where it belongs. Must start with `core/` or `game/`. |
| `description` | Yes | string | One sentence explaining what the component does. |
| `status` | Yes | string | Lifecycle status (see [Status values](#status-values)). |
| `render` | Yes | dict | The render spec — how the component draws (see [Render types](#render-types)). |
| `props` | No | dict | Data the component needs. Each prop has a `type` and `required` flag. |
| `art` | No | string | Reference ASCII art showing expected output. |
| `default_color_role` | No | string | Default color role applied when none is specified at render time. |
| `interaction` | No | dict | Keyboard interaction spec (see [Interaction fields](#interaction-fields)). |
| `variant` | No | string | Lists the available variants (e.g. `"default \| stats"`). |
| `notes` | No | string | Design notes for other designers. |

### Category prefixes

| Prefix | Contains |
|--------|----------|
| `core/` | General UI: `buttons`, `display`, `feedback`, `inputs`, `layouts`, `navigation`. |
| `game/` | Game-specific: `character`, `conversation`, `exploration`, `hud`, `inventory`, `menus`, `notifications`, `screens`, `trackers`. |

---

## Prop types

Each prop in a component's `props` block has these fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `type` | Yes | string | The data type (see table below). |
| `required` | Yes | boolean | Whether the prop must be provided. |
| `element` | No | dict | Shape of each item in an array (field names and types). |
| `element_type` | No | string | For array props: specifies the type of array elements when they aren't objects (e.g. `element_type: string` for string arrays). |

### Valid prop types

| Type | What it accepts | Example value |
|------|----------------|---------------|
| `string` | Any text. | `"The Clearing"` |
| `integer` | Whole numbers. | `85` |
| `number` | Numbers with decimals. | `3.14` |
| `boolean` | `true` or `false`. | `true` |
| `array` | A list of items. Define the item shape with `element` or `element_type`. | `[{id: n, label: north}]` |

---

## Render types

AskeeDS has 16 render types. Each one produces a different shape of
output.

### `inline`

Single line of text with blanks filled in from props.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `template` | Yes | Text pattern. Use `{prop_name}` for blanks. |

**Example:**

```yaml
render:
  type: inline
  template: "{label}: {value}"
```

```
HP: 85
```

---

### `join`

Joins items from an array prop into a single line with a separator.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop to iterate. |
| `separator` | Yes | Text between each item. |
| `template` | Yes | Pattern for each item. |
| `prefix` | No | Text before the joined items. |

**Example:**

```yaml
render:
  type: join
  over: directions
  separator: "  "
  template: "{label}"
  prefix: "Exits: "
```

```
Exits: north  south  east
```

---

### `box`

Bordered rectangle with structured sections inside.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `width` | Yes | Box width in characters, or `fill` / `content` for adaptive sizing. |
| `border` | Yes | Border style: `single`, `heavy`, or `double`. |
| `sections` | Yes | List of section objects (see [Box section types](#box-section-types)). |

**Sizing fields** (optional, used with adaptive widths):

| Field | Description |
|-------|-------------|
| `min_width` | Never narrower than this. |
| `max_width` | Never wider than this. |
| `height` | Fixed height, `fill`, or `content`. |
| `min_height` | Never shorter than this. |
| `max_height` | Never taller than this. |

Eight components use `width: fill` with `min_width`/`max_width` constraints.

**Example:**

```yaml
render:
  type: box
  width: 40
  border: single
  sections:
    - type: header
      text: "{title}"
    - type: divider
    - type: wrap
      text: "{body_text}"
      indent: 1
```

```
+-- Card title ------------------------+
| Body text goes here and may wrap     |
| across multiple lines when needed.   |
+--------------------------------------+
```

---

### `table`

Auto-width column table with a header separator row.

**Fields:** None beyond `type: table`. The component's `columns` and
`rows` props provide the data.

**Example:**

```yaml
render:
  type: table
```

```
+----------+---------+-------+
|   Col1   |  Col2   | Col3  |
+----------+---------+-------+
| Value 1  | Value 2 | 123   |
+----------+---------+-------+
```

---

### `banner`

Large multi-line ASCII text using Figlet fonts. Falls back to the
component's reference art when the Figlet library is not installed.

**Fields:** None beyond `type: banner`. The `text` prop provides the
content.

**Example:**

```yaml
render:
  type: banner
```

```
    ___  ____  _  __ ______
   / _ )/ __ \/ |/ // __/ /
  / _  / /_/ /    /_/ /_/ 
  /____/\____/_/|_/___/___ 
```

---

### `frames`

Returns a single frame from an animation sequence. The consumer is
responsible for cycling through frames at runtime.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `prop` | Yes | Name of the array prop containing the frame strings. |

**Example:**

```yaml
render:
  type: frames
  prop: frames
```

Given `frames: ["|", "/", "-", "\\"]`, renders:

```
|
```

---

### `bubble`

Speech bubble with a directional tail for dialogue.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `tail` | Yes | Tail direction: `left` or `right`. |

**Example:**

```yaml
render:
  type: bubble
  tail: left
```

```
    +-----------------------------+
   / The guard nods. "Go north."  |
  +-------------------------------+
```

---

### `tree`

Indented tree with `├──` / `└──` / `│` connectors for hierarchical
data.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `prop` | Yes | Name of the array prop containing tree nodes. Each node has `label` and optional `children`. |
| `template` | Yes | Pattern for each node's label. |

**Example:**

```yaml
render:
  type: tree
  prop: nodes
  template: "{label}"
```

```
Combat
├── Strike
├── Block
└── Parry
Lore
├── Identify
└── Persuade
```

---

### `grid`

Bordered cell grid for slot-based layouts (inventories, equipment).

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `prop` | Yes | Name of the array prop containing slot items. |
| `columns_prop` | Yes | Name of the integer prop for number of columns. |
| `cell_width` | Yes | Width of each cell in characters. |

**Example:**

```yaml
render:
  type: grid
  prop: slots
  columns_prop: columns
  cell_width: 8
```

```
+--------+--------+--------+--------+
| slot 1 | slot 2 | slot 3 | slot 4 |
+--------+--------+--------+--------+
| slot 5 | slot 6 | slot 7 | slot 8 |
+--------+--------+--------+--------+
```

---

### `charmap`

2D character grid with an optional legend, used for minimaps.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `prop` | Yes | Name of the 2D array prop (array of arrays). |
| `legend_prop` | No | Name of the array prop for legend entries (each with `char` and `label`). |

**Example:**

```yaml
render:
  type: charmap
  prop: grid
  legend_prop: legend_entries
```

```
+----------+
| ....#....|
| .P.#.....|
| ....D....|
+----------+
  . empty  # wall  P you  D door
```

---

### `clock`

Segment-style progress circle for countdowns and timers.

**Fields:** None beyond `type: clock`. Uses `label`, `segments`, and
`filled` props.

**Example:**

```yaml
render:
  type: clock
```

```
Quest: Find the key
[●●○○]   2 / 4
```

---

### `stage_track`

Horizontal multi-stage track showing progression or advancing threats.

**Fields:** None beyond `type: stage_track`. Uses `label`, `stages`,
and `current_stage_index` props.

**Example:**

```yaml
render:
  type: stage_track
```

```
Invasion front:
[ Safe ]-[ Skirmishes ]-[ Occupied ]-[ Overrun ]
   ^
```

---

### `art_lookup`

Returns a decoration's ASCII art. Falls back to the component's
reference art if the decoration is not found.

**Fields:** None beyond `type: art_lookup`.

---

### `stack`

Vertically stacked bordered blocks for full-screen layouts.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `prop` | Yes | Name of the array prop holding pre-rendered block strings. |
| `border` | Yes | Border style: `single`, `heavy`, or `double`. |

**Example:**

```yaml
render:
  type: stack
  prop: blocks
  border: single
```

```
+------------------------------------------------+
| block 1 (e.g. status bar)                      |
+------------------------------------------------+
| block 2 (main content)                         |
+------------------------------------------------+
| block 3 (input)                                |
+------------------------------------------------+
```

---

### `columns`

Side-by-side panes separated by a vertical border.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `left_prop` | Yes | Name of the prop holding pre-rendered left pane content. |
| `right_prop` | Yes | Name of the prop holding pre-rendered right pane content. |
| `width_prop` | No | Name of the integer prop for left pane width (default 20). |
| `border` | Yes | Border style. |

**Example:**

```yaml
render:
  type: columns
  left_prop: left_content
  right_prop: right_content
  width_prop: left_width
  border: single
```

```
+------------------+-----------------------------+
| left pane        | right pane                  |
+------------------+-----------------------------+
```

---

### `shell`

Full application shell with header, sidebar, and content area.

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `header_prop` | Yes | Name of the prop holding pre-rendered header content. |
| `sidebar_prop` | Yes | Name of the prop holding pre-rendered sidebar content. |
| `content_prop` | Yes | Name of the prop holding pre-rendered content area. |
| `width_prop` | No | Name of the integer prop for sidebar width. |
| `border` | Yes | Border style. |

**Example:**

```yaml
render:
  type: shell
  header_prop: header
  sidebar_prop: sidebar
  content_prop: content
  width_prop: sidebar_width
  border: single
```

```
+------------------------------------------------+
| App Title                  [user] [settings]   |
+------------+-----------------------------------+
| nav item 1 | content area                      |
| nav item 2 |                                   |
+------------+-----------------------------------+
```

---

## Box section types

These are the section types you can use inside a `box` render spec's
`sections` list.

### `header`

Title row at the top of a box.

| Field | Required | Description |
|-------|----------|-------------|
| `text` | Yes | The header text. Supports `{prop_name}` blanks. |

```yaml
- type: header
  text: "{title}"
```

```
+-- The Clearing ----------------------------+
```

---

### `divider`

Horizontal line separator.

No additional fields — just `type: divider`.

```yaml
- type: divider
```

```
+--------------------------------------------+
```

---

### `text`

Single line of text. Does not wrap — if the text is longer than the
box, it gets truncated.

| Field | Required | Description |
|-------|----------|-------------|
| `text` | Yes | The text content. Supports `{prop_name}` blanks. |

```yaml
- type: text
  text: "  {item_name}"
```

```
|  Iron Sword                                |
```

---

### `wrap`

Text that wraps to fit inside the box width.

| Field | Required | Description |
|-------|----------|-------------|
| `text` | Yes | The text to wrap. Supports `{prop_name}` blanks. |
| `indent` | No | Number of extra spaces to indent each wrapped line. |

```yaml
- type: wrap
  text: "{description_text}"
  indent: 1
```

```
| A low-ceilinged stone chamber. Water       |
| drips from the walls and the air smells    |
| of damp earth.                             |
```

---

### `blank`

An empty row for vertical spacing.

No additional fields — just `type: blank`.

```yaml
- type: blank
```

```
|                                            |
```

---

### `list`

One row per item in an array prop.

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop to iterate. |
| `template` | Yes | Pattern for each item. |
| `label` | No | Section label printed above the list (e.g. `"Items"`). |
| `if_empty` | No | Set to `hide` to omit the section when the array is empty. |

```yaml
- type: list
  label: "Items"
  over: items
  template: "  {label}"
  if_empty: hide
```

```
| Items:                                     |
|  rusty key                                 |
|  torch (lit)                               |
```

---

### `bars`

Resource bars from an array prop. Each item renders a filled/empty bar.

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop. Each item needs `label`, `current`, and `max`. |
| `template` | Yes | Pattern with `{label}`, `{bar}`, `{current}`, `{max}`. |
| `bar_width` | Yes | Width of the bar in characters. |

```yaml
- type: bars
  over: stats
  bar_width: 10
  template: " {label:<5} [{bar}] {current}/{max}"
```

```
| HP    [████████░░] 8/10                    |
| MP    [██████░░░░] 3/5                     |
```

---

### `progress`

A single progress bar (not from an array).

```yaml
- type: progress
```

---

### `numbered_list`

Items prefixed with sequential numbers (1. 2. 3.).

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop. |
| `template` | Yes | Pattern for each item. |

```yaml
- type: numbered_list
  over: options
  template: "{label}"
```

```
| 1. Go north                               |
| 2. Talk to guard                           |
| 3. Take lamp                              |
```

---

### `checked_list`

Items with `[x]` or `[ ]` checkboxes based on a boolean field.

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop. |
| `check_prop` | Yes | Name of the boolean field in each item that determines checked state. |
| `template` | Yes | Pattern for each item's label. |

```yaml
- type: checked_list
  over: objectives
  check_prop: checked
  template: "{label}"
```

```
| [x] Find the key                          |
| [ ] Open the door                         |
```

---

### `active_list`

Items with a `>` marker on the currently selected one.

| Field | Required | Description |
|-------|----------|-------------|
| `over` | Yes | Name of the array prop. |
| `active_prop` | Yes | Name of the prop holding the active item's ID. |
| `marker` | Yes | The marker character(s) for the active item (e.g. `">"`). |
| `template` | Yes | Pattern for each item. |

```yaml
- type: active_list
  over: links
  active_prop: active_id
  marker: ">"
  template: "{label}"
```

```
|   Home                                     |
| > Settings                                 |
|   About                                    |
```

---

## Design tokens

Tokens are design decisions stored in `tokens/` and shared across all
components.

### Color roles

10 semantic roles, each with background, foreground, border, and accent
colors:

| Role | Description | When to use |
|------|-------------|-------------|
| `neutral` | Default theme; no strong tint. | Most components. |
| `danger` | Red tint for threat, error, death. | Damage, errors, death screens. |
| `success` | Green/gold for victory, confirmation. | Healing, saved, accepted. |
| `arcane` | Purple/magenta for magic, rare systems. | Spells, enchantment, arcane lore. |
| `nature` | Green tones for outdoors, growth. | Safe zones, forests, gardens. |
| `frost` | Cyan/blue for cold, water, tech. | Ice areas, water, technology. |
| `rare` | Blue tint for rare items. | Quality indicators, rare loot. |
| `legendary` | Gold/amber for legendary, premium. | Epic loot, achievements. |
| `dungeon` | Dark stone, underground. | Dark interiors, caves, ruins. |
| `forest` | Green-brown forest zone. | Woodland areas, natural settings. |

Set a default on any component:

```yaml
default_color_role: danger
```

### Border styles

Three border character sets defined in `tokens/borders.yaml`:

**single** — Standard ASCII (7-bit safe, works on all terminals):

```
+--------+
| single |
+--------+
```

**heavy** — Heavier Unicode borders:

```
┏━━━━━━━━┓
┃ heavy  ┃
┗━━━━━━━━┛
```

**double** — Double-line Unicode borders:

```
╔════════╗
║ double ║
╚════════╝
```

Bar characters (used by `bars` sections):

| Glyph | Meaning |
|-------|---------|
| `█` | Filled segment. |
| `░` | Empty segment. |

### Typography

Defined in `tokens/typography.yaml`. Covers Figlet font conventions and
line width rules for the `banner` render type.

### Sizing defaults

Defined in `tokens/sizing.yaml`. The system targets **modern terminals**
(not retro hardware); defaults are set for typical contemporary sizes.

| Setting | Default |
|---------|---------|
| `terminal.default_width` | 100 |
| `terminal.default_height` | 30 |
| `terminal.min_width` | 40 |
| `terminal.min_height` | 10 |

### Theme variants

Theme files in `themes/` override `color_roles` so you can switch palettes
without changing component definitions. The system is built **grayscale-first**;
one theme adds color for experimentation.

| Theme | Description |
|-------|-------------|
| `dark` | Grayscale: dark background, light text. Good for low light. |
| `light` | Grayscale: light background, dark text. Good for bright environments. |
| `high-contrast` | Grayscale: black and white, maximum contrast for accessibility. |
| `experimental` | Full color palette. **Experimental** — may change in future releases. |

Use a theme from the CLI:

```bash
askee-ds preview room-card.default --theme dark
askee-ds compose screens/examples/adventure_main.yaml --theme high-contrast
```

From code: load base tokens from `tokens/`, then load a theme with
`Loader.load_theme(name, themes_dir)` and merge the returned dict over
tokens before passing to `Theme(tokens)`.

**Accessibility:** Prefer `high-contrast` for users who need maximum
readability. Grayscale themes avoid relying on color alone to convey meaning.

---

## Interaction fields

The `interaction` block declares how a component responds to keyboard
input. All fields are optional — omit the block entirely for
display-only components.

| Field | Type | Description |
|-------|------|-------------|
| `focusable` | boolean | Whether the component can receive keyboard focus. |
| `actions` | array | List of keyboard actions the component supports. |
| `scrollable` | boolean | Whether the component supports scrolling. |

### Action fields

Each action in the `actions` array has:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Identifier for the action (e.g. `activate`, `select_next`). |
| `keys` | Yes | Array of key names that trigger this action. |
| `description` | No | Human-readable description of what the action does. |

### Valid key names

`enter`, `space`, `escape`, `tab`, `up`, `down`, `left`, `right`,
`backspace`, `delete`, `home`, `end`, `page_up`, `page_down`.

---

## Screen fields

Screen YAML files (under `screens/`) define full-screen layouts.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Screen identifier (e.g. `adventure.main`). |
| `description` | Yes | string | What this screen shows. |
| `layout` | Yes | string | Layout component to use (e.g. `layout.stack`). |
| `slots` | Yes | dict | Slot data to fill into the layout. |
| `available_width` | No | integer | Override terminal width for this screen. |
| `available_height` | No | integer | Override terminal height for this screen. |

### Slot entry types

Each slot entry can be one of:

| Type | Shape | Description |
|------|-------|-------------|
| Component | `{component: "name", props: {...}}` | Render a component with props. |
| Nested layout | `{component: "layout.name", slots: {...}}` | Compose a layout recursively. |
| Plain text | `{text: "..."}` | Insert a plain string. |
| Array | `[entry, entry, ...]` | A list of the above (for array-typed slots like `blocks`). |

---

## Status values

| Status | Meaning |
|--------|---------|
| `ideated` | New idea. Design may change. |
| `to-do` | Design intent confirmed. Implementation planned. |
| `in-progress` | Actively being designed or refined. |
| `in-review` | Ready for review. |
| `approved` | Proven, stable, ready for use. |
| `deprecated` | Being replaced. Will be removed in a future version. |
| `cancelled` | Abandoned. Kept for reference only. |
