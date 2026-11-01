# Phase 93 — Timeline ownership and cross-pose save protection

## Reported blocker
The user manually confirmed Phase 92's automated Windows tests (6 passed), but the actual Swordcat test then showed **Pose 2's edited frame replacing Pose 1**, making the two older timeline poses appear identical after placing the next frame. Phase 92 is therefore **not** accepted. Earlier regression checks were insufficient because some compared visually identical poses.

## Code changes
- `Suite._saved_pose_key()` now stores the project's ID, animation, row index, and **persistent `model.pose_id`**. `Suite._apply_saved_pose()` records the identity of the currently loaded canvas.
- `Suite.preserve_pose_draft()` only writes to an identity-matched pose, resolving its latest row using `_sync_pose_ids()`; stale row ownership cannot overwrite another pose.
- `Suite._canvas_owns_selected_pose()` refuses frame-affecting operations if the current timeline row doesn't own the live canvas; Place Frame, Save Current Pose, Insert Pose, Copy Pose, Duplicate Pose, and per-pose visibility all use it.
- When switching to a project or animation with no poses, live ownership clears. The first Place Frame remains possible without existing pose IDs.
- Original **Move Original Pixels**, Copy Pixels, Slimer layers and independent old pose snapshots remain intact.

## Tests
- `tests/test_phase93_pose_identity_gui.py` (Windows only): create Pose 1 with red-pixel move, Pose 2 with a different cyan-pixel move, then Place Frame for Pose 3; verify Pose 1 remains distinct and retains its own Slimer layers when switching back and forth. Separate test deliberately mismatches live pose ID and stale widget row and verifies both save and Place Frame refuse to corrupt Pose 1.
- `tests/test_phase93_model_pose_isolation.py`: headless pixel and stable pose ID isolation for three distinctly rendered frames, including save/reload.
- Existing six GUI tests from earlier phases remain available.
- Local non-GUI full suite passed **497**, skipped **41** (Windows/PySide6 GUI not installed in this environment), plus 12 subtests. This is a **candidate fix**, not a confirmed resolution of the reported Swordcat symptom.

## Windows test command
From extracted ZIP directory:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase93_pose_identity_gui.py tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```

Expected 8 tests, all passed. If any failure, provide complete traceback. Test a **copy** of Swordcat work, not an irreplaceable project. For manual acceptance make Pose 1 and Pose 2 deliberately different before placing Pose 3, then check both older poses. Also verify save/reopen preserves differences. GitHub untouched.

## Separate outstanding issues
Slime Cleaner behaves incorrectly on the user's artwork; investigate exact UI reproduction and layered/rotated erasure without guessing or touching it destructively. No reference-image features should return. Real creature PNG imports and editing remain supported. Do not publish to GitHub without explicit approval.
