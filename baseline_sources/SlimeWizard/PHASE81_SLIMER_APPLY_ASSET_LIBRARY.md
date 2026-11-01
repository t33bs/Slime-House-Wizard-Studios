# Slime Wizard — Phase 81 Slimer source erase & Asset Library I/O

2026-10-30

## Windows reports addressed

1. Apply Move sometimes showed "Source erase failed; original pixels restored. Move not applied."
2. Edit Selection sometimes would not advance from highlighting until the tool was reset.
3. Asset Library had only Remove/Restore, no local Import Asset and Export for SHS actions.

## Root cause found and fix

The Phase 80 `slimer_apply_move_to_pose` excluded its provisional destination from source preflight, then restored visibility before `_slimer_erase_original_layers`. This allowed the provisional destination to be wrongly recognized as a source of selected original pixels, especially on overlapping or no-displacement moves. A verified headless reproduction showed that when moved zero pixels the new layer could erase itself, leaving the underlying source untouched; when moved a little, some destination pixels could be cleared.

Phase 81 makes `_slimer_erase_original_layers` temporarily hide the exact pending destination by object identity for the **entire erase transaction**, including every source-mapping path. It restores provisional visibility in `finally` even if the source erase raises an error. Apply Move retains its existing source snapshots, safe preflight, and rollback of images, undo/redo, and dirty state. If source erasure still fails for a different reason, the existing status now also includes the exception message to aid diagnosis. No unsafe fallbacks were added.

## Asset Library

- Added **Import Asset** and **Export for SHS** buttons directly below the Asset Library list. The original top-toolbar Import PNG assets action remains.
- Import uses the existing PNG import workflow and nearest-neighbor scaling only when requested; imported asset remains independently editable.
- Export saves the selected asset's native RGBA PNG source (pose-local source where applicable) for editing in Slime House Studios. It does **not** bake canvas position/rotation, overlays or tools into the image. This is file export, not a direct launch or live synchronization with SHS.
- Import and Export refuse to operate while an unfinished Slimer move is staged, preventing source/index confusion. Importing while Slimer is actively highlighting resets the stale highlight snapshot so the user can start a fresh selection without deactivating the tool.

## Edit Selection clarity

With an active Slimer highlighter and no pixels selected, Edit Selection shows an explicit "Nothing highlighted yet" instruction instead of silently turning on handles for an unrelated library layer. Existing-layer handle toggling remains available when not in highlight mode. The one-button Highlight → Edit Selection → Transform → Apply Move workflow remains unchanged; **Finish Selecting stays removed**.

## Verification

Full local Qt-free suite: **475 passed, 29 skipped, 12 subtests passed** (final verification when packaging; PySide6 is unavailable in this environment). All previous source tests retained, with new tests:

- `tests/test_phase81_move_original_staged_exclusion.py`
- `tests/test_phase81_asset_io_headless.py`
- `tests/test_phase81_asset_library_io_gui.py`
- `tests/test_phase81_overlapping_move_gui.py`

On Windows with the user's existing PySide6 venv, from extracted `SlimeWizard81` folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase81_asset_library_io_gui.py tests/test_phase81_overlapping_move_gui.py tests/test_phase80_clean_preview_buffer_gui.py
```

Then perform the **real Swordcat leg** acceptance check: highlight a leg; Edit Selection creates a staged layer; drag it only 1-2 pixels so source and destination overlap; Apply Move with Move Original ON; verify only selected source pixels clear and staged destination remains intact. Retry Rotate mode and Copy Pixels separately. If the source erase still fails on real artwork, preserve the staged edit and report the exact new reason shown in status.

Do not modify GitHub until a verified full Windows pass and user authorization.
