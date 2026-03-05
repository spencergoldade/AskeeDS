# AskeeDS Designer's Guide

AskeeDS is a toolkit for designing text-based game interfaces. You
describe what a UI element looks like and what data it needs using YAML
files, and the system turns that into real ASCII output — bordered
boxes, status bars, menus, room cards, and more.

This guide walks you through everything you need to know to design
components and screens. No programming experience required. Everything
here uses YAML files and the `askee-ds` command line tool.

---

## Core vocabulary

Before you start, here are the key terms you will see throughout
AskeeDS. Each one is simple — read through these once, and the rest of
the guide will make sense.

**Component** — A reusable UI building block. A button, a room card, a
status bar, a menu. Each component is defined in a YAML file under
`components/`.

**Props** — The data a component needs to display. Think of them like
blanks in a form: "title goes here," "HP value goes here." When someone
uses your component, they fill in the props.

**Render spec** — The recipe that tells the system how to draw the
component. "Use a box, put a header at the top, then a list of items
below it." You write this in YAML — you describe what you want, not how
to build it.

**Render type** — The overall shape of the output. `inline` is a single
line of text. `box` is a bordered rectangle with sections inside.
`table` is columns and rows. There are 16 render types in total (see
[REFERENCE.md](REFERENCE.md) for the full list).

**Section** — A piece inside a box. A header row, a divider line, a
list of items, a progress bar. You stack sections to build up the
content of a box component.

**Token** — A design decision stored separately from components. Which
characters draw borders, which colors mean "danger," how wide a
terminal is. Tokens live in `tokens/` and apply to every component.

**Screen** — A full game view made by combining multiple components. You
define a screen in a YAML file under `screens/`, and the system
assembles the pieces into a complete layout.

**Interaction spec** — A declaration of how a component responds to
keyboard input. "This button can receive focus and is activated with
Enter or Space." You add an `interaction` block to your component.

---

## Your first component

Let's create a simple one-line component that displays a cooldown timer.

### 1. Pick a file

Components live in YAML files under `components/`. Each file holds
related components. For a game HUD element, open
`components/game/hud.yaml`.

### 2. Add the definition

Add this to the end of the file:

```yaml
cooldown.timer:
  category: game/hud
  description: Shows an ability name and how many turns until it's ready.
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

Here's what each part means:

- `cooldown.timer` — The component's name. Use `category.variant` format.
- `category` — Where it belongs. Must start with `core/` or `game/`.
- `description` — One sentence explaining what it does.
- `status: ideated` — It's new and not yet proven. This is where every
  component starts.
- `props` — The blanks someone fills in when using this component.
  `label` is a piece of text (string), `turns_left` is a number
  (integer). Both are required.
- `render` — The recipe. `type: inline` means a single line of text.
  `template` is the pattern, where `{label}` and `{turns_left}` get
  replaced with the actual values.
- `art` — A reference example of what the output looks like. This helps
  other designers understand the component at a glance.

### 3. Validate

Run this command to check your work:

```bash
askee-ds validate
```

If everything is correct, you'll see:

```
OK — 56 components validated, 0 errors.
```

If something is wrong — a missing field, a typo in the render type —
the validator tells you exactly what to fix.

### 4. Preview

See your component rendered with real data:

```bash
askee-ds preview cooldown.timer --props '{"label":"Fireball","turns_left":3}'
```

Output:

```
── cooldown.timer (ideated) ──
Fireball: 3 turns
```

That's it. You've created a component.

---

## Building a box component

Most game UI needs borders, headers, and structured content. That's
what the `box` render type is for. Let's build a loot notification.

```yaml
loot.drop:
  category: game/notifications
  description: Bordered notification when the player finds an item.
  status: ideated
  props:
    item_name:
      type: string
      required: true
    rarity:
      type: string
      required: false
  render:
    type: box
    width: 36
    border: single
    sections:
      - type: header
        text: "Loot found!"
      - type: divider
      - type: text
        text: "  {item_name}"
      - type: text
        text: "  Rarity: {rarity}"
  art: |2
    +----------------------------------+
    | Loot found!                      |
    +----------------------------------+
    |  Iron Sword                      |
    |  Rarity: common                  |
    +----------------------------------+
