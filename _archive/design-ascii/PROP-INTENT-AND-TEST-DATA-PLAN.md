# Prop intent and test-data plan

This plan aligns **component intent**, **prop shapes/types**, and **dummy content** (defaults + randomization) used by the component visual test and any future tooling. The goal is for every component to have sensible, intent-preserving test data so the TUI preview behaves correctly and stays understandable.

---

## 1. Current state (summary)

### 1.1 Where intent and shape live today

- **`design/ascii/components.txt`**
  - **␟ props:** Comma-separated list (e.g. `name, stats[], color_role_optional`). Parsed by `askee_ds.components.parse_props_meta()` → `name`, `optional`, `is_array`. **No scalar type (string vs int) or array-element shape.**
  - **PROP SHAPES (lines 80–113):** Human-readable contracts for many components (e.g. `stats: { label, value }[] or { label, current, max }[]`). **Not machine-parsed**; tools infer shapes from prop names or hardcoded branches.

### 1.2 Visual test tool (`tools/component_visual_test.py`)

- **default_props_for_component(name, parsed_props)**  
  Builds initial prop values. Uses **prop name** (and sometimes name patterns like `"segment"`, `"exit"`) to choose shapes. Has explicit branches for: exits/directions, **stats**, needs, segments, objectives, lines, interactions, nodes, relations, abilities, blocks, items/options/entity/npcs/hints; else generic `{ id, label }` or scalar defaults.

- **randomize_props_for_component(name, parsed_props)**  
  Same idea: name-based branches for exits, segments, objectives, lines, interactions, nodes, relations, abilities, needs (panel), etc. **No branch for `stats`** (and possibly others), so they fall into the generic array branch → `{ id, label }` only, which breaks components that expect `{ label, current, max }` or other shapes.

- **apply_props_to_art(component_name, art, props, parsed_props)**  
  **Explicit branches** for ~35 components; they **rebuild** the preview from props (correct). The rest use a **generic path**: substitute default-value strings found in the reference art with current prop values. Generic path skips dicts and JSON-like strings; it only substitutes simple values that appear in the art. So components without an explicit branch often show no visible change on randomize, or wrong layout if the randomizer produced a different shape.

### 1.3 Gap

- **Intent** is in PROP SHAPES (prose) and in the **apply_props_to_art** branches (code).
- **Defaults and randomizer** use a separate, **incomplete** set of name-based rules. When a prop’s shape isn’t recognized (e.g. `stats`), the randomizer emits the wrong shape → preview breaks or looks like “dummy content.”
- **Scalar types** (integer vs string) are not specified anywhere machine-readable, so the randomizer can’t reliably choose e.g. `50` vs `"50"` or avoid putting words into numeric fields.

---

## 2. Goals

1. **Single source of truth for “what this prop is”**  
   So that default props, randomizer, and (optionally) validation all agree on shape and type.

2. **Intent-preserving dummy content**  
   Default and randomized values should preserve the component’s structure (e.g. character-sheet bars, breadcrumb path, menu items) and look like plausible content, not generic “Option 1” / “Submit” where they don’t fit.

3. **Clearer prop definitions**  
   Where useful, make it explicit when a prop is integer-only, string-only, or a specific object shape (e.g. `{ label, current, max }`), so tooling and implementers can rely on it.

4. **Process that involves you**  
   For ambiguous or under-specified components, the plan includes a **“ask the designer”** step so intent is captured correctly before we lock in shapes and test data.

---

## 3. Option A vs B: Where to define shape/type

| Approach | Pros | Cons |
|----------|------|------|
| **A. Extend components.txt meta** (e.g. ␟ shape: or ␟ prop-types:) | Single file; visible next to art and description. | Parsers and docs need updating; format must stay simple. |
| **B. Data file consumed by the tool** (e.g. `design/ascii/prop_shapes.yaml` or `.json`) | Machine-friendly; no parser change to components.txt. | Two places to keep in sync (components.txt props list + shape file). |

**Recommendation:** Start with **B** for tooling (defaults + randomizer) so we can move fast and not change the component file format immediately. Optionally later, add a **␟ shape:** (or similar) line per component in components.txt that **references** the same shapes (e.g. by component name), so the design file stays the single place people look; the tool can still read from the data file keyed by component name.

---

## 4. Proposed shape/type schema (for the data file or future meta)

Minimal schema that the visual test (and possible validators) can use:

- **Scalar prop:** `type: string | integer | number` (optional; default `string`).
- **Array prop:** `element_shape: "id_label" | "label_current_max" | "label_value" | "label_turns_left" | "exits" | "nodes" | "relations" | "objectives" | "lines" | "blocks" | ...`  
  So the tool knows to generate e.g. `{ label, current, max }` for `stats` / `needs`, and `{ id, label }` for `segments` / `options` / `items`.

We can start with a fixed set of **element_shape** tokens that match PROP SHAPES and the existing apply_props_to_art branches, and extend as we add components.

Optional: **value_hints** (e.g. “hero names”, “stat names”, “place names”) so the randomizer can pick from a curated list instead of generic words.

---

## 5. Phased plan

### Phase 1 — Inventory and document (no code change yet)

1. **List every component** that the visual test can open (from manifest or from components.txt), with:
   - **Props** (from ␟ props: via parse_props_meta).
   - **Documented shape** (from PROP SHAPES if present).
   - **Visual test behavior:** Has explicit `apply_props_to_art` branch? (Y/N). Uses default_props branch? Randomizer branch? (e.g. “stats → generic array”).
   - **Gap:** “Wrong shape on randomize”, “no visible change”, “wrong type (string vs int)”, etc.

2. **Produce a table or checklist** (e.g. in this file or a spreadsheet): one row per component, columns as above, plus “Needs designer input?” (Y/N).

3. **Designer pass:** For each component marked “Needs designer input?”, we (you and the agent) answer:
   - What should default look like? (e.g. “Hero”, “HP/Mana/Status”, “50/100, 30/60, Cautious”).
   - What should “randomized” look like? (e.g. “Random hero name, random stat names from [HP, Mana, Stamina, Energy, …], random current/max, bars proportional”).
   - Any prop that must be integer-only or string-only?

Output: **Component × prop intent** (and, where needed, scalar type and value hints) written down so the next phase can implement against it.

### Phase 2 — Align defaults and randomizer with intent

1. **Add a small “prop intent” data source** (e.g. `design/ascii/prop_shapes.yaml` or a Python dict in the tool keyed by component and prop). For each component (or each prop that needs it):
   - Specify **array element_shape** (and optionally scalar type and value_hints) from Phase 1.

2. **Refactor default_props_for_component** to:
   - Prefer the intent data when present (e.g. “for this component, `stats` → label_current_max”).
   - Keep existing behavior where intent isn’t specified (backward compatible).

3. **Refactor randomize_props_for_component** to:
   - Use the same intent data so every array prop gets the **right shape** (e.g. `stats` → `{ label, current, max }` with sensible ranges).
   - Use scalar type so e.g. `hp_current` stays integer.
   - Optionally use value_hints for “hero name”, “stat label”, “place name”, etc.

4. **Add missing branches** only where the generic path can’t work (e.g. a new element_shape that the generic randomizer doesn’t handle). Prefer one “stats” branch, one “needs” branch, etc., driven by the data file, rather than one-off branches per component name.

5. **Test:** Run the visual test for every (or key) components; default and Z (randomize) must preserve structure and look sensible.

**Phase 2 status:** Implemented. `prop_shapes.yaml` exists; `default_props_for_component` and `randomize_props_for_component` use `_get_array_shape()` so `stats` and `needs` (and any future prop with `label_current_max` in the YAML) get the right shape. Defaults for that shape come from `_default_label_current_max(prop_name)`; randomizer uses `_randomize_label_current_max(prop_name)`. Scalar `name` uses hero-style names when randomized.

### Phase 3 — (Optional) Clarify prop definitions in components.txt

1. If we want **implementers** to see types in the design file:
   - Add a **␟ shape:** line per component (or a short **PROP SHAPES** subsection per component) that states array shapes and, if needed, “hp_current: integer”, “message: string”.
   - Keep wording consistent with PROP SHAPES and with the tool’s element_shape names so the data file and the design file stay aligned.

2. If we introduce **␟ prop-types:** or similar in the future, the same schema (string/integer, element_shape) can be used there.

---

## 6. “Ask the designer” checklist (Phase 1)

Use this when a component is under-specified or the current dummy data clearly doesn’t match intent. For each such component, answer:

1. **What is this component for?** (One sentence.)
2. **Default view:** What should the reference + default props show? (e.g. “Hero, HP 85/100, Mana 20/50, with bars half-full and 20/50.”)
3. **Randomized view:** What should “Z” change? (e.g. “Name, stat labels, current/max numbers, and bar fill; maybe one value-only row like Status.”)
4. **Prop-by-prop:** For each prop, is it string, integer, or something else? For arrays, what fields must each element have? (e.g. stats: `label` + either `value` or `current`+`max`.)
5. **Edge cases:** Empty list? Zero max? Very long labels? (Optional; we can use sensible fallbacks if you prefer.)

I can draft a **first-pass inventory** (Phase 1 list of components, props, current behavior, and “Needs designer input?”) next, and then we can go through the checklist only for the ones that need it. After that, we implement Phase 2 (and optionally Phase 3) without changing anything outside this plan’s scope.

---

## 7. Out of scope (for this plan)

- Changing **apply_props_to_art** logic beyond what’s needed to support the new shapes (e.g. if we add a component that needs a new branch, we add it; we don’t refactor the whole function).
- Adding new components or new props; this plan only aligns **existing** components and their test data.
- Persisting or validating prop types at runtime in games/TUIs; this is about **design-time and tooling** (visual test, possibly validators).

---

## 8. Phase 1 inventory (first pass)

Below: components that appear in the library with **␟ props:**, and how the visual test currently treats them. “Apply branch” = explicit `apply_props_to_art` branch; “Default” / “Random” = has a dedicated branch in default_props / randomize_props for that prop or pattern. **Gap** = known issue. **Ask?** = recommend designer pass for intent/random behavior.

| Component | Props | Apply branch | Default / Random (array props) | Gap | Ask? |
|-----------|-------|--------------|--------------------------------|-----|------|
| breadcrumb.inline | segments[] | Y | segments → id+label | — | N |
| button.icon | label, icon | Y | scalar defaults / generic | — | N |
| button.text | label | Y | scalar | — | N |
| card.simple | title, body_text | Y | scalar | — | N |
| character-sheet.compact | name, stats[] | Y | default + random: stats → label_current_max ✓ | — | N |
| choice-wheel.inline | options[] | Y | options → id+label | — | N |
| command-input.default | prompt, placeholder, hint_text | Y | scalar | — | N |
| cooldown.row | abilities[] (label, turns_left) | Y | abilit* → label+turns_left | — | N |
| counter.ammo | label, current, max | Y | scalar; current/max int | — | N |
| counter.score | label, value | Y | scalar | — | N |
| entity-list.room | items[], npcs[] | Y | item/entity/npcs → id+label | — | N |
| exit-list.inline | directions[] | Y | exit/direction → id+label | — | N |
| feedback.error | message, suggestion | Y | scalar | — | N |
| feedback.success | message | Y | scalar | — | N |
| form.single-field | label, placeholder, hint | Y | scalar | — | N |
| hint-bar.contextual | hints[] | Y | hint → id+label | — | N |
| hint-bar.interactions | interactions[] | Y | interaction → id+label | — | N |
| input.text | prompt, placeholder, max_length | Y | scalar; max_length int | — | N |
| inventory.list | items[] | Y | item → id+label (quantity in default) | — | N |
| label.inline | label, value | Y | scalar (value can be int) | — | N |
| menu.main | title, items[] | Y | item → id+label | — | N |
| menu.pause | title, items[] | Y | item → id+label | — | N |
| meter.resource | type, current, max | Y | scalar; current/max int | — | N |
| modal.overlay | title, body_text | Y | scalar | — | N |
| narrative-log.pane | lines[] | Y | lines → string[] | — | N |
| panel.survival-status | needs[] | Y | **needs** → label+current+max ✓ (random has branch) | — | N |
| progress-bar.horizontal | value, max, label_optional | Y | scalar; value/max int | — | N |
| room-card.default | title, description_text, exits[] | Y | exits ✓; scalar ✓ | — | N |
| status-bar.default | hp_current, hp_max, location_name, turn_count | Y | scalar; hp_* / turn int | — | N |
| status-bar.risk | + risk_level, luck_band_optional | Y | scalar | — | N |
| toast.inline | message, variant | Y | scalar | — | N |
| tooltip.default | text; optional variant (name, stats_dict) | Y | scalar + stats_dict | — | N |
| tracker.objective | objectives[] | Y | objective → id+label+checked | — | N |
| tree.compact | nodes[] | Y | node → id+label+children | — | N |
| tree.relationships | relations[] | Y | relation → id+label+items | — | N |
| typography.banner | text, style_hint, font_optional | Y | scalar | — | N |

