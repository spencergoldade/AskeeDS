# Stakeholder requests (engine team)

Running list of requests and feedback from the Askee engine team. Sync with them periodically; move completed items to **Implemented** or remove.

Engine-side work that depends on these requests is tracked in their repo (e.g. ROADMAP, backlog). Keep this file and ROADMAP/BACKLOG in sync when adding or completing engine-dependent work.

**How to use:** Add one line per request with a short title and optional detail. When negotiating with the engine team, copy this list or link this file.

---

## Open

- **Mod theming / component extension** — Mods (adventures) should be able to override or extend theme and/or components; AskeeDS has agreed to support. Document the intended contract (e.g. per-adventure theme file or component set) so the engine can plan.
- **hint-bar.contextual** — (Optional.) Component or API for a contextual hint line so the engine can replace or augment the minimal HintBar with AskeeDS-driven hints (e.g. context-sensitive commands). See ROADMAP: stakeholder request; BACKLOG.
- **Screen YAML / composer** — (Optional.) Ability to compose the main game view from a screen definition (e.g. `adventure_main.yaml`) for layout-as-data. **Status:** AskeeDS already provides `Composer`, `askee-ds compose`, and 17 example screens under `screens/`. If the engine needs additional contract or features, specify and we can add to BACKLOG.

---

## Implemented / closed

- **Python 3.12+** — AskeeDS targets Python 3.12+. Done.
- **Screen composition from YAML** — Composer and screen YAML exist; 17 example screens. Done.

---

## Workflow recommendations (from engine team)

Suggestions so both teams can work optimally (single source of truth, clear priorities) and avoid wasted effort (no dead references, no duplicate plans, minimal irrelevant guidance).

- **Fix broken or stale references** — If a design or workflow doc was deleted or renamed, update every doc that points at it (e.g. README “Docs” tables, any local workflow docs). Point them at the current file. Dead references confuse tooling and humans.
- **One place for actionable work** — Use ROADMAP.md and BACKLOG.md at repo root. Before starting work, check both; when adding work, put it there; when finishing, mark done and add to CHANGELOG when pushed. That way work is not duplicated or invented ad hoc.
- **Severity on backlog** — Use a simple severity (e.g. High / Medium / Low) on open items and order backlog by severity so “do the most severe first” is explicit.
- **Real file paths in guidance** — In rules or docs that reference design or specs, use real paths (e.g. `ROADMAP.md`, `BACKLOG.md`, `design/…`) instead of vague “follow existing pattern” or “see the spec.” That way the right file can be opened directly.
- **Always-on vs requestable** — Make it explicit which guidance is always applied and which is “use when…” (e.g. by category or description). Reduces irrelevant load when the task does not need it.
- **Cross-reference, don’t duplicate** — Link to the canonical doc (e.g. REFERENCE.md, content spec) rather than copying long blocks. One source of truth keeps answers consistent.

If the engine team shares their workflow rule text or severity legend, we can align wording and structure.
