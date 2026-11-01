# Phase 96A — correct old Phase 87 Windows GUI test expectation

## What the Windows user reported
Phase 96 targeted Windows run: **14 passed, 1 failed**. Failure in `tests/test_phase87_pose_merge_gui.py::test_two_layer_moves_merge_in_next_pose_and_reedit_again`, at its assertion that saved frame 0 had 3 layers; it actually had 1 layer.

This is the new Phase 96 **intended behavior**. The test inserts and saves Pose 1 as the original single-part source, then performs two separate Slimer Move Original edits on the *live* canvas. The second Place Frame should capture those edits into a NEW Pose 2, while saved Pose 1 remains one original source layer. Under the older workflow, Pose 1 also accumulated two newly committed Slimer layers; Phase 96 specifically removed that unsafe overwrite.

## Change
- In the Phase 87 GUI test, expect 1 original source layer in saved Pose 1, not 3 edit layers; assert its name is the original `Swordcat Source`.
- Retain assertions that the two edited artwork moves become the next pose, previous RGBA pixels remain byte-for-byte identical, later poses keep their own original snapshots, and Asset Library correctly isolates layers.
- NO changes to application code, model behavior, or reference import features.
- No GitHub changes; old ZIPs preserved.

## Verification
Local: **500 passed, 44 skipped, 12 subtests passed**; `compileall` passed. PySide6 isn't installed in Linux execution environment. Windows GUI tests need rerun; previous run 14/15 with this one stale assertion.

Run from extracted Phase96A folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase96_place_frame_new_pose_gui.py tests/test_phase95_actual_gui_place_frame.py tests/test_phase94_edit_selection_active_gui.py tests/test_phase93_pose_identity_gui.py tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```

Expected targeted suite: **15 passed**. Actual user verification pending.

After the test, launch Phase96A with:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

Manual acceptance still required: new blank project + original Swordcat PNG, Place Frame to capture untouched Pose 1, two separate leg Slimer moves and Apply Move, Place Frame to capture Pose 2, verify Pose 1 unchanged, then create Pose 3, save/reopen and recheck. Slime Cleaner activation after Apply Move is still an open issue.