```

Breaking down the render spec:

- `type: box` — Draw a bordered rectangle.
- `width: 36` — The box is 36 characters wide.
- `border: single` — Use single-line borders (`+`, `-`, `|`). You can
  also use `heavy` or `double`.
- `sections` — The content inside the box, from top to bottom:
  - `header` — A bold title row. The system fills in `{item_name}` etc.
  - `divider` — A horizontal line across the box.
  - `text` — A single line of text. `{item_name}` gets replaced with
    the prop value.

### Available sections

Boxes can contain these section types:

| Section | What it does |
|---------|-------------|
| `header` | Title row at the top of a box. |
| `divider` | Horizontal line separator. |
| `text` | Single line of text (no wrapping). |
| `wrap` | Text that wraps to fit the box width. |
| `blank` | An empty row for spacing. |
| `list` | One row per item in an array prop. |
| `bars` | Resource bars (HP, mana) from an array. |
| `progress` | A single progress bar. |
| `numbered_list` | Items prefixed with 1. 2. 3. |
| `checked_list` | Items with [x] or [ ] checkboxes. |
| `active_list` | Items with a `>` marker on the selected one. |

For the full details on each section — what fields they accept and
examples — see [REFERENCE.md](REFERENCE.md).

---

## Adding interaction

Some components respond to keyboard input — buttons, menus, choice
lists. You declare this with an `interaction` block.

Here's a button that can receive keyboard focus and be pressed with
Enter or Space:

```yaml
button.confirm:
  category: core/buttons
  description: Confirmation button.
  status: ideated
  props:
    label:
      type: string
      required: true
  render:
    type: inline
    template: "[ {label} ]"
  interaction:
    focusable: true
    actions:
      - name: activate
        keys: [enter, space]
        description: Press the button
  art: |2
    [ OK ]
```

The `interaction` block says:

- `focusable: true` — This component can receive keyboard focus (it
  gets highlighted when the player tabs to it).
- `actions` — What keyboard actions the component supports. Each action
  has a `name`, a list of `keys` that trigger it, and a `description`.

For a navigable list (like a menu), you declare navigation actions:

```yaml
interaction:
  focusable: true
  actions:
    - name: select_next
      keys: [down]
      description: Move to next item
    - name: select_prev
      keys: [up]
      description: Move to previous item
    - name: confirm
      keys: [enter]
      description: Select the highlighted item
```

Available keys: `enter`, `space`, `escape`, `tab`, `up`, `down`,
`left`, `right`, `backspace`, `delete`, `home`, `end`, `page_up`,
`page_down`.

Display-only components (status bars, room cards, labels) do not need
an `interaction` block. If you leave it out, the component simply
cannot receive focus.

---

## Composing a screen

A screen combines multiple components into a full game view. You define
screens as YAML files under `screens/`. There are 17 example screens
under `screens/examples/` covering 6 gameplay contexts: title,
conversation, adventure play, open world, credits, and game menu.

Here's a text adventure screen with a status bar, a room card, and a
command input:

```yaml
name: adventure.main
description: Main text adventure screen.
layout: layout.stack
available_width: 50

slots:
  blocks:
    - component: status-bar.default
      props:
        hp_current: 85
        hp_max: 100
        location: The Undercroft
        turn_count: 12

    - component: room-card.default
      props:
        title: The Undercroft
        description_text: >-
          A low-ceilinged stone chamber. Water drips from the
          walls and the air smells of damp earth.
        items:
          - {id: rusty_key, label: rusty key}
          - {id: torch, label: torch (lit)}
        npcs:
          - {id: hooded_figure, label: hooded figure}
        exits:
          - {id: north, label: north}
          - {id: east, label: east}

    - component: command-input.default
      props:
        prompt: ">"
