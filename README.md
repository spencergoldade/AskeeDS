# AskeeDS

AskeeDS is an ASCII-based design system and component library for building terminal UIs (TUIs). It defines how screens, menus, and game elements should look and what data they expect—all in plain text and ASCII art so both humans and tools can use it.

- **Design system overview:** see [docs/ascii-design-system.md](docs/ascii-design-system.md).
- **Component library (canonical):** [design/ascii/components.txt](design/ascii/components.txt) (plus [design/ascii/README.md](design/ascii/README.md) and [design/ascii/format-spec.md](design/ascii/format-spec.md)).
- **Current version:** `0.1.0` (see [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md)).

---

## Table of contents

- [What you get in this repo](#what-you-get-in-this-repo)
- [Getting started (quick start)](#getting-started-quick-start)
- [How to add AskeeDS to an existing project](#how-to-add-askeeds-to-an-existing-project)
  - [Option A — Copy (recommended first)](#option-a--copy-recommended-first)
  - [Option B — Python package (future)](#option-b--python-package-future)
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
- `tools/test_parse_components.py` — tests for the parser.

---

## Getting started (quick start)

**If you just want to explore AskeeDS in this repo:**

1. From the repo root, validate the component library:
   - `python tools/parse_components.py --validate`
2. Render a small demo of a few components:
   - `python tools/render_demo.py`
3. Open [design/ascii/components.txt](design/ascii/components.txt) and [docs/ascii-design-system.md](docs/ascii-design-system.md) to see the components and their docs.

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

### Option B — Python package (future)

A future `askee-ds` Python package can ship the same bundle as **package data**, expose the parser as a CLI/API, and optionally provide an `askee-ds init` command to unpack the assets into your project. Until that exists, use **Option A (copy)**.

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

These are optional but recommended when you edit [design/ascii/components.txt](design/ascii/components.txt) or add new components/overrides.