**Components in manifest but not in table (no ␟ props in grep or no apply branch / generic only):**  
layout.app.shell, layout.two-column, layout.stack, table.fourcolumn, header.banner, nav.vertical, minimap.default, divider.horizontal, icon.placeholder, inventory.grid, spinner.loading, speech-bubble.left/right, decoration.placeholder, notification.*, screen.*, cooldown.badge, feedback.mixed, tracker.clock, tracker.front, quick-select.radial, panel.consequence.  
These either have no props, content-slots (pre-rendered strings), or use the **generic** apply path; they can be added to the inventory in a second pass once we decide how they should be tested.

**Summary:** Phase 2 is done: **character-sheet.compact** and **panel.survival-status** use `label_current_max` from prop_shapes.yaml for both defaults and randomizer. The table above reflects that; no rows need "Ask?" for the initial set. (The previous wrong-shape gap for stats was fixed.)

---

## 9. Designer pass (optional)

When you want to lock in intent or test data for more components, use the **"Ask the designer" checklist** (section 6) for any of these:

- **From "not in table":** header.banner (controls[]), nav.vertical (items[], active_id), inventory.grid (slots[], columns), layout.stack (blocks[]), minimap.default (grid[], legend_entries, player_position), spinner.loading (frames[]), screen.death (actions[]), quick-select.radial (options[], selected_id), panel.consequence (body_conditions[], mental_conditions[]), screen.crafting (inputs[], resource_costs[]).
- **From table, if you want different random behavior:** e.g. breadcrumb segments (place names), menu items (verb phrases), narrative lines (sentence style).

Answer the five checklist questions per component; then we can add or adjust defaults/randomizer and prop_shapes.yaml so the visual test stays aligned.

---

## 10. Next step

- **Done so far:** Phase 2 (prop_shapes.yaml, defaults + randomizer shape-driven for stats/needs, name to hero-style). Phase 3 (light): components.txt references prop_shapes.yaml; plan inventory updated; prop_shapes.yaml extended with controls, slots, frames, actions.
- **When you are ready:** Run the designer pass (section 9) for any component you care about, or add more components to the inventory and repeat.

---

## 11. Designer pass — full component list (4 chunks)

Work through each component using the checklist in section 6. Fill in your answers under each component. After **Chunk 1**, stop and tell the agent you are ready to continue; then Chunk 2 will be added or you continue in the doc. (Chunks 2–4 are listed below so you can do them in one sitting if you prefer.)

---

## Chunk 1 — Components 1–16

---

### `layout.app.shell`
**Props:** `color_role_optional`

**1. Purpose**
The app shell is the root-level layout container for the entire game UI. It acts as the structural skeleton that all other components live inside — defining the overall page chrome, background, and visual theme. In game engines like Unity or Godot, this is analogous to the root Canvas or the master scene node. In web-based game UIs (e.g. Twine, Bitsy, browser RPGs), it sets the viewport constraints, background color or texture, and font defaults.

**2. Default View**
Without a `color_role`, the shell renders with a neutral dark background (near-black), filling the full viewport. It creates a centered or full-bleed container that child components slot into. No visible elements of its own — purely structural. Typically renders as a `<div>` with `width: 100vw; height: 100vh; overflow: hidden`.

**3. Randomized View**
Changing `color_role` (e.g. "danger", "arcane", "nature") shifts the global palette — background color, border accent color, and text color all derive from the role. The layout itself (dimensions, flex direction) stays identical; only the visual theme changes. This allows a single shell to feel dramatically different across game zones or modes.

**4. Prop Types/Shapes**
- `color_role_optional`: `string | undefined` — A semantic theme token such as `"neutral"`, `"danger"`, `"arcane"`, `"nature"`, `"frost"`. Maps to a predefined color palette. If omitted, defaults to `"neutral"` or the system default theme.

**5. Edge Cases**
- No `color_role` provided → falls back to default theme without throwing.
- Unknown `color_role` string → should log a warning and fall back gracefully.
- Very small viewport (mobile, 320px wide) → must not overflow or clip child components.
- Used inside an iframe or embedded context → needs to respect parent container dimensions rather than `100vw/100vh`.

---

### `button.icon`
**Props:** `label`, `icon`, `color_role_optional`

**1. Purpose**
A compact, icon-first button used for game actions, toolbar controls, and HUD shortcuts (e.g. "Open Inventory", "Cast Spell", "Save Game"). Common in RPG action bars, strategy game control panels, and system menus. The label provides an accessible text name and may display as a tooltip or screen-reader-only text.

**2. Default View**
Renders as a square or near-square button with the icon centered inside it. The label is visually hidden (or shown on hover as a tooltip) to preserve compact layout. Default `color_role` produces a neutral/muted button; hover and active states provide visual feedback. Border radius and sizing should be consistent with the design system's base unit (e.g. 8px radius, 40×40px).

**3. Randomized View**
- Changing `icon` (e.g. a sword → a shield → a potion flask) changes the glyph rendered, but button dimensions stay fixed.
- Changing `color_role` (e.g. `"danger"` → red tint, `"success"` → green tint) recolors the button's background/border/icon tint.
- Changing `label` doesn't affect visual appearance unless a tooltip is shown, but updates accessible name.

**4. Prop Types/Shapes**
- `label`: `string` — Short human-readable action name, e.g. `"Attack"`, `"Open Map"`, `"Drink Potion"`. Used for accessibility and tooltip.
- `icon`: `string` — Icon identifier, e.g. a Unicode glyph (`"⚔"`, `"🗺"`), an icon library key (`"sword"`, `"map"`), or an image path (`"/icons/potion.svg"`).
- `color_role_optional`: `string | undefined` — Theme token as above.

**5. Edge Cases**
- Very long `label` string used in tooltip → must truncate or wrap gracefully.
- `icon` is an invalid path or unknown key → show a fallback placeholder glyph.
- Icon renders at very small sizes → must remain legible (minimum 16px target size for accessibility).
- `color_role` that maps to a very light color → ensure icon contrast ratio meets accessibility minimums.

---

### `tooltip.default`
**Props:** `text`; optional variant stats: `name`, `stats_dict`, `color_role_optional`

**1. Purpose**
Tooltips are contextual information overlays that appear on hover or focus. In games, they reveal item descriptions, stat breakdowns, ability costs, or lore entries. The stats variant (with `name` + `stats_dict`) is specifically for game items or characters — showing a mini stat sheet without navigating away. Common in Diablo-style ARPGs, Civilization, and most card games (e.g. Hearthstone, Slay the Spire).

**2. Default View**
The default (text-only) variant renders as a small floating panel near the hovered element, containing a single line or short paragraph of descriptive text. It should appear with a short delay (~300ms) and disappear when the cursor moves away. Default styling: dark background, light text, subtle border or shadow, 12–14px font.

The stats variant shows a header with `name` (item/character name), followed by a key-value breakdown from `stats_dict` (e.g. "ATK: 12", "DEF: 5", "Weight: 2kg"). This variant is taller and may include a divider between name and stats.

**3. Randomized View**
- Swapping `text` changes only the content. Layout stays identical.
- Populating `stats_dict` with many entries (10+) forces the tooltip to scroll or expand — its width should remain capped.
- Changing `color_role` recolors the tooltip panel to match a theme (e.g. `"rare"` = blue, `"legendary"` = gold), a pattern from games like World of Warcraft item quality coloring.

**4. Prop Types/Shapes**
- `text`: `string` — Descriptive prose, e.g. `"A rusted blade, worn by time but still sharp enough to cut."` Can be 1–3 sentences.
- `name`: `string | undefined` — Entity name for stats variant, e.g. `"Iron Sword"`, `"Guard Captain"`.
- `stats_dict`: `Record<string, string | number> | undefined` — Key-value pairs, e.g. `{ "ATK": 12, "Weight": "2.4kg", "Rarity": "Common" }`.
- `color_role_optional`: `string | undefined` — Theme token.

**5. Edge Cases**
- `text` is very long (paragraph) → needs max-width and text wrapping; avoid overflow.
- `stats_dict` is empty `{}` → stats variant should hide the stats section or fall back to text-only display.
- Tooltip positioned near edge of viewport → must flip direction (above/below, left/right) to stay in view.
- Touch devices have no "hover" state → tooltip should appear on tap/focus and dismiss on second tap.
- `text` and `stats_dict` both provided → clarify which takes visual priority.

---

### `table.fourcolumn`
**Props:** `label`, `content`, `color_role_optional`

**1. Purpose**
A four-column data table for presenting structured game data — loot tables, skill comparisons, leaderboard entries, equipment stats, quest logs, or bestiary entries. The rigid four-column layout suits data that naturally fits a left-aligned label + 3 data columns pattern, such as "Stat / Base / Modified / Max" or "Item / Weight / Value / Count".

**2. Default View**
Renders as a bordered table with a header row (derived from `label`) and data rows from `content`. Alternating row shading (zebra stripes) aids readability. Column widths distribute evenly unless overridden. The `label` appears as a table caption or header area above the grid.

**3. Randomized View**
- More rows in `content` → table grows vertically; scrollable if exceeding a container height.
- More columns used differently (sparse data, empty cells) → cells show an em dash or "—" for missing values.
- `color_role` changes header and border colors — e.g. `"arcane"` might give a purple header row.

**4. Prop Types/Shapes**
- `label`: `string` — Table title/caption, e.g. `"Item Comparison"`, `"Skill Tree Stats"`.
- `content`: `Array<[string, string, string, string]>` or `Array<Record<string, string>>` — Array of row data, each with exactly 4 values. Could also be structured as `{ headers: string[], rows: string[][] }`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Fewer than 4 values in a row → pad with empty strings or "—".
- Cell content is very long text → truncate with ellipsis or allow wrapping.
- Zero rows in `content` → show an empty state message ("No data available").
- Non-string values (numbers, booleans) → should coerce to string for display.
- Very narrow viewport → consider collapsing to a card-per-row layout on mobile.

---

### `status-bar.default`
**Props:** `hp_current`, `hp_max`, `location_name`, `turn_count`, `color_role_optional`

**1. Purpose**
The core game HUD status bar — a persistent top or bottom bar showing the player's current health, their location, and the current turn number. This is a fundamental UI pattern found in virtually every RPG, roguelike, and strategy game (Nethack, XCOM, Stardew Valley, Darkest Dungeon). It gives the player at-a-glance situational awareness without navigating menus.

