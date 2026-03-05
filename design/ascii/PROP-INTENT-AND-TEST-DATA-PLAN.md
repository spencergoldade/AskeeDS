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
| character-sheet.compact | name, stats[] | Y | default: stats ✓; **random: stats → generic id+label** | **Wrong shape on Z** | **Y** |
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

**Summary for this pass:** The only component with a **confirmed** wrong-shape-on-randomize gap in the table is **character-sheet.compact** (stats). Adding a **stats** branch to the randomizer fixes that one. The broader work is: (1) add a **prop-intent data source** and **stats** (and any other missing shapes) so future components don’t regress, and (2) go through “Ask?” rows (and any new components we add to the inventory) with the designer checklist so defaults and random data stay intent-preserving.

---

## 9. Next step

- **You:** Confirm this plan (and whether you prefer Option A or B for shape/type, and YAML vs JSON vs in-code dict for the data file).
- **Then:** We can either (a) do the **character-sheet.compact** fix immediately (stats branch in randomizer) and then add the data-driven Phase 2, or (b) do Phase 2 first (prop_shapes data + refactor) and fix character-sheet plus any other gaps in one go. For “Ask the designer,” we only need your input on components marked **Ask?** (and any you want to add from the “not in table” list).
