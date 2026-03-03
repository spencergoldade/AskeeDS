# AskeeDS

AskeeDS is an ASCII-based design system and component library for building terminal UIs (TUIs). It defines how screens, menus, and game elements should look and what data they expect—all in plain text and ASCII art so both humans and tools can use it.

- **Design system overview:** see [docs/ascii-design-system.md](docs/ascii-design-system.md).
- **Component library (canonical):** [design/ascii/components.txt](design/ascii/components.txt) (plus [design/ascii/README.md](design/ascii/README.md) and [design/ascii/format-spec.md](design/ascii/format-spec.md)).
- **Current version:** `0.1.0` (see [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md)).

---

## Who is this for?

- **Game designers (authoring):** You sketch screens, menus, and worlds in plain text and want a consistent visual language that engines can consume.
- **New developers (engine integration):** You wire AskeeDS assets into a game, tool, or TUI framework and need clear contracts and examples.
- **Tooling maintainers:** You build validation, export, or preview tools on top of the AskeeDS files and CLIs.

You can use the repo as **copyable design assets**, an **experimental Python package/CLI**, or both.

---

## What do I do first?

- **If you just want to see what this looks like (anyone):**
  - Open `design/ascii/components.txt` side by side with [docs/ascii-design-system.md](docs/ascii-design-system.md).
  - From the repo root run:
    - `python tools/parse_components.py --validate` (quick health check).
    - `python tools/render_demo.py` (prints a few canonical components).
- **If you are a game designer authoring UI or maps:**
  - Browse components in `design/ascii/components.txt` and maps in `design/ascii/maps/`.
  - Make a small edit (for example a new `room-card` variant or a tiny map).
  - Run:
    - `python tools/parse_components.py --validate` to catch common authoring mistakes.
    - `python tools/update_manifest.py` to refresh `design/ascii/manifest.yaml` when you add components.
- **If you are a new developer integrating AskeeDS:**
  - Decide whether you want to **copy the design assets** into your project or use the **experimental Python package/CLI** (see “How to add AskeeDS to an existing project” below).
  - Use `askee-ds-export --kind components` (or `python tools/parse_components.py --json ...`) to generate JSON.
  - Follow the patterns in [docs/implementation-notes.md](docs/implementation-notes.md) to map component props to your runtime’s UI widgets.

---

## Component examples

<!-- COMPONENT_EXAMPLES:START -->

Here are a few example components from AskeeDS:

- **`panel.consequence`** · Templates — Panel listing lasting body and mental consequences with severities.

```text

+------------------------------------------+
| Consequences                             |
+------------------------------------------+
| Body:                                    |
|  - Scarred arm (mild)                    |
|  - Broken rib (severe)                   |
| Mental:                                  |
|  - Nightmares (moderate)                 |
|  - Shaken faith (mild)                   |
+------------------------------------------+

---------- Game — quick-select ----------
```

- **`screen.crafting`** · Templates — Crafting workbench screen with input slots, output preview, and resource costs.

```text

+------------------------------------------+
|           Crafting bench                 |
+------------------------------------------+
| Inputs:                                  |
|  [ herb ]  [ bottle ]                    |
|                                          |
| Output: healing potion                   |
| Chance: 75%                              |
|                                          |
| Costs: mana 5, time 1h                   |
+------------------------------------------+
```

- **`layout.stack`** · Templates — Stacked full-width blocks (e.g. status + main + input).

```text

+------------------------------------------------+
| block 1 (e.g. status bar)                      |
+------------------------------------------------+
| block 2 (main content)                         |
|                                                |
+------------------------------------------------+
| block 3 (input)                                |
+------------------------------------------------+

---------- Patterns (structural) ----------
```

<!-- COMPONENT_EXAMPLES:END -->

## Table of contents

