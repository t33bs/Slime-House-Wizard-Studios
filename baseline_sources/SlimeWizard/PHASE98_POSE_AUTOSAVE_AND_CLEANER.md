# Slime Wizard Phase 98 — Autosave Pose Isolation + Slime Cleaner Layer Erasing

Date: 2026-10-31

## Reported after Phase 97

- User clicked Place Frame to save original Swordcat Pose 1, applied two independent Slimer leg moves, then clicked Place Frame again. The previous pose appeared overwritten.
- Slime Cleaner appeared unable to erase anything except pixels on the original source layer.

## Findings and fixes

1. **Recovered an unintended save path that Phase 96A didn't cover.** Place Frame itself no longer calls `preserve_pose_draft`, but `autosave_recovery()` still called that method every 60 seconds. After an Apply Move, this could save the live edited canvas into the selected older pose *before* Place Frame was clicked. Phase 98 marks a successful Slimer edit as an *unplaced next-pose draft* and prevents automatic `preserve_pose_draft` from replacing the old snapshot. `Place Frame` captures that live draft as the next independently saved pose; `Save Current Pose` remains the deliberate in-place save action.
2. **Protection against accidental draft loss.** Switching timeline frames or animations before committing an unplaced Slimer draft is blocked with an explanatory status. Saving the creature is also blocked until the user chooses Place Frame or Save Current Pose, preventing a misleading project save that omits the intended next frame. The 60-second recovery model still includes the live working art for crash recovery without mutating an earlier saved frame.
3. **Cleaner works on the uppermost visible layer in the current pose, not just the original imported PNG.** The eraser uses resolved per-pose transforms and can erase Slimer, Combined Artwork and rotated layers. For rotations it uses an ephemeral per-pixel identifier map with the same nearest-neighbor image transform as the renderer, avoiding uncertain inverse coordinate rounding. Only source images actually modified are updated. Hidden, lower, and earlier-pose snapshots are preserved; brush changes are Undo-able via the existing stroke transaction.
4. **The Phase 97 UI redesign remains.** The blue wizard-hat Slime Buddy panel and collapsible Animation Preview remain unchanged. His independent AI production engine is not connected or modified by this build.

## Automated checks

- Full local suite: **505 passed, 46 skipped, 12 subtests passed**.
- Headless tests added: `tests/test_phase98_autosave_capture_headless.py`, `tests/test_phase98_cleaner_layers_and_autosave.py`.
- Windows GUI tests added: `tests/test_phase98_real_gui_recovery_cleaner.py` (2 tests), **not runnable in this container without PySide6**.
- No GitHub push, original Phase 96A rollback ZIP and Phase 97 ZIP unchanged.

## Windows targeted GUI regression

Run in the extracted Phase 98 folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase98_real_gui_recovery_cleaner.py tests/test_phase97_collapsible_buddy_workspace_gui.py tests/test_phase96_place_frame_new_pose_gui.py tests/test_phase95_actual_gui_place_frame.py
```

**Expected 9 passed** (2 new, 3 Phase97, 2 Phase96, 2 Phase95). All must pass before real manual acceptance.

Then launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

### Manual Swordcat gate

1. Use a fresh test creature and the original source PNG, NOT an already corrupted saved project.
2. Click Place Frame once to make untouched Pose 1.
3. Make two separate leg moves, clicking Edit Selection and Apply Move each time.
4. **Allow more than 60 seconds to elapse between the first move and the second Place Frame** so the recovery timer fires.
5. Click Place Frame and compare Pose 1 vs Pose 2. Pose 1 must still be untouched and Pose 2 must contain both moves.
6. In Pose 2, use Slime Cleaner on the Combined Artwork layer. It must erase visible pixels there, and must leave Pose 1 unchanged.
7. Save/reopen the project and confirm both frames and the eraser edits survive (capture eraser edits with another Place Frame or explicit Save Current Pose as intended).

If the GUI still overwrites a frame, zip and share the `*.rig.json` project **together with its matching `_assets_<id>` directory**, so source snapshots and individual pose identities can be inspected. Sprite-sheet exports alone are insufficient.

## Limits / follow-up

- These are code-level and headless-verified repairs; Windows Qt and artist-provided manual acceptance remain pending.
- Slime Cleaner still deliberately refuses to abandon an unconfirmed Slimer layer; confirm or cancel it before erasing.
- For a pending next-pose draft, finish Place Frame or Save Current Pose before changing projects. Broader cross-project draft staging is out of scope.
