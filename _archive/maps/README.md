# Archived: maps/

**Moved:** 2026-03-05
**Reason:** Maps are game content, not design system primitives. They belong in the game project (Askee engine) that consumes AskeeDS, not in the design system itself.

The `charmap` render type in AskeeDS still supports rendering any 2D character grid passed as props — the render capability stays, the data moves out.

**Contents:**
- `tiles.yaml` — tileset definitions (chars to tile roles)
- `index.yaml` — map index with metadata
- `dungeon_room.txt` — example dungeon room layout
- `world_overworld.txt` — example overworld layout

**Safe to delete:** When the Askee engine repo has its own map data, or when you're certain these files aren't needed for reference.
