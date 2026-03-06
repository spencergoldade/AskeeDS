# AskeeDS Backlog

Open work ordered by **severity** (High → Medium → Low). For completed work and principles, see [ROADMAP.md](ROADMAP.md). For engine-team requests and workflow notes, see [STAKEHOLDER_REQUESTS.md](STAKEHOLDER_REQUESTS.md).

**Severity**

- **High** — Unblocks stakeholders, agreed commitment, or critical path.
- **Medium** — Valuable next step; no external blocker.
- **Low** — Nice-to-have or optional.

---

## High

*None.*

---

## Medium

| Item | Notes |
|------|------|
| **Migrate more components to adaptive sizing** | `toast.inline`, `progress-bar.horizontal`, `form.single-field`; layouts propagate height. |
| **Table sizing support** | Table render type respects `available_width`; proportional columns; truncation. |
| **Theme variants** | Multiple theme definitions (dark, light, high-contrast) swapping color tokens. |
| **Textual adapter interaction wiring** | Keyboard actions from interaction specs to Textual key bindings; focus ring; messages. |
| **hint-bar.contextual (engine request)** | Optional API/component for engine-driven contextual hints. |
| **Standalone designer prototyping tool** | Facsimile-only tool: pick components from list, add to canvas, move with arrow keys; visual prototyping only. |

---

## Low

| Item | Notes |
|------|------|
| **JSON export** | `askee-ds export --format json` for component/token/screen definitions. |
| **Snapshot coverage for remaining 32 components** | Optional post-v1; 24 already have golden files. |
| **More color themes** | Additional theme definitions (e.g. extra palettes, seasonal, a11y-focused). |
| **Style themes (symbol swap)** | Themes that swap ASCII symbols in components (borders, bullets, icons) for different look and feel. |
