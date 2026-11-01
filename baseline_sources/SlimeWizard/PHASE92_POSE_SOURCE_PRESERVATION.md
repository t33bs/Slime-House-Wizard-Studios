# Phase 92 — saved pose preservation / Move Original GUI regression

## User-observed red Windows test (Phase 91)
- `tests/test_phase88_first_place_frame_gui.py`: three other target GUI tests passed; Phase 88 failed expecting alpha **138** at `(50,60)` after Move Original shifted that pixel by **+3** horizontally.
- Since Move Original had successfully applied, source coordinate `(50,60)` should be **transparent** (alpha 0), and destination `(53,60)` should have alpha **138**. The older test assertion was incorrect and did not check the destination.
- A second, real bug was found while tracing the same flow: `slimer_place_frame` called `_finish_current_slimer_pose_as_working_source`, which silently flattened/replaced **the previously saved pose** when creating the next pose. This hid its independent Slimer layers. This violated the project's cross-pose layer-preservation requirement.

## App fix
- `slimer_place_frame()` still saves the current pose's complete edited snapshot with its distinct visible assets (via `preserve_pose_draft`), then calls `_insert_next_working_pose` to create a **new** combined working source for the next pose.
- Removed `_finish_current_slimer_pose_as_working_source` and its call; only the new pose is flattened. The previous pose retains its independent layer visibility and per-pose PNG snapshots.
- All previous Move Original / Copy Pixels guards, source erasure atomicity, default ON, and repeated edits are unchanged.
- Phase 91 removal of reference viewer/upload controls is preserved. Real PNG art imports are preserved. Slime Cleaner is unchanged and still requires separate debugging.

## Regression checks
- Updated `tests/test_phase88_first_place_frame_gui.py` to check both original and destination alpha, verify Pose 1 still has **two** visible editable layers after second move (Combined Artwork plus Slimer), and verify Pose 2 has one merged layer. Checks pose switching and Asset Library isolation.
- Added `tests/test_phase92_previous_pose_layers_model.py` for exact RGBA source/destination preservation, previous saved pose layer retention, and save/reopen with multiple poses.
- Local full suite passed; actual Windows PySide6 GUI acceptance still required.

## Windows run
```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```
Expected collection: 6 GUI tests in the four modules. Run inside extracted `SlimeWizard92` root.

## Manual acceptance
1. On a project **copy**, import the Swordcat as an actual editable PNG asset; activate Slimer with Move Original checked.
2. Highlight and move an opaque part, Apply Move. Place Frame for the first saved pose; it should show one Combined Artwork asset.
3. On Pose 1, highlight and move another part, Apply Move. Check original location empty, destination contains the moved pixel. Place Frame to create Pose 2.
4. Select Pose 1: the edited previous pose should keep its own separate Combined Artwork and Slimer Layer in the Asset Library, with all changes intact. Select Pose 2: one combined editable source should reproduce the complete artwork.
5. Repeat on Pose 2 and confirm Pose 1 remains unchanged. No new frame should appear from Apply Move alone.
