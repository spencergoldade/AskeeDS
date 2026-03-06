# AskeeDS v1 Final Pass — Plan (Phase 1 Step 1.2)

This document captures the strategic choices, structure, tools, exclusions, and to-do plan from the final pass before first major stable release. It is based on your answers to the eight assessment questions.

---

## Overarching strategic changes (and why)

1. **Add a theme-variant system (dark, light, high-contrast grayscale + experimental color)** — Aligns with a11y principles and your requirement that v1 include grayscale variants plus one clearly labeled experimental color theme.

2. **Keep interaction declarative-only; do not block v1 on full Textual key/focus wiring** — Matches “engines implement behaviour”; keeps the design system lightweight and extendible.

3. **Introduce a designer sizing workflow and a planned pause** — You need a documented checklist so you can decide which components get adaptive sizing; the plan includes a pause for you to complete it before more migration work.

4. **Prepare an output-agnostic contract (low effort)** — Document what the renderer produces and, if straightforward, introduce a small “render result” type so future adapters (e.g. HTML, JSON) can plug in without rewriting the core; no new output adapters in v1.

5. **Keep 24 approved + 32 ideated visible** — No batch promotion; ideated stays discoverable for feedback and conversation.

6. **Treat YAML + schema as the single source of truth** — No design-tool sync in scope unless you add it later.

---

## Optimal folder structure (tree)

```
askeeDS/
├── components/              # unchanged: YAML component definitions
│   ├── _schema.yaml
│   ├── core/
│   └── game/
├── tokens/                  # unchanged: shared structure (borders, typography, sizing, bar)
│   ├── borders.yaml
│   ├── typography.yaml
│   ├── sizing.yaml
│   └── colors.yaml         # optional: keep as fallback or move default into themes
├── themes/                  # NEW: theme variants (select one per runtime)
│   ├── dark.yaml           # grayscale
│   ├── light.yaml         # grayscale
│   ├── high-contrast.yaml # grayscale, a11y
│   └── experimental.yaml  # color; clearly labeled experimental
├── screens/
│   ├── _schema.yaml
│   └── examples/
├── askee_ds/
│   ├── loader.py          # extend: load_theme(name) or load_tokens_dir + theme overlay
│   ├── theme.py           # extend: accept theme name or path for variant
│   ├── renderer.py
│   ├── composer.py
│   ├── sizing.py
│   ├── validator.py
│   ├── cli.py             # extend: --theme dark|light|high-contrast|experimental
│   ├── render_types/
│   └── adapters/
├── tests/
├── examples/
├── _archive/
├── DESIGNER_SIZING_WORKFLOW.md   # NEW: checklist for you to complete (pause point)
├── GUIDE.md
├── REFERENCE.md
├── INTEGRATING.md
├── CHANGELOG.md
├── README.md
├── ROADMAP.md
├── VERSION
└── pyproject.toml
```

**Notes:**

- `themes/` holds one file per variant; each file supplies at least `color_roles` (and optionally reuses borders/bar from tokens or defines them).
- `DESIGNER_SIZING_WORKFLOW.md` at repo root is the tracked checklist you follow; the implementation plan pauses until you finish it.

---

## Recommended tools and libraries

| Current / proposed | Recommendation | Why |
|--------------------|----------------|----|
| PyYAML | **Keep** | Standard for YAML; no need to change. |
| pyfiglet | **Keep (optional)** | Banner render type depends on it; optional extra is correct. |
| Rich | **Keep (optional)** | ANSI output; adapter pattern is good. |
| Textual | **Keep (optional)** | TUI reference consumer; no need to wire every key for v1. |
| Theme variants | **No new lib** | Implement with YAML + existing Loader/Theme; load one theme file or merge theme `color_roles` over base tokens. |
| Output-agnostic | **No new lib** | Document render contract; optional small dataclass (e.g. list of lines + optional style hints) that adapters consume. |

---

## What is not in scope for this plan

- **Full Textual interaction wiring** — Focus/keys/scroll implemented by engines, not required for v1.
- **Batch promotion of ideated → approved** — 24 approved is sufficient; more in the next release.
- **Figma or other design-tool export/sync** — YAML is the source of truth unless you decide otherwise later.
- **New output adapters in v1** — Only “prepare the contract” and, if low effort, a clear render-output abstraction.
- **Migrating every component to adaptive sizing before your input** — Migration continues only after you complete the designer sizing workflow.
- **Any new heavy dependencies** — Keep the system lightweight and extendible.

