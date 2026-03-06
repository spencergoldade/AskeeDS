# Designer sizing workflow

This document is **your checklist** to decide how each component should behave when the terminal or layout width changes. The implementation plan pauses here until you complete it. When you’re done, we use your choices to migrate the next batch of components to adaptive sizing.

---

## What you’re deciding

For each component (or group), choose:

- **fill** — The component grows or shrinks with available width, within optional min/max. Good for main content, room cards, menus.
- **content** — Width is driven by content; layout gives an upper bound. Good for short labels, buttons, narrow lists.
- **fixed** — Keep a specific character width. Good for small widgets (e.g. cooldown badge) that shouldn’t stretch.

If you choose **fill**, note `min_width` and `max_width` (in characters) so the component stays readable. If you’re unsure, leave the row blank and we can decide together in the next pass.

---

## Already adaptive (no action unless you want to change)

These 8 components already use `width: fill` with min/max constraints. You can leave them as-is or note a change in the “Notes” section at the bottom.

| Component | Current min | Current max |
|-----------|-------------|-------------|
| card.simple | 28 | 50 |
| character-sheet.compact | 28 | 44 |
| entity-list.room | 20 | 40 |
| menu.main | 30 | 50 |
| modal.overlay | 30 | 50 |
| narrative-log.pane | 40 | 70 |
| room-card.default | 30 | 60 |
| status-bar.default | 40 | 80 |

---

## Checklist: remaining components

Fill in **Your choice** (fill / content / fixed) and, if fill, **min_width** and **max_width**. You can add a short note per component if helpful.

**Current min / Current max:** From the component’s render spec. If the component has no width (e.g. inline, join), it’s content-sized: **—** means no box width; *default 80* is the framework’s default when no width is set (terminal default). **Suggested max** is a recommended max when you choose fill and haven’t set one yet.

| Component | Render type | Current | Your choice | Current min | Current max | Suggested max | min_width | max_width | Notes |
|-----------|-------------|---------|-------------|-------------|-------------|---------------|-----------|-----------|-------|
| breadcrumb.inline | join | (content) | content | — | — | 80 | 10| 80 | |
| button.icon | inline | (content) | content| — | — | 80 | 4 | 50 | Buttons should never span the entire screen, I don't think. |
| button.text | inline | (content) | content | — | — | 80 | 10 | 50 | |
| choice-wheel.inline | box | fixed 30 | content | 30 | 30 | 48 | 30 | 48 | |
| command-input.default | inline | (content) | content | — | — | 80 | 10 | 50 | |
| cooldown.badge | inline | (content) | fixed | — | — | 80 | 5 | 40 | |
| cooldown.row | join | (content) | content | — | — | 80 | 10 | 80 | |
| counter.ammo | inline | (content) | fixed | — | — | 80 | 5 | 20 | |
| counter.score | inline | (content) | fixed | — | — | 80 | 5 | 40 | |
| divider.horizontal | inline | (content) | fill | — | — | 80 | 5 | 80 | |
| exit-list.inline | join | (content) | content| — | — | 80 | 10 | 80 | |
| feedback.error | inline | (content) | fixed | — | — | 80 | 10 | 40 | |
| feedback.mixed | box | fixed 44 | fixed | 44 | 44 | 55 | 10 | 50 | |
| form.single-field | box | fixed 38 | fixed | 38 | 38 | 50 | 38 | 50 | The reason why I agreed about setting a fairly conservative max width on this one is that generally an entered form value will become a variable in a game. Like entering your player name and then having NPCs repeat that in text everywhere. We don't want whatever they enter to break things in a game. I may be overthinking this. |
| header.banner | box | fixed 50 | fixed | 50 | 50 | 72 | 50 | 72 | |
| hint-bar.contextual | join | (content) | content | — | — | 80 | 10 | 80 | |
| input.text | inline | (content) | content | — | — | 80 | 10 | 80 | |
| inventory.grid | grid | (cell×cols) | fill | — | — | 72 | 20 | 80 | |
| inventory.list | box | fill | fill | 24 | 50 | — | 10 | 80 | |
| label.inline | inline | (content) | content | — | — | 80 | 10 | 80 | |
| layout.app.shell | shell | (layout) | fill | — | — | n/a | n/a | n/a | |
| layout.stack | stack | (layout) | fill | — | — | n/a | n/a | n/a | |
| layout.two-column | columns | (layout) | fill | — | — | n/a | n/a | n/a | |
| meter.resource | inline | (content) | fixed | — | — | 80 | 8 | 40 | |
| minimap.default | box | fill | fill | 40 | 70 | — | | | (already has fill) |
| nav.vertical | box | fill | fill | 16 | 36 | — | | | Would obviously grow vertically if there were more options. |
| notification.inline | box | fixed 44 | fixed | 44 | 44 | 55 | | 55 | |
| panel.consequence | box | fixed 44 | fixed | 44 | 44 | 55 | | 55 | |
| panel.survival-status | box | fixed 40 | fixed | 40 | 40 | 50 | | 50 | |
| progress-bar.horizontal | box | fixed 40 | fixed | 40 | 40 | 55 | | 50 | |
| screen.crafting | box | fixed 44 | fixed | 44 | 44 | 60 | | 60 | I love this screen so much. I keep going back and forth on if we need permutations of this for crafting trees, where there are clearer categories you can craft things from. |
| screen.death | box | fixed 44 | fixed | 44 | 44 | 60 | | 60 | This would typically be accompanied with a secondary message, some decorative art, and some options, like allowing the player to start over or load a save. |
| screen.loading | box | fill | fill | 30 | 60 | — | | 60 | |
| screen.tutorial | box | fixed 36 | fixed | 36 | 36 | 55 | | 55 | |
| speech-bubble | bubble | (content) | content | — | — | 60 | | 60 | |
| spinner.loading | frames | (content) | fixed | — | — | 40 | | 40 | Typically, should belong inside of a loading screen, but could also be used elsewhere. |
| status-bar.risk | inline | (content) | fixed | — | — | 80 | | 80 | |
| status-icon.row | join | (content) | fixed | — | — | 80 | | 80 | I'm going with the suggested max here, but I have yet to think of an application where that makes sense. The flipside is that I can't think of why it shouldn't. |
| table.fourcolumn | table | (content) | fill | — | — | 80 | | 80 | The idea with any table is also that the column widths inside would need to be adjustable or content-aware as well. We'd likely need more than just a four-column table, too. It was suggested to me when talking about AskeeDS that perhaps we should treat our tables similar to how Markdown treats tables, which definitely got me thinking. |
| toast.inline | box | fixed 38 | fixed | 38 | 38 | 55 | | 55 | |
| tooltip.default | box | fixed 34 | fixed | 34 | 34 | 50 | | 50 | I am agreeing with the 50 recommendation for now, but we may need to revisit this later once the application of tooltips has been explored more. |
| tracker.clock | clock | (content) | fixed | — | — | 60 | | 80 | The reason I agreed with this being able to have a much larger max width is because I think it could be interesting in some games to have a really long clock running, maybe even spanning across the entire screen (contained by the layout, of course). With more ○ symbols stretching across and slowly filling up, turning into ● symbols. Could help articulate stakes and drama. |
| tracker.front | stage_track | (content) | fixed | — | — | 72 | | 72 | |
| tracker.objective | box | fixed 32 | fixed | 32 | 32 | 48 | | 48 | |
| tree.compact | tree | (content) | fixed | — | — | 50 | | 50 | This could make sense mixed with other components to show a skill tree, or how some quests have branching objectives. |
| tree.relationships | tree | (content) | fixed | — | — | 55 | | 55 | This could make sense mixed with other components to show a skill tree, or how some quests have branching objectives.  |
| typography.banner | banner | (content) | fill | — | — | 72 | | 72 | Figlet type can get quite large. It should be allowed to fill the space it's in. Contained by whatever it's in, of course. |

