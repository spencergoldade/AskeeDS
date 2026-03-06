# AskeeDS Backlog

Open work ordered by **severity** (High → Medium → Low). For completed work and principles, see [ROADMAP.md](ROADMAP.md). For engine-team requests and workflow notes, see [STAKEHOLDER_REQUESTS.md](STAKEHOLDER_REQUESTS.md).

**Severity**

- **High** — Unblocks stakeholders, agreed commitment, or critical path.
- **Medium** — Valuable next step; no external blocker.
- **Low** — Nice-to-have or optional.

---

## High

| Item | Notes |
|------|------|
| **Mod theming / component extension** | Document contract so mods (adventures) can override or extend theme/components. Engine depends on this. |

---

## Medium

| Item | Notes |
|------|------|
| **Migrate more components to adaptive sizing** | `toast.inline`, `progress-bar.horizontal`, `form.single-field`; layouts propagate height. |
| **Table sizing support** | Table render type respects `available_width`; proportional columns; truncation. |
| **Theme variants** | Multiple theme definitions (dark, light, high-contrast) swapping color tokens. |
| **Textual adapter interaction wiring** | Keyboard actions from interaction specs to Textual key bindings; focus ring; messages. |
| **hint-bar.contextual (engine request)** | Optional API/component for engine-driven contextual hints. |

---

## Low

| Item | Notes |
|------|------|
| **JSON export** | `askee-ds export --format json` for component/token/screen definitions. |
| **Snapshot coverage for remaining 32 components** | Optional post-v1; 24 already have golden files. |