---

## Output-agnostic prioritization (your Q6)

1. **Document the contract** — In REFERENCE or INTEGRATING, describe what the renderer produces (e.g. list of strings, one per line; optional style hints per line/segment if we add them). So adapter authors know what to expect.
2. **Optional: explicit RenderOutput type** — If it’s a small change, have the renderer (or adapter layer) return a simple dataclass, e.g. `RenderOutput(lines: list[str], styles: list[dict] | None)`, and have Rich/Textual adapters consume that. Then a future HTML adapter just maps `RenderOutput` to HTML. If this would be a large refactor, skip for v1 and stay with “document the current behaviour.”
3. **No HTML/JSON adapters in v1** — Just make the extension point clear so they can be added later without redesign.

---

## Clear plan (to-dos you can check off)

Use this order; the pause is mandatory so your sizing decisions can drive migration.

### 1. Theme system

- [ ] Add `themes/` directory.
- [ ] Add `themes/dark.yaml`, `themes/light.yaml`, `themes/high-contrast.yaml` (grayscale only).
- [ ] Add `themes/experimental.yaml` (current color palette); add a clear “Experimental” label in the file and in docs.
- [ ] Extend Loader and/or Theme so a theme can be loaded by name (e.g. `Loader.load_theme("dark")` or load base tokens + theme overlay).
- [ ] Update CLI to accept `--theme dark|light|high-contrast|experimental` for `preview` and `compose`.
- [ ] Document theme usage in REFERENCE.md and GUIDE.md (how to choose a theme, a11y note for high-contrast).
- [ ] Tests: load each theme, render one component per theme, assert no crash and role resolution works.

### 2. Designer sizing workflow (pause point)

- [ ] Add `DESIGNER_SIZING_WORKFLOW.md` at repo root with:
  - List of components that are still fixed-width (or not yet using `width: fill` / constraints).
  - A simple checklist: for each component (or group), decide: **fill** (adaptive), **content**, or **fixed**; and min/max if applicable.
  - Instructions for you: “Complete this checklist; when done, we use it to migrate.”
- [ ] **Pause:** You complete the workflow (review components, make decisions, optionally fill in the checklist).
- [ ] No implementation to-dos for migration until the pause is done.

### 3. After the pause: adaptive sizing migration

- [ ] Migrate the next batch of components to adaptive sizing according to `DESIGNER_SIZING_WORKFLOW.md`.
- [ ] Prefer `width: fill` + `min_width`/`max_width` where you chose “adaptive”; update snapshots if affected components are approved.
- [ ] Run full test suite and snapshot diff; update CHANGELOG and README if component counts or behaviour change.

### 4. Output-agnostic contract

- [ ] Document in REFERENCE.md or INTEGRATING.md: “What the renderer produces” (line list, optional style hints).
- [ ] If low effort: introduce a small `RenderOutput` (or similar) type and have existing adapters use it; add a short test that renderer (or adapter) returns that type. If high effort, skip and leave “document only” for v1.

### 5. a11y and experimental theme in docs

- [ ] In GUIDE or REFERENCE, add a short “Accessibility and themes” note: high-contrast grayscale for a11y, and that the system is built grayscale-first.
- [ ] Ensure experimental theme is clearly labeled “Experimental” in README/REFERENCE and in `themes/experimental.yaml` (comment or description field).

### 6. Version and release

- [ ] After 1–5 are done: update VERSION and CHANGELOG, consider tagging v1.0.
- [ ] ROADMAP: mark v1 complete and set “What’s next” (e.g. more approved components, more sizing migration, theme polish).

---

## Summary

- **Strategy:** Theme variants (grayscale + experimental), declarative interaction only, designer sizing workflow with a pause, output contract documented (and optionally a small RenderOutput type), 24 approved + ideated visible, YAML as source of truth.
- **Structure:** Add `themes/` and `DESIGNER_SIZING_WORKFLOW.md`; rest stays as is.
- **Tools:** Unchanged; theme variants and contract are implemented with existing stack.
- **Out of scope:** Full Textual wiring, batch promotion, design-tool sync, new adapters in v1.
- **Order:** Theme system → Designer workflow + your pause → Sizing migration → Output contract + a11y/docs → Version/release.

You can follow the plan by checking off the to-dos in order; the only blocking pause is after “Designer sizing workflow” is written and before “adaptive sizing migration” continues.
