# Archived: decorations/

**Moved:** 2026-03-05
**Reason:** Decorative ASCII art is game content, not a design system primitive. The decoration catalog belongs in the game project that consumes AskeeDS.

The `art_lookup` render type in AskeeDS still supports looking up art by ID from any decoration dict passed at runtime — the render capability stays, the data moves out.

**Contents:**
- `catalog.yaml` — 23 named decorations keyed by id (skull, torch, sword, etc.)

**Safe to delete:** When the Askee engine repo has its own decoration catalog, or when you're certain these files aren't needed for reference.
