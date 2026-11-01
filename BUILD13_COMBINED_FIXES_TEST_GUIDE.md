# SLIME HOUSE WIZARD STUDIOS — Build 1.3 Candidate

**Purpose:** Batch the outstanding Save/Close/Frame and UX changes before the next Windows acceptance run.

## Included

1. Build 1.1: Save Creature can persist a still-unplaced next pose as a separate editable draft without adding a frame or rewriting a placed pose. Includes model and validator support.
2. Build 1.2: SHS close prompt handles **Yes = close with recovery backup**, **No = close and discard unsaved changes**, **Cancel = keep editing**. Wizard retains its own Save / Discard / Cancel guard.
3. **Save Creature As…** on Wizard toolbar to write a *new* `.rig.json` without replacing the prior file. The plain Save Creature still saves the current project path. SHS also gains **Save As** for its project JSON.
4. SHS Chameleon 2×2 tool: select **Chameleon (2×2)**, click source top-left pixel once to sample exact RGBA, click destination to stamp. **Chameleon: Resample 2×2** picks a fresh source. Undo available; source untouched; paint only into a selected, unrotated/unscaled layer.
5. SHS standard crosshair instead of the sometimes-empty cursor bubble. Main host has **Open Slime Wizard Tab** and **Save SHS Pose + Return to Wizard** linked handoff control.
6. **NEW: vertical resize bar between Wizard canvas and pose timeline**: drag the purple 13px handle (between creature tabs and POSE TIMELINE heading) up to enlarge the timeline, or down to enlarge the canvas. Divider sizes are saved in QSettings across a normal shutdown. Does *not* resize the 128×128 sprite, recolor pixels, or change saved poses.
7. **NEW: wider Wizard left panel and Asset Library scrollbars**: 19px width, >=44px scrollbar thumb height, contrasting hover color. Timeline pose thumbnails increased from 66×66 to 82×82; timeline may grow from 124px to 420px vertically. The timeline section has its own scroll when there isn't enough room for action rows.
8. Installer-path correction from the prior fix is preserved in `packaging/SHWS.iss` (source points to onedir `dist/SlimeHouseWizardStudios/*`).

## Automated checks performed here

- `python -m pytest tests -q` => **26 passed, 2 skipped** (PySide6 unavailable in this Linux runtime).
- `python -m compileall -q main.py studio shws_wizard tests` => passed.
- The user's recovered `placeframe.rig.json` loaded via real `shws_wizard.studio.pet_suite_model.PetSuiteModel.load_project`: 128×128 canvas, 12 parts, 6 Idle / Breathing poses.
- SHS + Wizard source baselines preserved (integration boundary tests). UI fixes are additive; the model logic and standalone Slime Buddy remain untouched.

## Windows testing — run once, after build

Build in a GitHub Actions Windows runner using `.github/workflows/build-windows.yml` or your local configured Windows PySide6 environment. This is a **source** ZIP, **not** a pre-built Windows executable; Windows runtime behavior has not been manually verified.

1. Open a rig with 6 poses. Drag the purple divider upward between Wizard canvas and Pose Timeline. Confirm you see more timeline area and larger thumbnails, with no pixel or frame changes. Drag it down to reclaim canvas area; check 'Fit to Canvas'.
2. Close and reopen normally; check vertical split is remembered. Check wide scrollbars in TOOLS & ASSETS and ASSET LIBRARY.
3. Make an unfinished next-pose edit without clicking Place Frame. **Save Creature** and reopen; previous 6 poses unchanged, unfinished pose restored. Place it to create pose 7, then repeat to 12.
4. Use **Save Creature As…** to create `my-creature-copy.rig.json`; verify original file is unchanged, new editable file opens.
5. In SHS, test Chameleon sample/stamp, undo, blank/transparent pixels, boundary handling, and **Save As**.
6. Change SHS without saving, close app, select **Cancel** => stays open, **No** => closes without saving, **Yes** => closes with recovery copy.
7. Use Edit Frame in SHS, change pixels, then Save SHS Pose + Return to Wizard. Confirm only linked pose changes.
8. Reopen the recovered sample rig if needed, and verify animation preview, export and timeline reorder continue to function.

## Restrictions

The canvas splitter resizes **UI panes only**. Sprite canvas dimensions, all existing animation data and Slimer/Cleaner tool behavior should remain unchanged. The full PySide6/Windows GUI tests and GUI visual QA are outstanding. Keep backups of original projects while accepting this candidate.
