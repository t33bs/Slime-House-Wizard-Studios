# Phase 88 — Continuous Slimer working-source cycle begins at Pose 1

## User goal

A beginner should be able to edit a Swordcat repeatedly from the first saved pose through any later pose. After using Place Frame, the placed artwork becomes one fresh editable *source* for Slimer. This is a rendering/working-layer operation; earlier source pixels, selected move layers and saved pose history must not be silently destroyed.

## Implemented scope

- First Place Frame **with existing Slimer edits**, even when this animation has no prior saved frame, now inserts Pose 1 with one visible, full-canvas RGBA `Combined Artwork NNN` source. Previously the first pose was left as numerous visible layers and only Pose 2 got the combination.
- All earlier source and Slimer layers are preserved as hidden, full PNG-bearing snapshot states; they are **not deleted**. The Asset Library displays only the visible combined source in that combined pose.
- Edit Selection can highlight and move new pixels from Pose 1, while additional Place Frame operations keep creating a single editable source in the newly created pose. Each pose retains its per-pose source PNG snapshots for later recall and project save/reopen.
- The existing normal flow, where a user saves a plain unedited Pose 1 first and creates Slimer edits on it later, remains unchanged: when creating Pose 2, Pose 1 retains its separately editable layers, while Pose 2 receives a combined working source. Old poses are deliberately not rewritten when creating the next one.
- Ordinary layered/rigged projects without Slimer edits remain unchanged. No automatic frame from Apply Move or Edit Selection.
- Existing Move Original (default checked), Copy Pixels, resizing, source-erasure integrity, and all other Slimer protections remain unchanged.

## Separate Slime Cleaner issue

Slime Cleaner currently clears only the topmost visible pixel using unrotated `(x - layer_x, y - layer_y)` coordinates. This can fail to target rotated or resized layers and reveal a pixel from a lower layer that makes the erasure appear ineffective. Because the user has not yet described precisely which symptom occurred, Phase 88 does not silently change whether Cleaner deletes only the topmost layer or all layers underneath. A narrowly scoped follow-up should reproduce Cleaner behavior with the user's actual selection/brush/layer state and add regression tests before altering destructive eraser semantics.

## Tests and release status

- Added `tests/test_phase88_pose_one_combined_source.py` for source preservation, repeat pose creation and save/reopen.
- Added Windows PySide6 `tests/test_phase88_first_place_frame_gui.py` for initial Slimer move, first Place Frame, re-highlight/edit, later pose creation, prior pose pixel independence.
- PySide6 GUI suite skipped on Linux; must be run on Windows. `isolate_gui_recovery` fixture prevents invisible autosave-recovery dialogs from blocking the tests and prevents test mutations to the real recovery folder.
- GitHub and preexisting source ZIPs remain untouched.
