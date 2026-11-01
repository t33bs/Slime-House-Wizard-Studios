# Slime Wizard — Phase 90: Independent Pose PNG Import + Transparency Modes

**Date:** 2026-10-31  
**Source baseline:** Phase 89  
**GitHub:** untouched

## User-reported bug

Importing `Swordcat_Walk_Pose_1_128.png` into Pose 2 appeared to turn black artwork transparent, and the Asset Library seemed to hide layers from another pose. The actual Swordcat PNG was not available to inspect; screenshots do not reveal RGBA alpha values reliably. This work isolates the two possible semantics rather than guessing or replacing transparent pixels with black.

## What changed

- The compact `Import Pose PNG` button creates a **new exact RGBA pose** by default. This mode preserves all pixels and alpha channels from the imported PNG, including opaque black, fractional-alpha black, and fully transparent black. The importer does **not** borrow black pixels from earlier poses or invent missing details.
- The arrow beside `Import Pose PNG` offers **Build new pose over previous artwork**. This mode first renders the selected saved pose from its snapshot, composites the imported PNG above it, and stores the result as one new independently editable image layer. Transparent PNG pixels reveal earlier artwork. This mode is optional, because it can create ghosts/overlaps when the PNG contains a complete alternate pose.
- Each imported pose gets its own saved layer state and identity. Existing poses' saved snapshots and their asset visibility are never rewritten. The shared source-asset table may still contain hidden inherited states for stable indices; these states are hidden **only in the new pose**. They do not disappear from another saved pose.
- The Asset Library defaults to showing **only visible/editable layers in the current pose**. `Show inactive` reveals the hidden rows for inspection and manual restoration without changing their artwork or affecting other poses.
- Status text shows the import mode and an **opaque-black pixel count in the input PNG**. This allows a real Swordcat file with no opaque black pixels to be distinguished from a broken importer.
- Kept previous Phase 89 timeline reorder behavior and Phase 88 Pose 1-to-infinity combined Slimer workflow, including source erasure and alpha safeguards.

## Automated verification

New headless file: `tests/test_phase90_png_import_modes_model.py` covers:

1. Opaque black stays opaque, transparent black stays transparent, partially transparent black keeps alpha in **exact** mode.
2. Overlay reveals original black through imported transparency and composites alpha correctly, without changing the previous pose.
3. Overlay renders the previous *saved snapshot*, not unrelated current live layer changes.
4. Missing base / invalid mode / size mismatch are rejected before appending a new asset.
5. Exact and overlay imports survive save/reopen and timeline reorder with the right pose IDs, pixels and durations.

Windows GUI file: `tests/test_phase90_import_modes_gui.py` covers:

1. Full `Import Pose PNG` process with black pixel checks, old pose preservation, timeline switching, visible-only library display and `Show inactive` toggle.
2. Full **Build over previous artwork** flow with independent edits and returning to old pose.
3. Uses `isolate_gui_recovery` to block hidden recovery modal hangs, without altering user recovery files.

Local test result (2026-10-31): **502 passed, 39 skipped, 12 subtests passed**; Python compilation passed. PySide6 GUI tests are skipped on this Linux host because PySide6 is unavailable. Actual Windows tests and actual Swordcat file acceptance are pending.

## Windows next steps

Extract the Phase 90 ZIP to a new folder. Open PowerShell there and run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase90_import_modes_gui.py tests/test_phase89_timeline_drag_import_gui.py tests/test_phase88_first_place_frame_gui.py
```

Then launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

Manual acceptance on a **copy of** the Swordcat project:

1. Open saved Pose 1 and note the black pixels and number of visible assets.
2. Click the main **Import Pose PNG** body, select `Swordcat_Walk_Pose_1_128.png`. Pose 2 should show the *exact* PNG with transparent regions preserved; read its opaque-black pixel count in the top status bar. Pose 1 must be unaltered when returning to it.
3. Select Pose 1 again; click the small **arrow** beside Import Pose PNG, choose **Build new pose over previous artwork**, and import the same PNG. The newly created pose should show earlier artwork beneath transparent regions, while Pose 1 is still unchanged.
4. `Show inactive` should reveal old rows in the new pose for inspection and hide them again without changing what the canvas renders.
5. Switch between the poses; check clean previews, saved layers, and PNG export. Optional: drag poses to reorder, then switch again.

If the **exact** import reports zero opaque-black pixels but the original Swordcat PNG visually appears to contain black, inspect the PNG's actual alpha channel by uploading it. The app must not infer or manufacture black RGB opacity.

## Separate issue (not changed)

User reported Slime Cleaner not behaving correctly; exact symptom still unknown. Its brush currently clears only the topmost visible layer and uses unrotated source coordinates, so rotated/overlapping artwork requires a dedicated diagnosis and tests. Do not alter potentially destructive erasure semantics based only on guesses. Keep this item open in `SLIME_WIZARD_BACKLOG.md`.