```

Breaking it down:

- `layout: layout.stack` — Stack the blocks vertically, one on top of
  another.
- `available_width: 50` — The screen is 50 characters wide.
- `slots.blocks` — A list of components to stack. Each entry has a
  `component` name and the `props` to fill in.

Save this as `screens/examples/my_screen.yaml` and render it:

```bash
askee-ds compose screens/examples/my_screen.yaml
```

You can also override the width:

```bash
askee-ds compose screens/examples/my_screen.yaml --width 80
```

### Nesting layouts

Slots can contain other layout components. For example, a two-column
layout inside a stack:

```yaml
slots:
  blocks:
    - component: status-bar.default
      props: { ... }

    - component: layout.two-column
      slots:
        left:
          component: narrative-log.pane
          props: { ... }
        right:
          component: entity-list.room
          props: { ... }
```

You can also use plain text in a slot:

```yaml
slots:
  blocks:
    - text: "> "
```

---

## Sizing for different terminals

Components can have a fixed width or adapt to the available space.

**Fixed width** — The component is always exactly this wide:

```yaml
render:
  type: box
  width: 44
```

**Adaptive width** — The component expands to fill the available space:

```yaml
render:
  type: box
  width: fill
```

**Adaptive with constraints** — Fill the space, but never narrower than
30 or wider than 60:

```yaml
render:
  type: box
  width: fill
  min_width: 30
  max_width: 60
```

**Content-sized** — Size to the content inside:

```yaml
render:
  type: box
  width: content
```

Height works the same way: `height: fill`, `height: content`, or a
fixed integer, with optional `min_height` and `max_height`.

Eight components now use `width: fill` with `min_width`/`max_width`
constraints: `status-bar.default`, `room-card.default`,
`narrative-log.pane`, `entity-list.room`, `modal.overlay`,
`character-sheet.compact`, `menu.main`, and `card.simple`. Most other
components use a fixed width. As you design new components, think
about whether they should grow and shrink — status bars and log panes
usually should, while notifications and tooltips usually should not.

---

## Color roles

AskeeDS has 10 color roles. Each one carries a mood or meaning. When
you set a color role on a component, the system applies the right
colors for borders, text, and accents.

| Role | When to use it |
|------|---------------|
| `neutral` | Default. No strong mood. |
| `danger` | Threats, errors, death, damage. |
| `success` | Victory, confirmation, healing. |
| `arcane` | Magic, rare systems, enchantment. |
| `nature` | Outdoors, growth, safe zones. |
| `frost` | Cold, water, technology. |
| `rare` | Rare items, quality indicators. |
| `legendary` | Legendary, premium, epic. |
| `dungeon` | Dark interiors, underground, stone. |
| `forest` | Forest zones, green-brown tones. |

Set a default color role in your component:

```yaml
default_color_role: danger
```

The engine or player can override this at runtime by passing a
`color_role` prop.

---

## Component lifecycle

Every component starts as `ideated` and earns its way to `approved`.
Here are all the statuses:

| Status | What it means |
|--------|--------------|
| `ideated` | New idea. The design may change. |
| `to-do` | The design intent is confirmed. Implementation is planned. |
| `in-progress` | Actively being designed or refined. |
| `in-review` | Ready for someone to review. |
| `approved` | Proven, stable, and ready for use. |
| `deprecated` | Being replaced. Will be removed in a future version. |
| `cancelled` | Abandoned. Kept for reference only. |

### What does "approved" require?

A component can be promoted to `approved` when it meets all of these:

1. **It renders correctly.** The output matches the reference art.
2. **It has tests.** At least one test exercises the component.
3. **Its props are validated.** All required props are typed. Schema
   validation passes.
4. **It serves a real game genre.** Text adventure, low-fi RPG,
   procedural RPG, or open-world ASCII.
5. **It's not redundant.** No other approved component does the same
   thing.
6. **It has an interaction spec** (if it's interactive). Focusable
   components must declare their keyboard actions.

---

## Where to go from here

- **Look up a specific field, section, or render type** —
  [REFERENCE.md](REFERENCE.md) has the complete lookup tables.
- **Wire AskeeDS into a game engine or Python app** —
  [INTEGRATING.md](INTEGRATING.md) covers the Python API and adapters.
- **Browse existing components** — Run `askee-ds list` to see all 56
  components, or `askee-ds list --status approved` for the 24 approved
  ones.
- **See everything rendered at once** — Run
  `python examples/all_components.py` for a visual catalog.
