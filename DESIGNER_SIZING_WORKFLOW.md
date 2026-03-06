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

| Component | Render type | Current | Your choice | min_width | max_width | Notes |
|-----------|-------------|---------|-------------|-----------|-----------|-------|
| breadcrumb.inline | join | (content) | | | | |
| button.icon | inline | (content) | | | | |
| button.text | box | fixed | | | | |
| choice-wheel.inline | join | (content) | | | | |
| command-input.default | box | fixed | | | | |
| cooldown.badge | box | fixed | | | | |
| cooldown.row | box | fixed | | | | |
| counter.ammo | box | fixed | | | | |
| counter.score | box | fixed | | | | |
| divider.horizontal | box | fixed | | | | |
| exit-list.inline | join | (content) | | | | |
| feedback.error | box | fixed | | | | |
| feedback.mixed | box | fixed | | | | |
| form.single-field | box | fixed | | | | |
| header.banner | box | fixed | | | | |
| hint-bar.contextual | join | (content) | | | | |
| input.text | box | fixed | | | | |
| inventory.grid | grid | fixed | | | | |
| inventory.list | box | fixed | | | | |
| label.inline | inline | (content) | | | | |
| layout.app.shell | shell | (layout) | | | | |
| layout.stack | stack | (layout) | | | | |
| layout.two-column | columns | (layout) | | | | |
| meter.resource | box | fixed | | | | |
| minimap.default | box | fill | | | | (already has fill) |
| nav.vertical | box | fixed | | | | |
| notification.inline | box | fixed | | | | |
| panel.consequence | box | fixed | | | | |
| panel.survival-status | box | fixed | | | | |
| progress-bar.horizontal | box | fixed | | | | |
| screen.crafting | box | fixed | | | | |
| screen.death | box | fixed | | | | |
| screen.loading | box | fixed | | | | |
| screen.tutorial | box | fixed | | | | |
| speech-bubble | bubble | (content) | | | | |
| spinner.loading | frames | fixed | | | | |
| status-bar.risk | box | fixed | | | | |
| status-icon.row | box | fixed | | | | |
| table.fourcolumn | table | fixed | | | | |
| toast.inline | box | fixed | | | | |
| tooltip.default | box | fixed | | | | |
| tracker.clock | clock | fixed | | | | |
| tracker.front | stage_track | fixed | | | | |
| tracker.objective | box | fixed | | | | |
| tree.compact | tree | fixed | | | | |
| tree.relationships | tree | fixed | | | | |
| typography.banner | banner | fixed | | | | |

---

## Notes (optional)

Use this space for any overall notes, exceptions, or “migrate these first” priorities.

---

## When you’re done

When you’ve filled in the checklist (or as much as you want to decide now), tell the implementer. The next step is to apply your choices: migrate the next batch of components to `width: fill` (or `content`) with your min/max where applicable, then run tests and update snapshots. No migration work will be done until you’ve completed this workflow.
