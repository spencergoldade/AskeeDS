# Archived: retired tools

## What these were

CLI tools and scripts that operated on the old U+241F component format or
were one-time migration utilities. They are no longer needed for day-to-day
work.

| File | Purpose |
|------|---------|
| **component_visual_test.py** | 2317-line Textual TUI for interactive component preview, status management, and prop randomization. Operated on `components.txt`. |
| **component_visual_test.tcss** | Textual CSS stylesheet for the visual test TUI. |
| **test_component_visual_test.py** | Unit tests for the visual test TUI. |
| **migrate.py** | One-time migration tool that converted `components.txt` (U+241F format) to the YAML files under `components/`. Supports dry run, preview, and write modes. |
| **add_component_status.py** | One-off script that added `status:` metadata to components in the old format. |
| **merge_intent_into_components.py** | One-off script that merged intent metadata into component definitions. |
| **update_manifest.py** | Synced `manifest.yaml` with component names in `components.txt`. The manifest is no longer needed (directory structure replaces it). |
| **update_readme_examples.py** | Regenerated README example output from rendered components. Will be rewritten for the new format when the README is rewritten. |
| **figlet_approved_fonts.txt** | List of approved Figlet fonts. Now captured in `tokens/typography.yaml`. |

## Why they were archived

These tools served the old U+241F format workflow or were one-time migration
scripts. Their responsibilities are now covered by:

| Old tool | Replaced by |
|----------|-------------|
| component_visual_test.py | `askee-ds preview <name>` CLI command (renders any component with props) |
| migrate.py | Migration complete; all 63 components are in YAML |
| add_component_status.py | Status is a first-class field in the YAML schema |
| merge_intent_into_components.py | Intent is part of each component's YAML definition |
| update_manifest.py | No manifest needed; `askee-ds list` discovers components from the directory |
| update_readme_examples.py | Will be rebuilt for the new format during README rewrite |

## Tools NOT archived (still in tools/)

- **parse_components.py** — Legacy component parser CLI. Still used by old
  CI steps and delegates to `askee_ds.components`. Will be retired when CI
  fully switches to the new YAML pipeline.
- **parse_decorations.py** — Decoration parser CLI. Decorations have not
  been migrated yet.
- **parse_maps.py** — Map parser CLI. Maps have not been migrated yet.
- **render_demo.py** — Minimal reference renderer. Still functional.
- **test_parse_components.py** — Parser tests for the old format.
- **test_parse_decorations.py** — Decoration parser tests.
- **test_parse_maps.py** — Map parser tests.

## When it is safe to delete this folder

This archive can be deleted when:

1. You no longer need the migration tool as a reference for how the
   conversion was done.
2. The visual test TUI is not being used as a reference for a replacement
   tool.
3. No one needs these scripts for debugging or understanding the old format.

In practice, once the README rewrite (Phase 7) is complete and you are
confident the old format is fully behind you, this folder can go.