**2. Default View**
A horizontal bar divided into regions: a health indicator on the left (typically showing `hp_current / hp_max` as both a number and a colored fill bar), the `location_name` centered, and `turn_count` on the right. The HP bar fills proportionally — green at full health, transitioning to yellow then red as HP drops.

**3. Randomized View**
- `hp_current` changing from 100 to 3 → bar shrinks and color shifts from green to critical red.
- `location_name` switching between short ("Cave") and long ("The Ancient Sunken Vault of Malachar") → long names must truncate with ellipsis.
- `turn_count` incrementing → counter updates cleanly; at large numbers (9999+) check for layout overflow.
- `color_role` → changes accent color of the bar's border/background, not the HP fill color (which is semantic).

**4. Prop Types/Shapes**
- `hp_current`: `number` (non-negative integer) — Current hit points. E.g. `45`.
- `hp_max`: `number` (positive integer) — Maximum hit points. E.g. `100`.
- `location_name`: `string` — Current room or zone name. E.g. `"Goblin Warren"`, `"Floor 3 — East Corridor"`.
- `turn_count`: `number` (non-negative integer) — Current game turn. E.g. `142`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `hp_current > hp_max` (e.g. buffed/overheal) → bar should cap at full or show overflow indicator.
- `hp_current = 0` → bar is empty; consider triggering a "death" visual state.
- `hp_max = 0` → guard against division-by-zero in percentage calculation.
- Extremely long `location_name` → truncate or scroll.
- `turn_count` overflows display space → abbreviate (e.g. "9.9k+").

---

### `status-bar.risk`
**Props:** `hp_current`, `hp_max`, `location_name`, `turn_count`, `risk_level`, `luck_band_optional`, `color_role_optional`

**1. Purpose**
An extended status bar for games with explicit risk/danger mechanics — survival games, horror roguelikes, games like Darkest Dungeon or Hades where a "danger level" or "heat" meter is tracked alongside health. The `risk_level` communicates ambient threat to the player; `luck_band` is used in probability-heavy systems (tabletop adaptations, dice-based games) to show the player's current fortune range.

**2. Default View**
Extends `status-bar.default` with two additional indicators: a `risk_level` badge or meter (e.g. LOW / MEDIUM / HIGH / CRITICAL, or a numeric 1–5 scale) displayed in a color-coded manner (green → amber → red), and an optional `luck_band` display (e.g. "Luck: Favored" or a small dial/range indicator). Risk level might pulse or animate at HIGH/CRITICAL.

**3. Randomized View**
- `risk_level` moving from LOW → CRITICAL → the badge changes color and may animate (pulse, shake).
- `luck_band` cycling through negative/neutral/positive → changes text and a subtle color indicator.
- All `status-bar.default` randomization behavior applies.

