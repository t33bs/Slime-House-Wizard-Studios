# Phase 95 — pose overwrite diagnosis and hard guard

## Manual report (not resolved)
The user confirmed all 11 Phase 94 Windows GUI tests passed, then manually reported **Pose 1 still becomes Pose 2** during actual editing. This outranks the green automated suite. The root cause is NOT yet established by a reproducing Windows failure or the user's saved project.

## Changes in Phase 95
- `Place Frame` now checks the exact saved per-layer state and the rendered RGBA pixel hashes for **all already existing timeline poses** after creating the new independent pose. This verification happens after saving the current draft (so the intentionally edited active pose is preserved) and before creating another frame.
- If a previous frame unexpectedly changes in that operation, restore the older snapshots, reject/remove the newly created frame, and surface an unmistakable `POSE PROTECTION` status instead of claiming success.
- For normal work, the status now explicitly says the new frame starts as a visual copy of the previous one and older saved poses were verified unchanged. This matters because seeing two identical frames **immediately after Place Frame** is expected; editing the new frame should make them different.
- Prevent `Place Frame` when the visibly selected Qt timeline row differs from the live editor's frame index. The old identity guard only compared the live ID and internal frame index, not the actual highlighted row.
- Expose the real `Place Frame` button under `slimer_place_frame_button` for regression tests and improve its tooltip.
- Add a Windows GUI test that clicks the actual buttons, edits two distinct poses, navigates via the actual timeline selection signal, and saves/reopens the project. Test is `tests/test_phase95_actual_gui_place_frame.py` (two GUI tests).
- Add 256x256 headless regression, `tests/test_phase95_pose_fidelity_headless.py`, and read-only `tools/inspect_pose_integrity.py` to report per-frame identity, pixel SHA, and whether adjacent saved poses are identical.

## What remains unverified
PySide6 is not installed in this container. The new Qt widget tests **must** run on the user's Windows system, and the real Swordcat editing path must be repeated. A perfect score does not prove the original bug is fixed. If the problem recurs, collect a ZIP containing the actual `.rig.json` project file **and its associated `<project>_assets_<id>` folder**, or run the read-only inspector and share its text. The exported sprite sheet PNG plus JSON is insufficient to identify where the editor's saved editable source was overwritten.

## Windows regression
From Phase 95 extracted directory:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase95_actual_gui_place_frame.py tests/test_phase94_edit_selection_active_gui.py tests/test_phase93_pose_identity_gui.py tests/test_phase91_no_reference_gui.py tests/test_phase88_first_place_frame_gui.py tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py
```

Expected **13 passes** if all earlier 11 pass and the new two pass. Also test with an expendable copy of the actual Swordcat project. Slime Cleaner remains a separate bug. No reference-only UI returned; original PNG imports retained. No GitHub changes or backup deletion.
