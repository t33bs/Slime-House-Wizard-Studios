# Slime Wizard — Phase 82: consecutive Slimer, direct imported placement, and SHS export

2026-10-30

## User findings from Phase 81

- First `Highlight -> Edit Selection -> Apply Move` succeeded on real Swordcat leg, with Move Original correctly erasing only original pixels.
- A second highlight/edit attempt in the same pose sometimes failed to proceed until the Slimer tool was reset.
- Transform handles did not reliably disappear after Apply Move.
- `Edit Selection` did not let a freshly imported Asset Library asset enter placement editing without painting another highlight.
- `Export for SHS` saved an apparently empty/useless file even after setting the SHS executable location.

## Changes in Phase 82

1. `Edit Selection` handles two cases without extra buttons: a nonempty painted Slimer highlight creates a new editable layer, while an empty selection with a selected nonempty Asset Library asset opens placement controls on that **existing** layer. No duplicate asset or frame is created.
2. Applying placement for an existing asset cleanly turns off its handles, refreshes the canvas, and returns to Slimer highlighting. This does not run Move Original source erasure because no new source pixels were selected.
3. The first new Slimer highlight stroke rebases an **empty** selection to the current artwork, preventing stale previous-pose/previous-move render references. Nonempty selections are never silently rebased, preserving stale-source safety.
4. `Export for SHS` saves **selected asset pixels**, not an apparently blank full-canvas PNG. Ordinary untransformed small imported PNGs preserve original pixel dimensions/padding. Full-canvas Slimer-selected layers and transformed layers export the visible selected artwork tightly cropped, with rotation and translation as displayed, no UI overlays or unrelated assets.
5. Export rejects invisible/off-canvas/empty assets rather than saving an empty file. It writes to a temporary PNG in the destination directory, reopens it, checks image dimensions and exact pixel data, and only then replaces the selected destination. Failure leaves existing files intact and reports a cause. The status reports dimensions and full output path.
6. **SHS location setting is unrelated to this Asset Library PNG export**. `Export for SHS` creates a PNG file for manual opening in SHS; it does not auto-launch SHS, alter the SHS EXE location, or create live synchronization. The tooltip now states this clearly.

## Critical behaviors retained

- Move Original Pixels ON by default; Copy Pixels available.
- Original selected pixels remain until a safe successful Apply Move. Cancel/failed operations preserve original artwork.
- Edit Selection remains the single transition from highlight to editable layer. There is no Finish Selecting control.
- No automatic new frame or changed timeline when repeating Slimer edits or editing imported asset placement.
- Pending Move Original locks the chosen source/layer identity and prevents Asset Library import/export until Apply/Cancel.
- Asset Library import/export preserve pixel alpha; exports never include selection tint, handles, ghosts, or joint dots.

## Verification

- Local test run: **480 passed, 31 skipped, 12 subtests passed**. The skipped tests are PySide6 GUI tests because Qt is not installed in this execution environment.
- `python -m compileall -q friendly_animator.py studio tests/test_phase82_repeat_and_imported_edit_gui.py tests/test_phase82_shs_export_visible_asset.py tests/test_phase82_shs_export_gui.py`: passed.
- Added GUI tests `tests/test_phase82_repeat_and_imported_edit_gui.py` and `tests/test_phase82_shs_export_gui.py`, to run on the user's Windows PySide6 environment.
- Added headless asset export tests `tests/test_phase82_shs_export_visible_asset.py`; all passed, including cropped Slimer layer, transformed part, small-native PNG, blank export refusal, and pending edit refusal.

## Windows test command

Extract the ZIP, open PowerShell in the folder, run:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase82_repeat_and_imported_edit_gui.py tests/test_phase82_shs_export_gui.py tests/test_phase82_shs_export_visible_asset.py tests/test_phase81_overlapping_move_gui.py
```

Then manually test: two Highlight -> Edit Selection -> Move -> Apply cycles on one pose; confirm handles hide after each Apply, no new frame appears, all source pixels clear only after Apply; import an asset and edit its placement using Edit Selection with no painted highlight; select the confirmed Slimer Layer in Asset Library, click Export for SHS, save an actual PNG, and open it in Paint or SHS to verify visible pixels.

## Remaining verification

- User must run Windows GUI tests; Phase 82 has **not** been verified against the user’s real Swordcat artwork yet.
- Confirm whether export for SHS should eventually auto-launch SHS when configured; this release implements reliable file export only.
- Continue to investigate any intermittent second selection failure not reproduced by the regression scenario, preserving exact status text and the editable project when possible.
- GitHub has **not** been modified.