**4. Prop Types/Shapes**
- All props from `status-bar.default` (same types).
- `risk_level`: `string | number` — Semantic level string (`"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`) or a numeric score (1–5). Maps to a display color.
- `luck_band_optional`: `string | undefined` — Descriptive luck label, e.g. `"Cursed"`, `"Neutral"`, `"Blessed"`, `"Lucky"`. Or a numeric range string like `"-2 to +1"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Unknown `risk_level` string → fallback to neutral/gray display; don't crash.
- `luck_band` omitted entirely → section is hidden cleanly without leaving empty space.
- `risk_level = CRITICAL` + `hp_current` near 0 → both indicators in danger states simultaneously; must remain visually readable without clashing.
- Localization: `risk_level` strings may need translation keys rather than raw English strings.

---

### `room-card.default`
**Props:** `title`, `description_text`, `entity_list[]`, `exits[]`, `color_role_optional`

**1. Purpose**
The central content card for a location in a text adventure, roguelike, or narrative RPG. It presents the current room or scene: its name, a prose description, the entities present (items and NPCs), and the available exits. Common in Zork-style text adventures, modern interpretations like Inkle's games, and dungeon crawlers like Caves of Qud. This is often the largest single element on screen during exploration.

**2. Default View**
A card-shaped panel with:
- `title` as a bold header (e.g. "The Merchant's Cellar")
- `description_text` as a prose paragraph below the title
- An `entity_list` section showing interactable items/NPCs (can use the `entity-list.room` component)
- An `exits` section listing available directions (can use the `exit-list.inline` component)
The card has a border, padding, and a subtle background differentiated from the app shell.

**3. Randomized View**
- Long `description_text` → card grows vertically or scrolls; overflow should be handled.
- Empty `entity_list` → "Nothing of interest here." or the section is omitted.
- Empty `exits` → "No exits visible." or a locked/dead-end indicator.
- `color_role` changing → border color and header background shift to match the zone theme (e.g. `"dungeon"` = dark stone, `"forest"` = green tones).

**4. Prop Types/Shapes**
- `title`: `string` — Room/location name, e.g. `"Crumbling Guard Post"`, `"Town Square"`.
- `description_text`: `string` — 1–4 sentence atmospheric prose, e.g. `"Moss clings to the stone walls. A torch flickers in the corner, casting long shadows."`.
- `entity_list`: `Array<{ id: string, name: string, type: "item" | "npc" }>` — Entities present in the room.
- `exits`: `Array<{ direction: string, destination_name?: string }>` — Available exits, e.g. `[{ direction: "north", destination_name: "Dark Corridor" }, { direction: "east" }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `description_text` is empty string → show a fallback ("The room is unremarkable.") rather than an empty card body.
- `entity_list` has duplicate entries (same item appears twice) → deduplicate or display quantity.
- `exits` contains non-standard directions (e.g. `"up"`, `"down"`, `"in"`) → must render without breaking layout.
- Very long room `title` → truncate with ellipsis or allow wrapping.

---

### `entity-list.room`
**Props:** `items[]`, `npcs[]`, `color_role_optional`

**1. Purpose**
A sub-component (often used inside `room-card.default`) that displays all interactable entities in the current location — both items (objects the player can pick up, use, or inspect) and NPCs (characters the player can talk to, trade with, or fight). Equivalent to the "you can see" section of a text adventure's room description, or the entity overlay in a top-down RPG.

**2. Default View**
Two subsections rendered sequentially: Items (labeled "You see:" or "Items:") and NPCs (labeled "People:" or "Characters:"). Each is a simple list. Items show their name and possibly a brief descriptor; NPCs show their name and status (e.g. hostile/neutral/friendly) via an icon or color badge. If one list is empty, that section is omitted.

**3. Randomized View**
- Empty `items[]` + populated `npcs[]` → only the NPC section renders.
- 10+ items → list wraps or scrolls; consider a "…and 4 more" overflow pattern.
- NPC with `type: "hostile"` → name displays in red or with a threat icon.
- `color_role` changes accent/label colors but not the individual entity status colors (those are semantic).

**4. Prop Types/Shapes**
- `items`: `Array<{ id: string, name: string, quantity?: number, description?: string }>` — E.g. `[{ id: "item_001", name: "Rusty Key", quantity: 1 }]`.
- `npcs`: `Array<{ id: string, name: string, disposition: "friendly" | "neutral" | "hostile", status?: string }>` — E.g. `[{ id: "npc_guard", name: "Town Guard", disposition: "neutral" }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Both `items` and `npcs` are empty → render a single "Nothing here." message.
- `quantity` of 0 for an item → should not render that item (or show "0 × Rusty Key" as a stale state warning).
- NPC with an unknown `disposition` value → default to neutral styling.
- Very long entity names → truncate with ellipsis.

---

### `exit-list.inline`
**Props:** `directions[]`, `color_role_optional`

**1. Purpose**
Displays the available exits or navigation directions from the current room or location. A staple of text adventures and dungeon crawlers — the "Obvious exits: North, East, Down" line in Zork. In graphical games it could manifest as directional indicators on a HUD compass. Helps players understand navigational options without needing to consult a map.

**2. Default View**
A compact inline or wrapped list of direction labels, typically prefixed with "Exits:" or "You can go:". Each direction is styled as a clickable chip or badge. Standard compass directions (N, S, E, W, NE, NW, SE, SW) may use abbreviations; non-cardinal directions ("up", "down", "in", "out") render as-is. Default styling: muted bordered badges in a flex row.

**3. Randomized View**
- Single exit → renders as "Exit: North" (singular label).
- Six or more exits → wraps to a second line; layout must not overflow its container.
- Blocked or locked exits → direction renders in gray/strikethrough with a lock icon.
- `color_role` → badge background/border colors change.

**4. Prop Types/Shapes**
- `directions`: `Array<{ direction: string, label?: string, blocked?: boolean }>` — E.g. `[{ direction: "north" }, { direction: "east", label: "Market District" }, { direction: "down", blocked: true }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `directions` is empty → render "No exits." or hide entirely.
- Duplicate direction entries (two "north" entries) → deduplicate or show warning.
- Very long `label` on a direction → truncate within badge.
- All exits `blocked: true` → component renders but communicates the player is locked in (important narrative signal).

---

### `minimap.default`
**Props:** `grid[]`, `legend_entries`, `player_position`, `color_role_optional`

**1. Purpose**
A top-down grid minimap showing the explored layout of the current dungeon, level, or world area. Fundamental to dungeon crawlers (Diablo, Nethack, Pokémon), strategy games, and metroidvanias. Gives the player spatial awareness and helps track exploration progress. The grid stores tile data (room types, connections, obstacles), and the player's current position is highlighted.

**2. Default View**
A small, fixed-size grid rendered as a matrix of colored cells. Unexplored cells are dark/invisible; explored cells show their room type via color or symbol (from `legend_entries`). The player's cell is highlighted distinctly (bright dot, cursor icon, or pulsing indicator). A legend may appear below or beside the grid matching symbols/colors to room types. Default size: approximately 10×10 to 20×20 cells.

**3. Randomized View**
- Player moves to a different cell → the highlighted position shifts; camera may pan if the map is larger than the viewport.
- New rooms explored → previously dark cells reveal their type.
- Dense grid (30×30) → minimap must scale cells down to fit; very small cells may reduce to 1–2px squares.
- `color_role` → changes the map's border/background but not the semantic tile colors (those come from `legend_entries`).

**4. Prop Types/Shapes**
- `grid`: `Array<Array<{ type: string, explored: boolean, passable: boolean }>>` — 2D array of tile data. `type` maps to a color/symbol via `legend_entries`. E.g. `{ type: "room", explored: true, passable: true }`.
- `legend_entries`: `Record<string, { color: string, symbol?: string, label: string }>` — Mapping of tile types to display info. E.g. `{ room: { color: "#aaa", label: "Room" }, corridor: { color: "#666", label: "Corridor" }, boss: { color: "#f00", label: "Boss Room" } }`.
- `player_position`: `{ x: number, y: number }` — Grid coordinates of the player.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `player_position` outside grid bounds → clamp to nearest edge; do not crash.
- Empty `grid` (0×0) → render an empty bordered box with "Map unavailable."
- Tile type not in `legend_entries` → render as gray/unknown.
- Very large grids (100×100) → consider virtual rendering or fixed zoom window.
- Accessibility: minimap is inherently visual; provide an accessible text summary of nearby exits.

---

### `command-input.default`
**Props:** `prompt`, `placeholder`, `hint_text`, `color_role_optional`

**1. Purpose**
The primary text input for command-driven games — text adventures, interactive fiction, classic MUDs, and hybrid parser games. The player types commands here (e.g. "go north", "take key", "talk to guard"). The `prompt` establishes the input prefix (e.g. `>`), `placeholder` shows an example command when empty, and `hint_text` provides contextual guidance.

**2. Default View**
A single-line text input with a left-side prompt prefix (e.g. `> `) and a blinking cursor. `placeholder` text is shown in muted styling when no input is present (e.g. "Type a command…"). `hint_text` appears below the input as a small helper label (e.g. "Try: look, go north, take sword"). On submit (Enter key), the input clears and the command is dispatched.

**3. Randomized View**
- Changing `prompt` from `">"` to `"$ "` or `"[INPUT] >"` → prefix renders differently but input behavior is unchanged.
- Different `placeholder` values → the empty-state text changes.
- Different `hint_text` → the helper text below updates (useful for context-sensitive guidance).
- `color_role` → border/background of the input and prompt prefix shift to match the theme.

**4. Prop Types/Shapes**
- `prompt`: `string` — Short prefix string, e.g. `">"`, `"$ "`, `"CMD:"`. Typically 1–5 characters.
- `placeholder`: `string` — Input hint text, e.g. `"Enter a command…"`, `"What do you do?"`.
- `hint_text`: `string` — Contextual sub-label, e.g. `"Tip: type 'help' for a list of commands"`, `"You can: go [direction], take [item], talk to [person]"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Player pastes a very long command → input must handle it gracefully; consider a max character limit.
- Empty submission (press Enter with no input) → should not dispatch a command; may shake/flash the input.
- Input while a modal/menu is open → should be blocked (focus trap in modal takes priority).
- Special characters in input (`<`, `>`, `&`) → sanitize before display in narrative log.
- Mobile/touch devices → virtual keyboard appearing may resize viewport; layout must adapt.

---

### `hint-bar.contextual`
**Props:** `hints[]`, `color_role_optional`

**1. Purpose**
A persistent or semi-persistent bar that surfaces context-sensitive hints based on the player's current situation. Unlike a static tutorial, contextual hints react to the game state — showing relevant reminders when a player enters a new area, picks up an item, or encounters a new mechanic. Common in modern games that blend discoverability with player agency (e.g. Celeste, Hollow Knight loading tips, Stardew Valley season-start reminders).

**2. Default View**
A slim horizontal bar (typically at the bottom of the screen) cycling through or displaying 1–3 hint strings. Hints are shown in small, muted text to avoid distracting from the main game view. May include a small icon prefix (💡 or an "i" symbol). If multiple hints exist, they can rotate on a timer or be manually dismissed.

**3. Randomized View**
- Single hint → renders statically without rotation controls.
- 5+ hints → either rotates automatically or shows navigation arrows.
- Hints with action keywords (e.g. "Press [E] to interact") → keywords may be highlighted as key badges.
- `color_role` → bar background and text color shift to match theme.

**4. Prop Types/Shapes**
- `hints`: `Array<string>` — List of hint strings, e.g. `["Try examining items before picking them up.", "Doors to the east are often unlocked.", "Your torch will burn out after 50 turns."]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `hints` is empty → bar renders empty or hides entirely; avoid showing a blank bar.
- A single hint is very long (paragraph-length) → truncate or scroll within the bar.
- Hints contain formatting markup → either strip or support a safe subset of rich text.
- Rapid hint updates (many state changes) → prevent jarring rapid text swaps; debounce or queue.

---

### `hint-bar.interactions`
**Props:** `interactions[]`, `color_role_optional`

**1. Purpose**
Shows the available interactions the player can perform in the current context — a "what can I do here" reference bar. More specific than contextual hints: this lists actual current affordances (e.g. "[E] Talk", "[F] Fight", "[T] Take Item"). Common in action-RPGs (Skyrim's button prompts), visual novels (interaction menus), and immersive sims (Prey, Dishonored).

**2. Default View**
A row of interaction chips, each showing a key binding (or button prompt) plus an action label. E.g.: `[E] Examine` | `[T] Take` | `[F] Attack Guard`. Displayed in a compact horizontal bar. Key badges use distinct styling (rounded bordered box) to stand out from the action label text.

**3. Randomized View**
- More interactions (6+) → chips wrap or overflow into a scrollable row; consider a "+N more" overflow indicator.
- Fewer interactions (1) → single chip renders left-aligned.
- Interactions with long labels → labels truncate within their chip.
- `color_role` → chip background/border colors shift.
- Unavailable interactions (e.g. locked) → chips render grayed out.

**4. Prop Types/Shapes**
- `interactions`: `Array<{ key: string, label: string, available?: boolean }>` — E.g. `[{ key: "E", label: "Examine", available: true }, { key: "F", label: "Attack", available: false }]`. `key` is a short string: `"E"`, `"Space"`, `"LMB"`, `"△"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `interactions` is empty → hide the bar entirely rather than showing an empty row.
- Multiple interactions with the same key → flag as a conflict (warn in dev, gracefully display in prod).
- Controller vs. keyboard: `key` strings may need platform-conditional rendering (e.g. `"A"` vs `"⬤"`).
- Very long `label` text → truncate inside chip.

---

### `narrative-log.pane`
**Props:** `lines[]`, `max_visible`, `color_role_optional`

**1. Purpose**
The scrollable text log that records all narrative events, combat outcomes, dialogue excerpts, and system messages during a play session. A core component of roguelikes (Nethack, DCSS, Caves of Qud), text adventures, and MUDs. Players refer to the log to review what just happened, track combat details, or re-read missed dialogue. It is the primary "story so far" surface.

**2. Default View**
A vertically scrolling pane showing the most recent `max_visible` lines at the bottom (newest-last). Older lines are accessible by scrolling up. Each line may be plain text or richly typed (e.g. combat messages in red, loot messages in gold, system messages in gray). Auto-scrolls to the bottom on new entries. A subtle scrollbar appears when content overflows.

**3. Randomized View**
- Many lines (500+) → pane must virtualize or paginate to avoid DOM/memory issues.
- Lines with different semantic types → color coding applies per type.
- `max_visible = 3` → very compact log; most content hidden behind scroll.
- `max_visible = 50` → tall log, shows a lot of history.
- `color_role` → pane background and default text color shift.

**4. Prop Types/Shapes**
- `lines`: `Array<{ text: string, type?: "combat" | "loot" | "narrative" | "system" | "dialogue" | "error", timestamp?: number }>` — Each log entry. E.g. `{ text: "You strike the goblin for 8 damage.", type: "combat" }`.
- `max_visible`: `number` (positive integer) — Number of lines visible before scrolling. E.g. `10`, `20`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `lines[]` → show a placeholder ("The log is empty.") or simply a blank pane.
- A line is very long → wrap within the pane; don't overflow horizontally.
- Extremely rapid line additions (10/sec in fast combat) → batch DOM updates to prevent jank.
- `max_visible = 0` → guard against; default to a minimum (e.g. 3).
- Lines containing HTML/markdown → sanitize to prevent injection.

---

### `feedback.success`
**Props:** `message`, `color_role_optional`

**1. Purpose**
A transient or persistent success confirmation message shown after a positive player action — picking a lock, completing a quest, leveling up, or successfully crafting an item. Provides immediate positive reinforcement. Found in virtually all games as flashes, popups, or inline confirmations.

**2. Default View**
A small banner or inline message with a green accent (checkmark icon + message text). Appears near the action's context or in a fixed notification zone. Typically auto-dismisses after 2–3 seconds. Example: ✓ "You successfully picked the lock."

**3. Randomized View**
- Short message ("Done!") vs. long message ("You have completed the main quest and unlocked the true ending!") → layout stays consistent; long messages wrap or truncate.
- `color_role` → while success is semantically green, `color_role` may modify the surrounding chrome (border, background) for themed contexts.

**4. Prop Types/Shapes**
- `message`: `string` — Positive confirmation text, e.g. `"Item crafted successfully!"`, `"Quest complete: The Lost Relic"`, `"Level up! You are now level 5."`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `message` is empty → do not render; log a warning.
- Multiple success messages queued rapidly → stack or queue rather than overwrite.
- Message persists too long if auto-dismiss is implemented → must be dismissible manually too.

---

### `feedback.error`
**Props:** `message`, `suggestion`, `color_role_optional`

**1. Purpose**
A feedback component for invalid player inputs or failed game actions — trying to go through a locked door, entering an unrecognized command, attempting an action without required items. The `suggestion` prop makes this especially useful in parser/text-adventure contexts where guiding the player toward correct syntax is important (e.g. "Did you mean: 'go north'?").

**2. Default View**
A red-accented inline message with an error icon (✗ or ⚠). Shows `message` on the first line and `suggestion` in a muted secondary style below it. E.g.: ✗ "You can't go that way." / "Try: north, east, or down." Auto-dismisses or persists until the next action.

**3. Randomized View**
- No `suggestion` provided → renders only the `message` line; suggestion area is absent.
- Long `message` and `suggestion` both present → both wrap gracefully.
- `color_role` may modify the border chrome while keeping the error red/amber semantic coloring for the icon/text.

**4. Prop Types/Shapes**
- `message`: `string` — Error description, e.g. `"Unknown command: 'attac sword'"`, `"You don't have a key."`, `"That direction is blocked."`.
- `suggestion`: `string` — Corrective hint, e.g. `"Did you mean: 'attack sword'?"`, `"Find a key first."`, `"Available exits: north, south."`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `message` is empty → do not render; fall back silently.
- `suggestion` is empty string vs. undefined → both should result in suggestion area being hidden (distinguish between "no suggestion provided" and "empty suggestion").
- Rapid sequence of errors → queue or debounce; avoid error message spam.
- XSS risk if `message` is derived from player input → sanitize before rendering.

---

## Chunk 2 — Components 17–32

---

### `divider.horizontal`
**Props:** `(none or style)`, `color_role_optional`

**1. Purpose**
A simple horizontal line used to visually separate sections of UI — between a room card and the command input, between log entries of different types, or between sections of a menu or character sheet. Universal in all UI systems; in games it helps organize dense information panels.

**2. Default View**
A full-width horizontal rule with 1px height and a muted border color. May have vertical margin above and below. `style` might offer variants like `"solid"`, `"dashed"`, `"dotted"`, or `"ornamental"` (a styled fantasy divider for thematic UIs).

**3. Randomized View**
- `style = "dashed"` → dashed line.
- `style = "ornamental"` → decorative divider (e.g. `--- ✦ ---`).
- `color_role` → line color matches the theme accent color.

**4. Prop Types/Shapes**
- `style`: `"solid" | "dashed" | "dotted" | "ornamental" | undefined` — Visual style of the line.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Used inside a very narrow container → must span full container width, not overflow.
- `style` value not recognized → fallback to `"solid"`.
- Multiple dividers stacked → spacing between them should not double-compound margins.

---

### `input.text`
**Props:** `prompt`, `placeholder`, `max_length`, `color_role_optional`

**1. Purpose**
A general-purpose text input for non-command contexts — naming a character, entering a save file name, typing a chat message in a multiplayer game, or filling in a journal entry. Distinct from `command-input.default` in that it's for form-style data entry rather than game command parsing.

**2. Default View**
A bordered text field with the `prompt` label above or inline-left, `placeholder` ghost text when empty, and a character counter when near `max_length`. Submits on Enter or a linked button press. Standard focus ring on active state.

**3. Randomized View**
- `max_length = 8` (e.g. character name) → very short field with tight counter feedback.
- `max_length = 280` (e.g. journal entry) → taller or wider field; multiline support may be needed.
- `color_role` → border, focus ring, and label color shift.

**4. Prop Types/Shapes**
- `prompt`: `string` — Field label, e.g. `"Character Name"`, `"Enter your message"`, `"Save file name"`.
- `placeholder`: `string` — Ghost text, e.g. `"E.g. Aldric the Bold"`, `"Type here…"`.
- `max_length`: `number` (positive integer) — Hard character limit, e.g. `16`, `64`, `280`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Player exceeds `max_length` → input should prevent further characters and show a count warning.
- Player enters only whitespace → validate before allowing submission.
- Special characters or unicode (emoji, accented characters) → handle multibyte correctly in length counting.
- `max_length = 0` → guard against; treat as unconstrained or use a sensible default.

---

### `label.inline`
**Props:** `label`, `value`, `color_role_optional`

**1. Purpose**
A compact key-value display for showing a single stat, attribute, or piece of metadata inline. Used widely in character sheets, item panels, leaderboards, and settings screens — e.g. "Strength: 14", "Gold: 320", "Kills: 47". The fundamental atom of game data display.

**2. Default View**
A short horizontal pairing: `label` in muted/secondary text on the left, `value` in primary/bold text on the right (or immediately after a colon). No border; renders inline with surrounding content. Example: `STR  14` or `Gold: 320`.

**3. Randomized View**
- Long `label` and long `value` simultaneously → may need a minimum gap or wrapping rule.
- Numeric `value` changing rapidly (live combat stats) → value updates in place; no layout shift.
- `color_role` → `label` and/or `value` text colors shift.

**4. Prop Types/Shapes**
- `label`: `string` — Attribute name, e.g. `"Strength"`, `"STR"`, `"Gold"`, `"Kills"`.
- `value`: `string | number` — Attribute value, e.g. `14`, `"320 GP"`, `"Lawful Good"`, `true`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `value` is `null` or `undefined` → display `"—"` or `"N/A"` rather than blank.
- Very large numbers → format with commas or abbreviate (`1,200,000` → `1.2M`).
- `label` is empty → render value-only or hide entirely.

---

### `icon.placeholder`
**Props:** `symbol`, `alt_text`, `color_role_optional`

**1. Purpose**
A flexible icon component for displaying symbols, glyphs, or placeholder imagery when full sprite/image assets are unavailable — common during prototyping, in text-mode games, or in systems using Unicode/emoji as lightweight icons. Also used as a fallback when an image fails to load.

**2. Default View**
A fixed-size box (e.g. 24×24px or 32×32px) containing the `symbol` character or glyph, centered with appropriate font sizing. Has a subtle background or border to give it a "badge" appearance. `alt_text` is used as the accessible `aria-label`.

**3. Randomized View**
- Different `symbol` values → e.g. `"⚔"`, `"🛡"`, `"💀"`, `"★"` — only the glyph changes; container size is constant.
- `color_role` → background and glyph color shift.

**4. Prop Types/Shapes**
- `symbol`: `string` — A single Unicode character, emoji, or short text glyph. E.g. `"⚔"`, `"🧪"`, `"?"`, `"★"`. Should be 1–2 visible characters.
- `alt_text`: `string` — Accessible description, e.g. `"Sword"`, `"Potion"`, `"Unknown item"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Multi-character `symbol` → render the first character only, or scale down font size.
- Symbol is an emoji that renders differently across OS/platforms → accept visual inconsistency or use SVG icons instead.
- Symbol has zero visible width → show a fallback `"?"`.

---

### `button.text`
**Props:** `label`, `color_role_optional`

**1. Purpose**
A simple text-only button for low-emphasis actions — "Cancel", "Back", "Skip", "More Info". Used where an icon button would be too ambiguous and a full styled button too heavy. Common in menus, dialog dismissals, and secondary actions.

**2. Default View**
Plain text styled as a clickable element — underline or color shift on hover, visible focus ring for keyboard navigation. No border or background by default (or a very subtle one). Padding ensures adequate click target size (minimum 44px tall for accessibility).

**3. Randomized View**
- Short label ("OK") vs. long label ("View Full Character History") → button width scales to content.
- `color_role` → text color and hover state match the theme.

**4. Prop Types/Shapes**
- `label`: `string` — Button text, e.g. `"Cancel"`, `"Continue"`, `"View Map"`, `"Skip Tutorial"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `label` → do not render; invisible button is a trap for keyboard users.
- Very long `label` → wrap or constrain within max-width.
- Multiple `button.text` components side by side → ensure sufficient spacing between click targets.

---

### `breadcrumb.inline`
**Props:** `segments[]`, `color_role_optional`

**1. Purpose**
Shows the player's navigation path through a hierarchical menu or game world — e.g. "World Map > Dungeon > Floor 3 > Room 4" or "Main Menu > Settings > Audio". Common in games with nested menus, complex inventories, or world maps with drill-down navigation. Helps players understand where they are and navigate back.

**2. Default View**
A horizontal row of segment labels separated by a divider character (`>`, `/`, or `›`). The last segment (current location) is displayed in full/bold as the active item; preceding segments are muted and clickable (if navigation is supported). Renders compactly on a single line.

**3. Randomized View**
- Single segment → renders without separators.
- 6+ segments → earlier segments may collapse into `…` (truncated breadcrumb).
- `color_role` → separator and active segment color shift.

**4. Prop Types/Shapes**
- `segments`: `Array<{ label: string, href?: string }>` — Ordered path from root to current. E.g. `[{ label: "World Map" }, { label: "Dungeon", href: "/dungeon" }, { label: "Floor 3" }]`. Last item is the current page (no `href` needed).
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `segments` → render nothing or hide component.
- Very long segment labels → truncate middle segments before the active (last) one.
- No `href` on intermediate segments → render as plain text, not a link.

---

### `form.single-field`
**Props:** `label`, `placeholder`, `hint`, `color_role_optional`

**1. Purpose**
A minimal, single-field form for collecting one piece of player input — character name on game start, a password for save encryption, or a search term in an item database. More structured than `input.text` alone, as it includes the label and hint layout as a unified unit.

**2. Default View**
A vertical stack: `label` text above, the input field in the middle, and `hint` text in small muted text below. The input has the `placeholder` ghost text. Submit action is handled externally (a linked button or Enter key). Visually complete as a standalone form unit.

**3. Randomized View**
- Different `label` + `placeholder` combinations change the input's perceived purpose.
- Short `hint` vs. long `hint` → hint text wraps below the input.
- `color_role` → label color, border color, and hint color shift.

**4. Prop Types/Shapes**
- `label`: `string` — Field label above input, e.g. `"Your Character's Name"`.
- `placeholder`: `string` — Ghost text inside input, e.g. `"E.g. Kira Dunmore"`.
- `hint`: `string` — Sub-label below input, e.g. `"Max 16 characters. No special symbols."`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- All three text props are empty strings → renders a bare input with no context — valid in controlled scenarios but confusing in practice.
- `hint` is very long → wraps gracefully below the field without affecting field width.
- Validation errors → this component may need an error state (red border + error message replacing hint).

---

### `card.simple`
**Props:** `title`, `body_text`, `color_role_optional`

**1. Purpose**
A general-purpose content card for displaying a self-contained piece of information — an ability description, a lore entry, a notice board posting, an NPC bio, or a game tip. The foundational "content chunk" component of the design system, used wherever a bordered, padded text block is needed.

**2. Default View**
A bordered, padded rectangular card with `title` as a bold header and `body_text` as a prose paragraph below. Drop shadow or border radius provides card depth. Background is slightly differentiated from the surrounding surface.

**3. Randomized View**
- Short `title` + short `body_text` → compact card.
- Long `body_text` (multiple paragraphs) → card grows vertically; consider max-height + scroll.
- `color_role` → card border, header background, or accent color shifts.

**4. Prop Types/Shapes**
- `title`: `string` — Card heading, e.g. `"Fireball"`, `"The Old Miller's Tale"`, `"Notice: Curfew in Effect"`.
- `body_text`: `string` — Body content, e.g. `"Deals 6d6 fire damage in a 20ft radius. Reflex save DC 15 for half."`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `title` is empty → render card with body only; hide title area.
- `body_text` is empty → render with title only; hide body area.
- Both empty → do not render the card.
- Very long `body_text` → either scroll or paginate.

---

### `header.banner`
**Props:** `title`, `controls[]`, `color_role_optional`

**1. Purpose**
The top banner/header of a view, screen, or panel — showing the current section title and providing control buttons in the top-right (e.g. close, minimize, settings, help). Common in game menus, inventory screens, map overlays, and system panels. The game equivalent of a desktop application's title bar.

**2. Default View**
A full-width horizontal bar with `title` on the left (or centered) and `controls` as a row of icon/text buttons on the right. Background slightly elevated from the content area. Height typically 40–56px. Title is styled prominently (bold, larger font).

**3. Randomized View**
- `controls` with many buttons → buttons stack or overflow; may need a dropdown for extras.
- `controls` empty → header renders title only (clean, minimal).
- `color_role` → banner background/text color shifts strongly (this is a prominent theming surface).

**4. Prop Types/Shapes**
- `title`: `string` — Screen/panel title, e.g. `"Inventory"`, `"World Map"`, `"Settings"`, `"Chapter 2: The Descent"`.
- `controls`: `Array<{ id: string, label: string, icon?: string, action: string }>` — E.g. `[{ id: "close", label: "Close", icon: "✕", action: "close" }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Long `title` + many `controls` → title truncates before controls.
- `controls` array is empty → right side is blank; title can center.
- Control with missing `label` → falls back to `id` for accessibility.

---

### `nav.vertical`
**Props:** `items[]`, `active_id`, `color_role_optional`

**1. Purpose**
A vertical navigation sidebar for multi-section screens — character sheet tabs (Stats / Inventory / Skills / Journal), settings categories (Audio / Video / Controls), or a game's main menu list. Provides clear wayfinding and section switching without full page navigation.

**2. Default View**
A vertically stacked list of navigation items, each showing a label (and optionally an icon). The item matching `active_id` is visually highlighted (bold text, accent background, or a left-border indicator). Items not matching `active_id` are interactive and navigate on click. Standard width: 160–240px.

**3. Randomized View**
- `active_id` changes → highlight moves to new active item with a smooth transition.
- 2 items vs. 10 items → list grows; may need scroll if it overflows the container.
- Items with icons → icon renders left of label.
- `color_role` → active highlight color and sidebar background shift.

**4. Prop Types/Shapes**
- `items`: `Array<{ id: string, label: string, icon?: string, disabled?: boolean }>` — E.g. `[{ id: "stats", label: "Stats", icon: "📊" }, { id: "inventory", label: "Inventory", icon: "🎒", disabled: false }]`.
- `active_id`: `string` — The `id` of the currently selected nav item.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `active_id` doesn't match any item `id` → no item highlighted; log a warning.
- Disabled items → rendered but not clickable; shown in muted styling.
- Single nav item → still renders correctly (not meaningless in all contexts).

---

### `layout.two-column`
**Props:** `left_content`, `right_content`, `color_role_optional`

**1. Purpose**
A two-column layout container for split-screen game UI panels — map on the left, room details on the right; character portrait on the left, stats on the right; narrative log on the left, command input + inventory on the right. Common in classic CRPGs (Baldur's Gate, Planescape Torment) and complex information-dense UIs.

**2. Default View**
A horizontally divided container with two child regions. Default split: 50/50 or configurable (e.g. 30/70 for nav + content). Both regions fill the container's height. A `divider.horizontal` rotated or a vertical border may separate them. Overflow within each column is independent.

**3. Randomized View**
- Different content in each column → columns are independent; one may be taller than the other.
- `color_role` → column backgrounds or the divider between them may shift.
- On narrow viewports → columns stack vertically (responsive behavior).

**4. Prop Types/Shapes**
- `left_content`: `ReactNode | ComponentRef` — The left column's child content. Accepts any renderable content.
- `right_content`: `ReactNode | ComponentRef` — The right column's child content.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Content in one column is much taller → define whether the layout stretches or clips.
- Viewport is too narrow for two columns → must collapse gracefully to single-column stacked layout.
- Both columns empty → render an empty two-column frame (acceptable during loading states).

---

### `layout.stack`
**Props:** `blocks[]`, `color_role_optional`

**1. Purpose**
A vertical stacking layout for composing multiple components into a sequential top-to-bottom arrangement. The flex/grid equivalent for ordered content flows — stacking a header, a room card, an entity list, a command input, and a hint bar. Fundamental for assembling screen layouts from discrete component blocks.

**2. Default View**
A vertically ordered sequence of `blocks`, each separated by consistent spacing (a gap or margin defined by the design system's spacing scale). No borders of its own. Fills its container's width. Each block renders at full width.

**3. Randomized View**
- Varying number of blocks → stack grows or shrinks; spacing remains consistent.
- Blocks with different heights → stack accommodates all sizes.
- `color_role` → minimal visual effect (stack itself has no significant chrome); may set background.

**4. Prop Types/Shapes**
- `blocks`: `Array<ReactNode | ComponentRef>` — Ordered list of child components/content to stack vertically.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `blocks[]` → render nothing (or an invisible container).
- Single block → renders with no visible stacking; effectively a wrapper.
- Very many blocks → entire page height may be exceeded; define scroll behavior on the parent container.

---

### `modal.overlay`
**Props:** `title`, `body_text`, `color_role_optional`

**1. Purpose**
A modal dialog for interrupting game flow with important information — a death screen, a level-up summary, a confirmation dialog ("Are you sure you want to quit?"), or a story event cutscene summary. Modals block interaction with the background and demand player acknowledgment before continuing.

**2. Default View**
A centered dialog box with a semi-transparent dark overlay behind it covering the full viewport. Inside: `title` as a prominent header, `body_text` as body content, and action buttons (typically rendered separately, e.g. "OK", "Cancel"). Has close behavior on button press or Escape key. Entrance animation (fade-in or slide-up) is common.

**3. Randomized View**
- Short `body_text` → compact modal.
- Long `body_text` → scrollable body area; modal height is capped.
- `color_role` = `"danger"` → modal header/border takes a red tone (for death/error scenarios).
- `color_role` = `"success"` → golden/green tone (for victory/level-up).

**4. Prop Types/Shapes**
- `title`: `string` — Modal heading, e.g. `"You Died"`, `"Level Up!"`, `"Confirm Quit"`, `"New Message"`.
- `body_text`: `string` — Body content, e.g. `"Your adventure ends here. You reached Floor 12 and slew 47 enemies."`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Modal opened while another modal is open → stack modals or prevent double-opening.
- Body text is empty → render title-only modal (valid for simple confirmations).
- Player presses Escape → modal should close (or at minimum, not lock the player out).
- Focus trap: keyboard focus must stay inside the modal while it is open.
- Background game logic → must pause or ignore input while modal is active.

---

### `toast.inline`
**Props:** `message`, `variant`, `color_role_optional`

**1. Purpose**
A brief, non-blocking notification that appears temporarily on screen without interrupting gameplay — "Item added to inventory", "Autosaved", "Achievement unlocked: First Blood". Unlike modals, toasts are transient and do not require interaction. Inspired by the toast notification pattern ubiquitous in modern UI, adapted for games.

**2. Default View**
A small pill or banner rendered at a fixed position (bottom-right or top-center common in games). Shows `message` text and a `variant`-based icon/color: `"info"` (blue), `"success"` (green), `"warning"` (amber), `"error"` (red). Auto-dismisses after ~2–4 seconds with a fade-out. A progress bar at the bottom may indicate remaining display time.

**3. Randomized View**
- `variant = "warning"` → amber background with ⚠ icon.
- `variant = "error"` → red background with ✗ icon.
- Multiple toasts queued → stack vertically.
- `color_role` → modifies surrounding chrome while `variant` governs the semantic color.

**4. Prop Types/Shapes**
- `message`: `string` — Notification text, e.g. `"Sword of Valor added to inventory."`, `"Game autosaved."`, `"Low health! Find a healing item."`.
- `variant`: `"info" | "success" | "warning" | "error"` — Semantic type governing color and icon.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Rapid succession of toasts → queue system; do not stack infinitely.
- Very long `message` → wrap within toast width; cap at 2 lines with ellipsis.
- Unknown `variant` → fallback to `"info"`.
- Toast during a modal overlay → toast should either render above the modal or be suppressed until modal closes.

---

### `progress-bar.horizontal`
**Props:** `value`, `max`, `label_optional`, `color_role_optional`

**1. Purpose**
A horizontal fill bar for tracking progress toward a goal — experience points to the next level, loading progress, quest completion percentage, download/install progress in menus, or a crafting timer. One of the most universally used UI elements in all of game design.

**2. Default View**
A full-width bordered track with a filled portion representing `value / max * 100%`. The fill color is semantic by default (blue for XP, green for HP, yellow for stamina — though this may be overridden by `color_role`). The optional `label` appears above the bar or overlaid on it (e.g. "XP: 340 / 500").

**3. Randomized View**
- `value = 0` → empty bar.
- `value = max` → full bar, possibly with a completion pulse animation.
- `value` changes incrementally → bar animates (smooth CSS transition) to new fill amount.
- `color_role` → bar fill color shifts.

**4. Prop Types/Shapes**
- `value`: `number` (non-negative) — Current amount. E.g. `340`.
- `max`: `number` (positive) — Maximum value. E.g. `500`.
- `label_optional`: `string | undefined` — Descriptor text, e.g. `"XP"`, `"Loading…"`, `"Quest Progress"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `value > max` → cap display at 100% (e.g. overflow XP); do not break layout.
- `max = 0` → guard against division-by-zero; render as empty or show an error state.
- `value` or `max` is negative → treat as 0.
- `value` animated changes larger than a few percent at once → animation should not appear to "teleport."

---

### `spinner.loading`
**Props:** `(none) or style_hint`, `frames[]`, `color_role_optional`

**1. Purpose**
A loading/waiting indicator shown during async operations — loading a save file, generating a dungeon, waiting for a network response in a multiplayer game. Provides feedback that the system is working and hasn't frozen. `frames[]` allows custom ASCII/Unicode animation sequences for text-mode or themed games (e.g. `["|", "/", "—", "\\"]` or `["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]`).

**2. Default View**
An animated cycling glyph (using `frames[]`) centered in the component, with no other decoration. Default frames if none provided: a simple CSS spinner icon or `["|", "/", "—", "\\"]`. Cycles at ~150ms per frame. `style_hint` can modify size or label (e.g. `"large"`, `"inline"`, `"overlay"`).

**3. Randomized View**
- Custom `frames` array → different animation characters cycle in sequence.
- `style_hint = "overlay"` → spinner rendered over a dimmed fullscreen background.
- `style_hint = "inline"` → spinner renders as a tiny inline indicator beside text.
- `color_role` → spinner color shifts.

**4. Prop Types/Shapes**
- `style_hint`: `"default" | "large" | "inline" | "overlay" | undefined` — Size/context modifier.
- `frames`: `Array<string> | undefined` — Array of animation frame strings. E.g. `["|", "/", "—", "\\"]`. If not provided, a default set is used.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `frames` is empty array `[]` → fallback to default frames; do not break animation loop.
- `frames` has only one element → no apparent animation; acceptable but potentially confusing.
- Spinner renders for too long (30+ seconds) → should be paired with a timeout/error state at the application level.
- Multiple spinners on screen simultaneously → ensure they don't use synchronized timers (stagger offset).

---

## Chunk 3 — Components 33–48

---

### `typography.banner`
**Props:** `text`, `style_hint`, `font_optional`, `color_role_optional`

**1. Purpose**
Large, prominent display text for game titles, chapter headings, win/loss screens, zone name announcements, and dramatic narrative moments. The typographic equivalent of a cinematic title card. Used in game UIs when text itself needs to carry visual weight — e.g. "GAME OVER", "Chapter 3: Into the Dark", "LEVEL COMPLETE".

**2. Default View**
Very large text (48–96px) centered horizontally, using a display or serif font. `style_hint` controls visual treatment (e.g. `"outlined"`, `"shadowed"`, `"glowing"`). `font_optional` allows override to a thematic typeface. Typically full-width, centered, with generous vertical padding.

**3. Randomized View**
- Short text ("WIN") vs. long text ("THE DARKNESS RECLAIMS WHAT WAS LOST") → font scales down or wraps.
- `style_hint = "glowing"` → text-shadow glow effect in the `color_role` color.
- `font_optional = "serif"` vs. `"monospace"` → dramatic change in character and mood.
- `color_role` → text and glow/shadow color shift.

**4. Prop Types/Shapes**
- `text`: `string` — Display text, e.g. `"GAME OVER"`, `"Chapter 4"`, `"A New Dawn"`.
- `style_hint`: `"default" | "outlined" | "shadowed" | "glowing" | "embossed" | undefined` — Visual treatment.
- `font_optional`: `string | undefined` — Font family name or token, e.g. `"serif"`, `"pixel"`, `"gothic"`, or a CSS font-family string.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Very long `text` → must wrap; font size may need to scale down (fluid typography).
- Empty `text` → do not render.
- `font_optional` is an invalid/missing font → fallback to system font stack.
- Used in a small container → must not overflow; respect container boundaries.

---

### `speech-bubble.left`
**Props:** `text`, `speaker_id`, `color_role_optional`

**1. Purpose**
A dialogue bubble aligned to the left, representing an NPC, companion, or other non-player speaker in conversation sequences. The left alignment and `speaker_id` attribute it to a character on the left side of the screen — standard visual novel and RPG dialogue convention (the "other" character speaks on the left). Found in games like Persona, Fire Emblem, Undertale, and countless visual novels.

**2. Default View**
A rounded rectangle bubble with a tail pointing downward-left. `speaker_id` appears above the bubble as a name label (in the character's accent color or a neutral secondary style). `text` fills the bubble body. Bubble appears on the left half of the layout. Width: 60–70% of container max.

**3. Randomized View**
- Long `text` → bubble grows taller; tail stays anchored at bottom-left.
- Different `speaker_id` values → name label above bubble changes; bubble color may shift per character.
- `color_role` → bubble background and border color shift.

**4. Prop Types/Shapes**
- `text`: `string` — NPC dialogue, e.g. `"You look like you could use some help, stranger."`.
- `speaker_id`: `string` — NPC identifier or display name, e.g. `"Guard Captain"`, `"Merchant Helda"`, `"????"`. Rendered as the speaker label.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `speaker_id` is empty or unknown → show generic label ("???") rather than blank.
- Very long `text` (monologue) → bubble has a max-height with scroll, or text is paginated.
- Multiple sequential speech bubbles from same speaker → may collapse name label on consecutive messages.
- Rendered on a narrow screen → bubble width adjusts; text wraps rather than overflows.

---

### `speech-bubble.right`
**Props:** `text`, `color_role_optional`

**1. Purpose**
A dialogue bubble aligned to the right, representing the player character's responses or choices in a conversation. No `speaker_id` is needed because "the player" is the implicit speaker — the right side of the screen is the player's side by convention (as in Persona 5's Joker, or the protagonist in most visual novels). Can also represent a second character on the right in a two-character conversation.

**2. Default View**
Mirrors `speech-bubble.left` but right-aligned: bubble tail points downward-right, bubble body is in the right half of the layout, and no speaker name is shown (or "You" / "Player" is shown). Player bubbles often use a distinct color from NPC bubbles (e.g. darker, blue-tinted, or a "your color" theme).

**3. Randomized View**
- Long `text` → bubble grows taller on the right side.
- `color_role` → player bubble color shifts; useful for differentiating parties in multi-party conversations.

**4. Prop Types/Shapes**
- `text`: `string` — Player dialogue or chosen response, e.g. `"I'll take the quest."`, `"Who are you?"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Very long `text` (if player types freely) → same as `speech-bubble.left`: max-height + scroll or pagination.
- Used in a context where two right-side bubbles appear consecutively → spacing rules prevent visual collision.
- Contrast between player bubble and NPC bubble must be sufficient when both are visible simultaneously.

---

### `choice-wheel.inline`
**Props:** `options[]`, `color_role_optional`

**1. Purpose**
Presents the player with a set of selectable dialogue or action choices — the "dialogue wheel" popularized by Mass Effect, or inline choice menus in visual novels. `options[]` are the available choices; the player picks one to advance the narrative or trigger an action. Also used in non-dialogue contexts (choose your path, select a reward).

**2. Default View**
A horizontal row (or vertical list, depending on count) of labeled option buttons, numbered or lettered for keyboard accessibility (e.g. [1] Accept, [2] Refuse, [3] Ask more). Each option is a selectable button styled consistently. The active/hovered option is highlighted. If rendered as a wheel (radial), options are arranged circularly.

**3. Randomized View**
- 2 options → simple binary choice layout.
- 6 options → may need a grid or multi-row layout.
- Long option text → options wrap within their button bounds.
- `color_role` → option button background/border color shifts.
- Some options with `disabled: true` → rendered grayed out and unclickable.

**4. Prop Types/Shapes**
- `options`: `Array<{ id: string, text: string, disabled?: boolean, consequence_hint?: string }>` — E.g. `[{ id: "accept", text: "I'll help you." }, { id: "refuse", text: "Find someone else." }, { id: "more", text: "Tell me more first.", consequence_hint: "Delays quest start." }]`. `consequence_hint` may display a tooltip.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Only 1 option → effectively "press to continue"; render as a clear continue prompt.
- All options `disabled` → player is locked out; ensure there's always at least one available option.
- Very many options (10+) → scroll or paginate; don't overflow the screen.
- Options with identical `text` → disambiguate (add `id`-based sub-labels in dev mode).

---

### `menu.main`
**Props:** `title`, `items[]`, `color_role_optional`

**1. Purpose**
The main game menu — the first screen the player sees when launching the game. Contains top-level actions: New Game, Load Game, Settings, Credits, Quit. Sets the tone and visual identity for the entire game experience. The menu is both functional and a branding surface.

**2. Default View**
A centered vertical list of menu items below the game `title`. Each item is a large, clearly clickable option. The title is displayed prominently (often using `typography.banner` styling). Background may be animated (particle effects, a game scene loop) but the component itself provides the menu structure. Items are navigable by keyboard (arrow keys + Enter).

**3. Randomized View**
- Few items (3: New/Load/Quit) → compact, centered, elegant.
- Many items (8+) → items may need spacing adjustment to prevent feeling crowded.
- `color_role` → heavy theming opportunity; this component's background, title color, and item hover states all shift.

**4. Prop Types/Shapes**
- `title`: `string` — Game or menu title, e.g. `"Echoes of the Void"`, `"Main Menu"`.
- `items`: `Array<{ id: string, label: string, disabled?: boolean, badge?: string }>` — E.g. `[{ id: "new_game", label: "New Game" }, { id: "load", label: "Load Game" }, { id: "settings", label: "Settings" }, { id: "quit", label: "Quit", badge: undefined }]`. `badge` could show "NEW" or "!" for notifications.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `items` is empty → render title only with no list; unusual but should not crash.
- Disabled `items` → grayed out, not selectable (e.g. "Load Game" disabled if no saves exist).
- `title` is very long → must scale down or wrap without obscuring menu items.
- First render: keyboard focus should automatically land on the first enabled item.

---

### `menu.pause`
**Props:** `title`, `items[]`, `color_role_optional`

**1. Purpose**
The in-game pause menu, accessed while the game is suspended mid-play. Typically contains: Resume, Save Game, Load Game, Settings, Return to Main Menu. Unlike `menu.main`, this renders as an overlay on top of the paused game state (the game world is frozen/blurred in the background). Its design prioritizes quick navigation back to play.

**2. Default View**
A semi-transparent or fully opaque centered overlay (usually narrower than `menu.main`) with the `title` (e.g. "PAUSED") at the top and `items` as a vertical list. Background shows the frozen game state or a blurred screenshot. "Resume" is always the first item and has default focus so a quick Escape/press continues the game.

**3. Randomized View**
- Different `title` values → e.g. `"Game Paused"`, `"PAUSED"`, or the game's thematic equivalent.
- `items` vary based on game state (e.g. "Save" disabled in a boss fight zone) → disabled states important here.
- `color_role` → overlay tint and item styling shift.

**4. Prop Types/Shapes**
- Same types as `menu.main`.
- `title`: `string` — Typically `"Paused"`, `"Game Paused"`, or thematic equivalent.
- `items`: Same array structure. The first item is conventionally "Resume".
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Game state doesn't allow pausing (e.g. online multiplayer) → component should not render or be inaccessible.
- "Save" item disabled in certain zones → communicate to player why (tooltip or hint).
- Background interaction while pause menu is open → must be blocked (pointer-events: none on background).
- Pause triggered during a modal (e.g. a dialogue) → stack management must handle layered overlays.

---

### `inventory.grid`
**Props:** `slots[]`, `columns`, `color_role_optional`

**1. Purpose**
A grid-based inventory UI where each item occupies one or more grid cells (depending on the system). The visual language of Diablo, Resident Evil, Escape from Tarkov's stash, and countless RPGs. Players drag-and-drop items between slots, compare equipment, and manage limited carry capacity. The grid is the most spatially intuitive inventory representation for item-heavy games.

**2. Default View**
A rectangular grid with `columns` defining the number of columns (rows are derived from `slots.length / columns`). Each cell shows an item icon (or is empty). Hovering a cell shows the item's tooltip. Occupied cells have an icon and optionally a quantity badge. Empty cells are darkened/hatched. A scroll bar appears if the grid exceeds its container height.

**3. Randomized View**
- Mostly empty slots → sparse grid with many dark empty cells.
- Fully filled slots → dense, colorful grid.
- `columns = 4` vs `columns = 10` → narrower vs. wider grid layout.
- `color_role` → grid background and cell border colors shift.

**4. Prop Types/Shapes**
- `slots`: `Array<{ id: string, item?: { name: string, icon: string, quantity?: number, rarity?: string } }>` — Each slot may be empty (no `item`) or contain an item. E.g. `[{ id: "slot_0", item: { name: "Iron Sword", icon: "⚔", quantity: 1, rarity: "common" } }, { id: "slot_1" }]`.
- `columns`: `number` (positive integer) — Grid column count, e.g. `4`, `8`, `10`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `slots` array length is not divisible by `columns` → last row has trailing empty cells.
- `columns = 0` or negative → guard; default to `4`.
- Very many slots (100+) → virtualize the grid.
- Two items with the same `id` → deduplicate or warn.
- Items with `quantity = 0` → either show empty slot or show quantity badge "0" as a warning state.

---

### `inventory.list`
**Props:** `items[]`, `color_role_optional`

**1. Purpose**
A list-view inventory for games where a grid is too visual/dense — text adventures, classic JRPGs (Final Fantasy menu), survival games showing a simple item list. More readable for items where name and stats matter more than spatial arrangement. Easier to navigate with a keyboard or D-pad.

**2. Default View**
A vertically scrolling list where each row shows: item icon/symbol (optional), item name, quantity, and a brief stat or category label. Selectable rows highlight on hover/focus. May include sort controls at the top (by name, type, weight). Width spans its container.

**3. Randomized View**
- Long item names → names truncate with ellipsis; full name in tooltip.
- High quantity values → number formatted with commas.
- 100+ items → virtual scroll list; smooth performance.
- `color_role` → row hover color, header background, and border shift.

**4. Prop Types/Shapes**
- `items`: `Array<{ id: string, name: string, quantity: number, category?: string, weight?: number, icon?: string, equipped?: boolean }>` — E.g. `[{ id: "item_001", name: "Health Potion", quantity: 3, category: "Consumable", weight: 0.5 }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `items[]` → show "Your inventory is empty."
- Items with `quantity = 0` → filter out or show as grayed out.
- `equipped` items → marked with an indicator (e.g. ✓ or [E] tag).
- Very long list → performance via virtual scrolling.

---

### `character-sheet.compact`
**Props:** `name`, `stats[]`, `color_role_optional`

**1. Purpose**
A condensed view of a character's core attributes — name, class, level, and key stats (STR, DEX, CON, INT, etc. in D&D terms; or HP, ATK, DEF, SPD in JRPG terms). Designed for sidebar display, character select screens, party management, or quick-reference panels without opening the full character screen. The "at a glance" version of a full character sheet.

**2. Default View**
Character name as a header, followed by a compact grid or list of `stats[]` rendered as `label.inline` pairs (e.g. "STR: 14 | DEX: 12 | CON: 16"). Stats are laid out in a 2- or 3-column grid for density. Color coding may indicate stat bonuses (green) or penalties (red) relative to base values.

**3. Randomized View**
- Different character → name and all stat values change.
- Stats with modifiers (STR 14 → STR 14 (+2)) → display both base and modifier.
- Many stats (12+) → grid wraps or scrolls.
- `color_role` → header background and accent color shift.

**4. Prop Types/Shapes**
- `name`: `string` — Character name, e.g. `"Elara Voss"`, `"The Warden"`.
- `stats`: `Array<{ key: string, label: string, value: number | string, modifier?: number }>` — E.g. `[{ key: "str", label: "STR", value: 14, modifier: 2 }, { key: "dex", label: "DEX", value: 10 }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `stats[]` → show name only with "No stats available."
- `name` is empty → use a fallback like "Unknown Character".
- Negative `modifier` → display as `(-1)` in red.
- Very long stat labels or values → truncate within their cell.

---

### `panel.survival-status`
**Props:** `needs[]`, `color_role_optional`

**1. Purpose**
Displays the player's survival needs in games with survival mechanics — hunger, thirst, fatigue, temperature, oxygen, sanity, etc. Prominent in survival games like The Long Dark, Don't Starve, Green Hell, and Minecraft's hunger bar. Players must track these needs and manage them or face penalties. Each need has a current value, a max, and typically a critical threshold.

**2. Default View**
A stacked or grid panel showing each need as a labeled meter or bar. Each entry includes: need icon or label (e.g. 🍗 Hunger), a fill bar showing current level, and a status descriptor at extremes (e.g. "Starving", "Full"). Critical states (near-zero or near-max) are highlighted in red or amber. The panel is typically compact and persistent.

**3. Randomized View**
- All needs at full → all bars green, no alerts.
- `hunger` near zero → hunger bar turns red, pulses or displays "STARVING" warning.
- Many needs (8+) → panel grows tall; may need to scroll or collapse less-critical needs.
- `color_role` → panel background and border shift; semantic need colors remain.

**4. Prop Types/Shapes**
- `needs`: `Array<{ id: string, label: string, icon?: string, current: number, max: number, critical_threshold?: number, status_label?: string }>` — E.g. `[{ id: "hunger", label: "Hunger", icon: "🍗", current: 15, max: 100, critical_threshold: 20, status_label: "Famished" }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `current > max` (e.g. overfed/buffed) → cap at max; may show overflow icon.
- `max = 0` → guard against division-by-zero.
- `current` at exactly `critical_threshold` → trigger alert state.
- Empty `needs[]` → hide panel or show "All needs stable."
- Very many needs → consider collapsible sections or a compact icon-only mode.

---

### `tree.compact`
**Props:** `nodes[]`, `color_role_optional`

**1. Purpose**
A compact collapsible tree for displaying hierarchical data — a skill tree, a crafting recipe dependency tree, a tech tree, a file/asset hierarchy, or a decision tree. Compact variant means it minimizes vertical space while still showing parent-child relationships. Used in games like Civilization's tech tree, Path of Exile's passive skill tree (simplified), or any game with progression hierarchies.

**2. Default View**
An indented tree list where each node shows its label and an expand/collapse toggle if it has children. Root nodes start at level 0 indentation; each child level indents further (typically 16–20px per level). Leaf nodes (no children) show without a toggle. Unlocked/completed nodes appear brighter; locked nodes appear muted.

**3. Randomized View**
- Deep tree (5+ levels) → heavy indentation; horizontal scroll may appear.
- Wide tree (many siblings at one level) → long vertical list.
- Collapsed nodes → children hidden; expand toggle visible.
- `color_role` → tree accent color (connecting lines, active node highlight) shifts.

**4. Prop Types/Shapes**
- `nodes`: `Array<{ id: string, label: string, children?: Node[], unlocked?: boolean, active?: boolean, icon?: string }>` (recursive) — E.g. `{ id: "combat", label: "Combat", unlocked: true, children: [{ id: "sword_mastery", label: "Sword Mastery", unlocked: false }] }`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Circular references in `nodes` → must detect and prevent infinite render loops.
- Very deep nesting (10+ levels) → indentation overflows container; set a max visual depth.
- All nodes collapsed by default vs. all expanded → define a sensible default.
- A node with `unlocked: false` but `active: true` → contradictory state; define precedence.

---

### `tree.relationships`
**Props:** `relations[]`, `color_role_optional`

**1. Purpose**
Visualizes relationship networks — faction relationships, character relationship webs, diplomatic maps, or social graphs. Found in Crusader Kings III's character relationship view, in games like Disco Elysium (character/faction affinity), or political simulators. Unlike `tree.compact` (which is hierarchical/parent-child), `tree.relationships` is a graph that may have many-to-many connections.

**2. Default View**
A node-and-edge diagram: each `relation` entity is a node rendered as a labeled circle or badge; edges between nodes represent relationship type (ally, enemy, neutral, romantic, family) shown as colored lines with optional direction arrows and labels. Nodes are positioned to minimize edge crossings (force-directed or fixed layout). A legend explains edge types by color.

**3. Randomized View**
- Few relations (3 nodes) → sparse, readable graph.
- Many relations (20 nodes) → dense graph; may need zoom/pan or clustering.
- Different relationship types → edges change color (green = allied, red = hostile, gray = neutral).
- `color_role` → node background and edge default colors shift.

**4. Prop Types/Shapes**
- `relations`: `Array<{ id: string, label: string, connections: Array<{ target_id: string, type: "ally" | "enemy" | "neutral" | "family" | "romantic" | string, strength?: number }> }>` — E.g. `[{ id: "player", label: "You", connections: [{ target_id: "npc_001", type: "ally", strength: 80 }] }, { id: "npc_001", label: "Elder Mira", connections: [] }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- A node references a `target_id` that doesn't exist in `relations` → render a ghost/orphan node or skip the edge.
- Bidirectional relationships (A→B and B→A) → merge into a single undirected edge or show both arrows.
- Isolated nodes (no connections) → render as standalone labeled circles.
- Very large graphs (50+ nodes) → must virtualize or provide zoom/pan navigation.

---

### `meter.resource`
**Props:** `type`, `current`, `max`, `color_role_optional`

**1. Purpose**
A resource meter for tracking a named resource that depletes and regenerates — mana (magic), stamina/endurance, energy, fuel, ammo reserves, shields, durability. Distinct from the HP bar (`status-bar`) in that these resources are tactical consumables, not the player's survival state. Common in virtually every RPG, action game, and strategy game.

**2. Default View**
A horizontal or circular fill meter with the resource `type` label (e.g. "MP", "Stamina") and a numeric display (`current / max`). Color is semantically linked to the resource type (blue for mana, yellow/green for stamina, cyan for shields) but overridable by `color_role`. Depletion is visually dramatic — the bar empties from right to left.

**3. Randomized View**
- `current = 0` → fully depleted; label may shift to a warning state (e.g. "Out of Mana").
- `current = max` → full meter; may briefly pulse on restoration.
- Different `type` values (mana, stamina, fuel) → label changes; semantic color changes.
- `color_role` → explicit color override for when the semantic default isn't appropriate.

**4. Prop Types/Shapes**
- `type`: `string` — Resource name, e.g. `"Mana"`, `"MP"`, `"Stamina"`, `"Fuel"`, `"Shields"`, `"Energy"`.
- `current`: `number` (non-negative) — Current resource amount. E.g. `45`.
- `max`: `number` (positive) — Maximum resource amount. E.g. `100`.
- `color_role_optional`: `string | undefined` — Overrides semantic color.

**5. Edge Cases**
- `current > max` → cap at 100%; a common edge case with regeneration buffs.
- `max = 0` → division-by-zero guard; render as depleted.
- Rapid resource changes (fast combat) → animate transitions smoothly.
- `type` is an empty string → render meter without label.

---

### `counter.ammo`
**Props:** `current`, `max`, `label`, `color_role_optional`

**1. Purpose**
Tracks ammunition count for weapons — bullets in the chamber, arrows in the quiver, spell charges, throwing knives. A critical HUD element in shooters (Doom, Halo), action RPGs (Witcher), and roguelikes with ranged weapons. The visual convention is often individual pip representations for small counts (e.g. 6 revolver chambers), or numeric for large counts.

**2. Default View**
A compact component showing `current / max` (e.g. `12 / 30`) with the `label` (weapon or ammo type, e.g. "Pistol", "Arrows"). May render as: numeric text, individual pip icons, or a segmented horizontal bar. At low ammo (e.g. `current / max < 0.25`), the counter turns amber or red and may pulse. At `current = 0`, the label shows "EMPTY" or "RELOAD".

**3. Randomized View**
- `current = 0` → empty state: red color, "EMPTY" or "RELOAD" indicator.
- `current = max` → full ammo, green or neutral.
- Large `max` (300 bullets) → numeric display preferred over pips.
- Small `max` (6 chambers) → pip display preferred.
- `color_role` → color of label and counter shift.

**4. Prop Types/Shapes**
- `current`: `number` (non-negative integer) — Current ammo. E.g. `12`.
- `max`: `number` (positive integer) — Max ammo capacity. E.g. `30`.
- `label`: `string` — Weapon or ammo type, e.g. `"Pistol"`, `"Arrows"`, `"Fire Bolts"`, `"Charges"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- `current > max` (e.g. ammo overflow glitch) → cap display; don't crash.
- `max = 0` → guard; some weapons have "unlimited" ammo — render differently (e.g. "∞").
- `current = 0` → must clearly signal to player they cannot fire.
- Very high `max` (9999) → numeric display only; pips impractical.

---

### `counter.score`
**Props:** `value`, `label`, `color_role_optional`

**1. Purpose**
Displays a running score, point total, currency amount, or any accumulated numeric value. Central to arcade games, score-attack modes, leaderboards, and currency/resource displays in strategy games. The `label` contextualizes the number (e.g. "Score", "Gold", "Coins", "XP", "Points").

**2. Default View**
A prominent numeric display with `label` above or beside it. Score value is large and easily readable. May include a prefix symbol (e.g. "⭐", "💰", "G") before the number. In arcade contexts, the number animates upward (count-up) when increasing. Typically right-aligned in a HUD corner.

**3. Randomized View**
- Small value (0) → shows "0" cleanly.
- Large value (1,234,567) → formatted with thousands separators for readability.
- Rapid increments (combo scoring) → number animates/counts up smoothly.
- `color_role` → label and value colors shift; `"gold"` color role for currency is natural.

**4. Prop Types/Shapes**
- `value`: `number` (non-negative integer, or float for currency) — E.g. `0`, `4200`, `1234567`, `99.5`.
- `label`: `string` — Context label, e.g. `"Score"`, `"Gold"`, `"Coins"`, `"Points"`, `"EXP"`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Negative `value` (debt/penalty scoring) → must render with a minus sign; ensure layout accommodates.
- Very large values (overflow int bounds) → use BigInt or formatted string.
- `value` is `NaN` or `undefined` → display `0` or `—`; do not render `NaN`.
- Rapid large increments (score bomb) → animation must not lag or queue up indefinitely.

---

### `tracker.objective`
**Props:** `objectives[]`, `color_role_optional`

**1. Purpose**
Tracks active quests, mission objectives, and goals in the game world — the quest log HUD overlay. A standard component in RPGs (Skyrim's quest tracker), MMOs, narrative games, and mission-based action games. Players consult this to understand their current goals. Objectives may be primary (main quest) or secondary (side quests), completed or in-progress.

**2. Default View**
A vertically stacked list of `objectives`, each showing a checkbox/indicator, objective title, and optionally a short description or progress fraction (e.g. "Defeat Goblins (3/5)"). Completed objectives are shown with a strikethrough or checkmark in a muted style. Active/primary objectives may be highlighted or pinned. The component is typically displayed in a corner overlay during gameplay.

**3. Randomized View**
- All objectives complete → all rows checked/dimmed; "All objectives complete!" message.
- 1 active objective → single entry, focused.
- Mixed complete/incomplete → completed objectives visually distinct from active.
- Objective with progress fraction (3/5 complete) → shows a mini-progress bar or "3/5" counter.
- `color_role` → header and accent colors shift.

**4. Prop Types/Shapes**
- `objectives`: `Array<{ id: string, title: string, description?: string, completed: boolean, progress?: { current: number, total: number }, priority?: "primary" | "secondary" | "optional" }>` — E.g. `[{ id: "q1", title: "Find the Lost Artifact", description: "Last seen in the old mines.", completed: false, priority: "primary" }, { id: "q2", title: "Defeat 5 Goblins", completed: false, progress: { current: 3, total: 5 }, priority: "secondary" }]`.
- `color_role_optional`: `string | undefined`.

**5. Edge Cases**
- Empty `objectives[]` → show "No active objectives." rather than blank component.
- All objectives completed → show a completion state with clear visual feedback.
- Very many objectives (20+) → collapse completed objectives into a "Completed (N)" expandable section.
- `progress.current > progress.total` → cap display at total; do not break progress bar.
- Long `title` → truncate with ellipsis; full text in tooltip.

---

**End of designer pass.** Use your answers to update prop_shapes.yaml, defaults, and the randomizer as needed.

**Designer pass applied (tooling sync):** From your answers, the following were updated. **prop_shapes.yaml:** `scalar_types` enabled for integer props (hp_current, hp_max, turn_count, max_visible, max_length, value, max, current, columns, current_stage_index, turns_left, width, height, filled, success_chance_optional) so the randomizer keeps numeric props as integers. **component_visual_test.py:** Added `_get_scalar_type()`; randomizer now consults it so unknown scalar props typed as integer in the YAML get a sensible random integer. Added explicit randomizer branches for `risk_level` (LOW / MEDIUM / HIGH / CRITICAL) and `luck_band_optional` (Cursed, Neutral, Blessed, Lucky, Fading) for status-bar.risk. Array shapes and existing default/random behavior were already aligned with your intent (stats, needs, segments, options, items, etc.); no changes needed there.