---

## Notes (optional)

Use this space for any overall notes, exceptions, or “migrate these first” priorities.

**Implementer note (short pass):** Migrated three box components to `width: fill` with default min/max: **inventory.list** (24–50), **nav.vertical** (16–36), **screen.loading** (30–60). Snapshots updated for the two approved ones. Layouts already fill via Composer. Deferred (need renderer/spec support): divider.horizontal, inventory.grid, table.fourcolumn, typography.banner. When you add min/max in the table, we can align or override these defaults.

**Implementer note (workflow filled):** Applied your min/max: **inventory.list** → fill 10–80; **choice-wheel.inline** → content 30–48. Snapshots updated for both. feedback.mixed remains fixed at 44 (designer confirmed min/max 10–50 was a mistake; disregarded).

---

## When you’re done

When you’ve filled in the checklist (or as much as you want to decide now), tell the implementer. The next step is to apply your choices: migrate the next batch of components to `width: fill` (or `content`) with your min/max where applicable, then run tests and update snapshots. No migration work will be done until you’ve completed this workflow.

---

## Proposed next steps for stable v1

With all 56 components now approved and sizing decisions applied where possible, the following will get the project to a shippable v1:

1. **Document the render contract** — In REFERENCE or INTEGRATING, add a short "What the renderer produces" section: list of lines (strings), one per line; optional style hints if we add them. Lets adapter authors (and future HTML/JSON adapters) know the contract without reading code.

2. **Optional: RenderOutput type** — If low effort, introduce a small dataclass (e.g. `lines: list[str]`, optional `styles`) and have the renderer or adapter layer return it so future adapters plug in cleanly. If it's a large refactor, skip for v1.

3. **ROADMAP and VERSION** — Set ROADMAP "What's next" to post-v1 (e.g. snapshot coverage for remaining 32 components, table/grid/banner sizing, Textual key wiring). Bump VERSION to 1.0.0 when you're ready to tag.

4. **Release checklist** — Before tagging v1: run `askee-ds validate`, full pytest, quick manual `preview`/`compose` with a theme; ensure README and CHANGELOG are accurate.

Deferred to post-v1: full Textual interaction wiring, theme variants beyond the four shipped, HTML/JSON adapters. (Divider/grid/table/banner fill support is done.)
