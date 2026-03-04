# AskeeDS

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20the%20project-FF5E5B?style=flat&logo=ko-fi)](https://ko-fi.com/spencerg1350)

AskeeDS is an ASCII-based design system and component library for building terminal UIs (TUIs). It defines how screens, menus, and game elements should look and what data they expect—all in plain text and ASCII art so both humans and tools can use it.

- **Design system overview:** see [design/ascii/README.md](design/ascii/README.md) and [design/ascii/format-spec.md](design/ascii/format-spec.md).
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

> **Note:** The examples below use `python`. On macOS and some Linux setups you may get `zsh: command not found: python`; use `python3` instead (e.g. `python3 tools/render_demo.py`).

- **If you just want to see what this looks like (anyone):**
  - Open `design/ascii/components.txt` side by side with [design/ascii/README.md](design/ascii/README.md).
  - From the repo root run:
    - `python tools/parse_components.py --validate` (quick health check).
    - `python tools/render_demo.py` (prints a few canonical components).
    - **Visual test (optional):** `python tools/component_visual_test.py` — interactive TUI to browse components by status, edit props, and see a live preview. Requires: `pip install textual` or `pip install -e ".[visual-test]"`.
- **If you are a game designer authoring UI or maps:**
  - Browse components in `design/ascii/components.txt` and maps in `design/ascii/maps/`.
  - Make a small edit (for example a new `room-card` variant or a tiny map).
  - Run:
    - `python tools/parse_components.py --validate` to catch common authoring mistakes.
    - `python tools/update_manifest.py` to refresh `design/ascii/manifest.yaml` when you add components.
- **If you are a new developer integrating AskeeDS:**
  - Decide whether you want to **copy the design assets** into your project or use the **experimental Python package/CLI** (see “How to add AskeeDS to an existing project” below).
  - Use `askee-ds-export --kind components` (or `python tools/parse_components.py --json ...`) to generate JSON.
  - Use the parser (see [Scripts and commands (reference)](#scripts-and-commands-reference)) to export JSON and map component props to your runtime’s UI widgets.

---

## Component examples

<!-- COMPONENT_EXAMPLES:START -->

Here are a few examples of the 63+ components from AskeeDS:

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
```

<!-- COMPONENT_EXAMPLES:END -->

## Table of contents

- [Scripts and commands (reference)](#scripts-and-commands-reference)
- [What you get in this repo](#what-you-get-in-this-repo)
- [Getting started (quick start)](#getting-started-quick-start)
- [How to add AskeeDS to an existing project](#how-to-add-askeeds-to-an-existing-project)
  - [Option A — Copy (recommended first)](#option-a--copy-recommended-first)
  - [Option B — Python package / CLI (experimental)](#option-b--python-package--cli-experimental)
  - [Option C — Git submodule / subtree (optional)](#option-c--git-submodule--subtree-optional)
- [Using the parser and overrides](#using-the-parser-and-overrides)
- [Versioning and updates](#versioning-and-updates)
- [Local dev utilities](#local-dev-utilities)
- [Acknowledgments](#acknowledgments)

---

## Scripts and commands (reference)

All commands below are run from the **repo root**. Use this table to find the right script for the job.

> **Reminder:** The examples below use `python`. On macOS and some Linux setups you may get `zsh: command not found: python`; use `python3` instead (e.g. `python3 tools/render_demo.py`).

| Command | What it does | When to use it |
|--------|----------------|--------------------------------|
| `python tools/parse_components.py --validate` [paths...] | Validates the component library (and optional overrides). Exits with errors if meta is invalid, ␟ in art, or Deprecated without replaced-by. | After editing `components.txt` or overrides; before committing; in CI. |
| `python tools/parse_components.py --json` [paths...] | Outputs merged components as JSON to stdout (name, meta, art). | When you need machine-readable component data for an engine or tool. |
| `python tools/render_demo.py` | Prints a few canonical components (status-bar, room-card, layout.stack) as ASCII to the terminal. | Quick visual check that the library loads and looks right. |
| `python tools/component_visual_test.py` | **Interactive TUI:** browse components by status, open one, edit and randomize props, see live preview. No persistence. | Manual QA: review components by status, test how props affect layout. **Requires:** `pip install textual` or `pip install -e ".[visual-test]"`. |
| `python tools/update_manifest.py` | Regenerates `design/ascii/manifest.yaml` from `components.txt` (sorted list of component names). | After adding or renaming components so tooling and tests stay in sync. |
| `python tools/update_readme_examples.py` | Refreshes the “Component examples” block in this README from a curated list. | After adding or changing components you want highlighted in the README. |
| `python tools/parse_decorations.py --validate` [paths...] | Validates the decoration catalog (e.g. `decoration-catalog.txt`). | After editing decorative ASCII art entries. |
| `python tools/parse_decorations.py --json` [paths...] | Outputs decorations as JSON. | When you need the decoration catalog in machine form. |
| `python tools/parse_maps.py --validate` | Validates ASCII maps in `design/ascii/maps/` (known tiles, rectangular, line length). | After editing maps or map index. |
| `python tools/parse_maps.py --json` | Outputs map definitions and grid data as JSON. | When you need map data for an engine or preview tool. |
| `python tools/test_parse_components.py` | Runs unit tests for the component parser and validator. | After changing `parse_components.py` or component format. |
| `python tools/test_parse_decorations.py` | Runs unit tests for the decoration parser. | After changing decoration parsing. |
| `python tools/test_parse_maps.py` | Runs unit tests for the map parser. | After changing map parsing. |
| `askee-ds-validate` [--kind components\|decorations\|maps\|all] | Package CLI: validates components, decorations, and/or maps (same rules as the tools above). | When the package is installed and you prefer a single command. |
| `askee-ds-export` [--kind components\|decorations\|maps] [--list] | Package CLI: exports assets as JSON; with `--kind components --list`, prints component names (and descriptions). | When the package is installed and you want JSON or a name list. |
| `askee-ds-demo` [-c name] [--prefix p] | Package CLI: prints sample components as ASCII (default or by name/prefix). | When the package is installed; like `render_demo.py` with more options. |
| `npm run update:manifest` | Same as `python tools/update_manifest.py`. | If you prefer npm for repo tasks. |
| `npm run update:readme-examples` | Same as `python tools/update_readme_examples.py`. | If you prefer npm for repo tasks. |
| `npm run test` | Runs `python3 -m unittest discover -s tools`. | Run all tests under `tools/`. |

**Notes:**

- **Paths:** For `parse_components.py` and `parse_decorations.py`, if you omit paths, the default is the canonical file in `design/ascii/` (e.g. `components.txt`). Pass multiple files to merge core + overrides.
- **Package CLIs:** `askee-ds-validate`, `askee-ds-export`, and `askee-ds-demo` are available after `pip install -e .`; they use the same logic as the scripts under `tools/`.

---

## What you get in this repo

- `design/ascii/` — ASCII design system source of truth:
  - `components.txt` — all components, their meta (description, props, shapes), and ASCII sketches.
  - `box-drawing.yaml` — approved border characters.
  - `map-tiles.yaml` — minimap / grid tile roles.
  - `manifest.yaml` — list of component names.
  - `README.md`, `format-spec.md` — how to parse and extend the system.
- `tools/parse_components.py` — parser/validator and JSON export CLI.
- `tools/render_demo.py` — minimal reference renderer (prints a few components to stdout).
- `tools/component_visual_test.py` — interactive TUI to visually test components by status, edit prop values, and see a live preview (requires Textual: `pip install textual` or `pip install -e ".[visual-test]"`).
- `tools/test_parse_components.py` and additional tests/parsers under `tools/` — tests for the parser and related utilities.

---

## Getting started (quick start)

**If you just want to explore AskeeDS in this repo:**

1. From the repo root, validate the component library:
   - `python tools/parse_components.py --validate`
2. Render a small demo of a few components:
   - `python tools/render_demo.py`
3. Open [design/ascii/components.txt](design/ascii/components.txt) and [design/ascii/README.md](design/ascii/README.md) to see the components and their docs.

> **Make something weird and wonderful.** AskeeDS is meant to be copied, bent, and remixed—build strange worlds, kind TUIs, tiny tools, or full games. If you ship something you’re proud of, consider sharing a short write-up or screenshot and crediting AskeeDS so others can discover it too.

**If you want to use AskeeDS in *another* project (copy-based install):**

1. Clone this repo (or download it as a ZIP):
   - `git clone <this-repo-url>`
2. In your target project, copy the **design assets**:
   - `design/ascii/` (all files)
3. Optionally also copy **tooling**:
   - `tools/parse_components.py`, `tools/render_demo.py`, `tools/test_parse_components.py`
4. In your project, treat [design/ascii/components.txt](design/ascii/components.txt) as the **core upstream file**, and put any project-specific components or overrides in a separate file (for example `design/ascii/overrides.txt`).
5. Use the parser in your project to validate or export the merged components (see [Using the parser and overrides](#using-the-parser-and-overrides)).

For versioning and update strategy, see the [Versioning and updates](#versioning-and-updates) section below and [CHANGELOG.md](CHANGELOG.md).

---

## How to add AskeeDS to an existing project

AskeeDS is designed to be easy to **copy into any project**. There are three main adoption patterns.

### Option A — Copy (recommended first)

Copy the design-system bundle from this repo into your project.

- Copy **design assets**:
  - `design/ascii/` (all files)
- Optionally also copy **tooling**:
  - `tools/parse_components.py`, `tools/render_demo.py`, `tools/test_parse_components.py`

Then, in your project:

- Treat [design/ascii/components.txt](design/ascii/components.txt) as the **core, upstream file** (read-only from your perspective).
- Put any project-specific components or overrides in a separate file (for example `design/ascii/overrides.txt`).
- When using the parser, pass both files (core first, overrides second) so overrides win for duplicate names (see [Using the parser and overrides](#using-the-parser-and-overrides)).

### Option B — Python package / CLI (experimental)

This repo now includes a minimal `pyproject.toml` and an **experimental** `askee_ds` package with simple CLIs (`askee-ds-validate`, `askee-ds-export`, `askee-ds-demo`). These are provided **as a convenience only**:

- The **source of truth** for the design system remains the copyable bundle under `design/ascii/`.
- The package/CLI layer is intended for teams already using Python who want quick validation or JSON export without wiring the scripts themselves.
- Public packaging, distribution, and version guarantees for the Python layer may change; do not treat it as a stable, hard dependency the way you treat the ASCII assets.

If you’re unsure which option to choose, start with **Option A (copy)** and consider the Python tools as an optional helper.

### Option C — Git submodule / subtree (optional)

If you prefer vendoring via Git:

- Add this repo as a submodule (for example under `vendor/askee-ds/`) and pin to a tag.
- Point your tools or build scripts at the design assets in that folder.
- When a new version is published, update the submodule to the new tag and follow the changelog in [CHANGELOG.md](CHANGELOG.md).

For versioning and update strategy, see the [Versioning and updates](#versioning-and-updates) section above and [CHANGELOG.md](CHANGELOG.md).

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
  - **PATCH:** Non-breaking fixes, clarifications, documentation and tooling only.
- **Changelog:** See [CHANGELOG.md](CHANGELOG.md) for what changed in each release and migration notes when a breaking change occurs.
- **Layering:** To keep updates safe, treat core files (especially [design/ascii/components.txt](design/ascii/components.txt)) as upstream, and put your changes in overrides. When you update AskeeDS (via copy, package, or submodule), keep your overrides file and follow the changelog for any renames.

With this model, you can stay on a specific version (for example `0.1.x`) or move to a newer version when you're ready, without losing customizations.

---

## Local dev utilities

For a **full list of scripts and when to use each**, see [Scripts and commands (reference)](#scripts-and-commands-reference) above.

When you edit [design/ascii/components.txt](design/ascii/components.txt) or add components/overrides, run at least: `python tools/parse_components.py --validate` and, after adding names, `python tools/update_manifest.py`. Use the visual test and parser tests as needed for QA.

---

## Acknowledgments

This README’s structure was inspired by [Best README Template](https://github.com/othneildrew/Best-README-Template).

