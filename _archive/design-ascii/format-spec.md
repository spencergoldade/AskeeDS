# AskeeDS component library — format spec

Machine-readable grammar for the component library file (e.g. `design/ascii/components.txt`). Delimiter: **U+241F** (SYMBOL FOR UNIT SEPARATOR), shown as ␟.

## Grammar

- **Component boundary:** A line that starts with exactly three U+241F characters, then the literal `COMPONENT: ` (with trailing space), then the component name. The component name is the rest of the line (trimmed). No leading/trailing spaces in the name.
- **Meta line:** A line that starts with exactly one U+241F character, then a key (identifier or word), then the literal `: ` (colon + space), then the value. The value is the rest of the line (trimmed). Keys are case-sensitive (e.g. `description`, `props`).
- **ASCII art block:** Consecutive lines that are not a component boundary and not a meta line. This is the component's structural sketch. May be empty. Ends at the next component boundary, at a **section header** line (a line that starts with `---------- ` and ends with `----------`), or at end of file.

## Parsing algorithm

1. Split the file into lines (preserve line endings for art if needed; for structure, line-by-line is enough).
2. Scan for the delimiter character (U+241F). Count leading delimiters on each line.
3. If a line starts with `␟␟␟` and then `COMPONENT: `, begin a new component. Record the name (rest of line after `COMPONENT: `, trimmed).
4. Subsequent lines starting with exactly one `␟` are meta: parse key and value (after the first `␟`, take up to first `: ` as key, rest as value).
5. After the meta block (first line that is not component-boundary and not meta), treat all following lines as the ASCII art block. Stop when you reach the next `␟␟␟ COMPONENT: ` line or a section-header line (starts with `---------- ` and ends with `----------`). Store the art as a string (lines joined by newline) or list of lines.
6. Repeat until EOF.

## Multiple files and overrides

- Canonical location: the shared library lives at `design/ascii/components.txt`.
- Overrides: projects may add one or more additional files (for example
  `components.overrides.txt`) and pass both paths to the parser/CLI; later
  files **override earlier ones by component name**.
- Future modularization: if the library is ever split, recommended names are:
  - `components.core.txt` — core layout and structural components
  - `components.game.txt` — game- and RPG-focused components
  - `components.maps.txt` — map/minimap-related components
- Tooling:
  - The Python CLI (`tools/parse_components.py`) already accepts multiple paths
    and merges them in order.
  - JSON exports should reflect the merged view, not individual source files.

## Constraints (validation)

- **No ␟ in art:** The ASCII art block must not contain the character U+241F. Parsers may reject or warn if found.
- **Max line length:** Recommended max 80 characters per line (warning only; not enforced by format).
- **Required meta:** Each component should have at least `description` and `props` (or explicit "none") for authoring; validators may warn if missing.
- **Component status:** Each component should have `component-status` with one of: `Ideated`, `To Do`, `In Progress`, `In Review`, `Approved`, `Cancelled`, `Deprecated`. Validators may warn if missing. When `component-status` is `Deprecated`, `replaced-by` must be present and non-empty (validators should error if not).
- **Component names:** Use dot notation `category.variant`; no spaces. Must match manifest if present.
- **Standard optional prop — color:** Every component may list an optional prop `color_role_optional` (or equivalent). When present, it is a semantic role id (e.g. `status.good`, `ui.accent`) that the implementation maps to its own color tokens. When absent, the implementation uses the component's `color-hint` default(s) or theme. Semantics are implementation-defined but should map to project tokens.

## Example (minimal)

```
␟␟␟ COMPONENT: button.text
␟ description: Text-only button
␟ component-status: In Review
␟ props: label
[ Submit ]
```

Parsed as: name `button.text`, meta `{ "description": "Text-only button", "component-status": "In Review", "props": "label" }`, art (one line) `"[ Submit ]"`.

## Export (JSON)

A parser may output a structure like:

```json
{
  "components": [
    {
      "name": "button.text",
      "meta": { "description": "...", "component-status": "In Review", "props": "label", "interactive": "true" },
      "art": "[ Submit ]\n"
    }
  ]
}
```

Keys in `meta` are strings; values are strings. Duplicate keys (e.g. multiple `color-hint`) may be combined as array or last-wins per implementation.