- [What you get in this repo](#what-you-get-in-this-repo)
- [Getting started (quick start)](#getting-started-quick-start)
- [How to add AskeeDS to an existing project](#how-to-add-askeeds-to-an-existing-project)
  - [Option A — Copy (recommended first)](#option-a--copy-recommended-first)
  - [Option B — Python package / CLI (experimental)](#option-b--python-package--cli-experimental)
  - [Option C — Git submodule / subtree (optional)](#option-c--git-submodule--subtree-optional)
- [Using the parser and overrides](#using-the-parser-and-overrides)
- [Versioning and updates](#versioning-and-updates)
- [Local dev utilities](#local-dev-utilities)

---

## What you get in this repo

- `design/ascii/` — ASCII design system source of truth:
  - `components.txt` — all components, their meta (description, props, shapes), and ASCII sketches.
  - `box-drawing.yaml` — approved border characters.
  - `map-tiles.yaml` — minimap / grid tile roles.
  - `manifest.yaml` — list of component names.
  - `README.md`, `format-spec.md` — how to parse and extend the system.
- `design/tokens/colors.md` — TUI semantic color tokens (status bands, UI, entity, feedback).
- `docs/ascii-design-system.md` — narrative overview, features, groups, and constraints.
- `docs/ascii-reference.txt` — ASCII code points and the AskeeDS delimiter (U+241F, ␟).
- `docs/adoption-and-updates-plan.md` — detailed plan for adoption, versioning, and updates.
- `tools/parse_components.py` — parser/validator and JSON export CLI.
- `tools/render_demo.py` — minimal reference renderer (prints a few components to stdout).
- `tools/test_parse_components.py` and additional tests/parsers under `tools/` — tests for the parser and related utilities.
> **Note:** The Python tooling and package metadata in this repo are **experimental helpers**. The primary deliverable is the design-system bundle itself (`design/` + key docs). You should treat the Python code as a convenience layer, not a required integration path.

---

## Getting started (quick start)

**If you just want to explore AskeeDS in this repo:**

1. From the repo root, validate the component library:
   - `python tools/parse_components.py --validate`
2. Render a small demo of a few components:
   - `python tools/render_demo.py`
3. Open [design/ascii/components.txt](design/ascii/components.txt) and [docs/ascii-design-system.md](docs/ascii-design-system.md) to see the components and their docs.

> **Make something weird and wonderful.** AskeeDS is meant to be copied, bent, and remixed—build strange worlds, kind TUIs, tiny tools, or full games. If you ship something you’re proud of, consider sharing a short write-up or screenshot and crediting AskeeDS so others can discover it too.

**If you want to use AskeeDS in *another* project (copy-based install):**

1. Clone this repo (or download it as a ZIP):
   - `git clone <this-repo-url>`
2. In your target project, copy the **design assets**:
   - `design/ascii/` (all files)
   - `design/tokens/colors.md`
   - `docs/ascii-design-system.md`
   - `docs/ascii-reference.txt`
3. Optionally also copy **tooling**:
   - `tools/parse_components.py`, `tools/render_demo.py`, `tools/test_parse_components.py`
4. In your project, treat [design/ascii/components.txt](design/ascii/components.txt) as the **core upstream file**, and put any project-specific components or overrides in a separate file (for example `design/ascii/overrides.txt`).
5. Use the parser in your project to validate or export the merged components (see [Using the parser and overrides](#using-the-parser-and-overrides)).

For more detailed guidance and trade-offs (package vs copy vs submodule), see [docs/adoption-and-updates-plan.md](docs/adoption-and-updates-plan.md).

---

## How to add AskeeDS to an existing project

AskeeDS is designed to be easy to **copy into any project**. There are three main adoption patterns.

### Option A — Copy (recommended first)

Copy the design-system bundle from this repo into your project.

- Copy **design assets**:
  - `design/ascii/` (all files)
  - `design/tokens/colors.md`
  - `docs/ascii-design-system.md`
  - `docs/ascii-reference.txt`
- Optionally also copy **tooling**:
  - `tools/parse_components.py`, `tools/render_demo.py`, `tools/test_parse_components.py`

Then, in your project:

- Treat [design/ascii/components.txt](design/ascii/components.txt) as the **core, upstream file** (read-only from your perspective).
- Put any project-specific components or overrides in a separate file (for example `design/ascii/overrides.txt`).
- When using the parser, pass both files (core first, overrides second) so overrides win for duplicate names (see [Using the parser and overrides](#using-the-parser-and-overrides)).

### Option B — Python package / CLI (experimental)

This repo now includes a minimal `pyproject.toml` and an **experimental** `askee_ds` package with simple CLIs (`askee-ds-validate`, `askee-ds-export`, `askee-ds-demo`). These are provided **as a convenience only**:

- The **source of truth** for the design system remains the copyable bundle under `design/` plus the key docs in `docs/`.
- The package/CLI layer is intended for teams already using Python who want quick validation or JSON export without wiring the scripts themselves.
- Public packaging, distribution, and version guarantees for the Python layer may change; do not treat it as a stable, hard dependency the way you treat the ASCII assets.

If you’re unsure which option to choose, start with **Option A (copy)** and consider the Python tools as an optional helper.

### Option C — Git submodule / subtree (optional)

If you prefer vendoring via Git:

- Add this repo as a submodule (for example under `vendor/askee-ds/`) and pin to a tag.
- Point your tools or build scripts at the design assets in that folder.
- When a new version is published, update the submodule to the new tag and follow the changelog in [CHANGELOG.md](CHANGELOG.md).

For more detail on all options and trade-offs, see [docs/adoption-and-updates-plan.md](docs/adoption-and-updates-plan.md).

---

## Using the parser and overrides

The parser CLI supports **one or more component files**, merged in order (later files override earlier ones by component name):

```bash
# Validate the core library only
python tools/parse_components.py --validate design/ascii/components.txt

# Validate core + project-specific overrides
python tools/parse_components.py --validate design/ascii/components.txt design/ascii/overrides.txt

# Export merged components as JSON
python tools/parse_components.py --json design/ascii/components.txt design/ascii/overrides.txt > components.json
```

In code, you can import `parse_components` from [tools/parse_components.py](tools/parse_components.py) and load/merge files however your runtime prefers.

To keep the component manifest in sync with the library, you can regenerate `design/ascii/manifest.yaml` directly from `components.txt`:

```bash
# Regenerate manifest from components.txt
python3 tools/update_manifest.py
# or via npm
npm run update:manifest
```

---

## Versioning and updates

- **Versioning:** AskeeDS follows semantic versioning (`MAJOR.MINOR.PATCH`) recorded in [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md).
  - **MAJOR:** Breaking changes (rename/remove component, rename/remove required prop, format changes).
  - **MINOR:** Additive (new components, new optional props, new tokens).
  - **PATCH:** Non-breaking fixes, clarifications, docs/tooling only.
- **Changelog:** See [CHANGELOG.md](CHANGELOG.md) for what changed in each release and migration notes when a breaking change occurs.
- **Layering:** To keep updates safe, treat core files (especially [design/ascii/components.txt](design/ascii/components.txt)) as upstream, and put your changes in overrides. When you update AskeeDS (via copy, package, or submodule), keep your overrides file and follow the changelog for any renames.

With this model, you can stay on a specific version (for example `0.1.x`) or move to a newer version when you're ready, without losing customizations.

---

## Local dev utilities

- **Validate components:** `python tools/parse_components.py --validate`
- **Render a demo:** `python tools/render_demo.py`
- **Run parser tests:** `python tools/test_parse_components.py`
- **Refresh README examples:** `python3 tools/update_readme_examples.py` (or `npm run update:readme-examples`)

These are optional but recommended when you edit [design/ascii/components.txt](design/ascii/components.txt) or add new components/overrides.
