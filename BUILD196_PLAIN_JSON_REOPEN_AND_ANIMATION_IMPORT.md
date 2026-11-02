# Build 1.9.6 — Plain JSON Reopen and Animation Import

## Why
Native `*.rig.json` continued to open while some plain `*.json` files did not. There are two independent issues:

1. An older Wizard `placeframe.json` may be a valid version-3 creature with `size`, `parts`, `animations`, IDs and **embedded** original PNG bytes, but have an absent external asset folder. Previously the loader ignored the embedded bytes and rejected the project.
2. `*_sheet.json` and `*_frames.json` are real animation exports with dimensions/timing, but cannot be opened as a native rig. Paired source PNGs contain sufficient pixels to import independent paintable frames, not to reconstruct source rig parts.

## Changes
- Wizard Open Creature now shows all supported `.json` files by default.
- The loader prefers and validates the referenced external PNGs when present. Missing PNGs may be sourced from verified inline `source_png` data without writing anything back to the old JSON or asset folder. It still rejects a missing file without an embedded source; it never silently treats a corrupt external PNG as valid just because an embedded copy exists.
- A standalone, read-only animation importer uses the exact referenced sprite sheet rectangles or listed frame PNGs. Each frame is stored with its own `source_png` on one independent editable full-frame layer. Animation names, timing and canvas size persist. There is no claim of independent limb rigging. Paths are confined to companion PNGs in the same folder; bad coordinates fail atomically.
- Imported animation projects are **unsaved**: the original JSON/PNG isn't the project save destination. Choose Save Creature As and a new `.rig.json` filename.

## Test and manual acceptance
1. Open a legacy `placeframe.json` (with embedded artwork, no sibling assets). Verify every pose, size, timing and unique ID. Save As to `.rig.json`, close and reopen.
2. Open a sprite export `testerfester_sheet.json` with `testerfester_sheet.png` next to it. Confirm 9 frames. Edit frame 5, confirm frames 1–4 and 6–9 remain unchanged. Save As `.rig.json`, reopen, and compare frames.
3. Test missing sprite-sheet PNG. Open must fail without changing other open projects.
4. Confirm original `.rig.json` loading, Slimer/Cleaner, GIF/APNG, export and SHS reference windows still work.
5. Run `python -m pytest tests -q` in Windows GitHub Actions; GUI tests require installed PySide6.

## Scope
Only Wizard's Open Creature path, an isolated import module and embedded-asset fallback are changed. Baseline SHS editor, external `.rig.json` save structure, timeline save semantics, reference viewer, Chameleon, APNG exporter and separate Slime Buddy are unchanged.
