# Phase 87 — One combined editable asset for each NEW Slimer pose

## User-verified baseline

The user confirmed the real Swordcat can now make two independent highlight → Edit Selection → Apply Move operations on one pose; each move creates a correct Slimer layer (Phase 86A). Phase 85 resizing and Apply Move passed manually, as did the yellow joint guide cleanup. This is a distinct next-pose usability improvement, **not** a workaround to fix repeated selection.

## Behavior

- Pose 1 retains its original source + every individual Slimer layer, editable independently.
- After a user deliberately creates **Pose 2** from a saved Slimer-edited pose, the app renders only the visible source artwork into a new full-canvas, transparent RGBA `Combined Artwork NNN` asset **owned by the new pose**. Its earlier source layers remain in the global model (for old pose snapshots and undo) but are hidden in this new pose.
- The Asset Library lists only active/visible rows on combined poses, using `QListWidgetItem.setHidden`, which does not change the row-to-model index mapping. The previous pose still shows its original individual layer rows when revisited.
- The newly combined asset is selected by default and Slimer's selection snapshot is reset to the new artwork. Highlight any part of that base, Edit Selection, move/resize/rotate and Apply Move. No extra frame created by editing.
- On further user-created poses, recombine all newly visible changes into one new combined base. Each prior pose stays independently editable.
- Ordinary non-Slimer poses retain their pre-existing layered rigging, duplication and insertion behavior; no indiscriminate flattening.
- Only explicit timeline commands create poses: Place Frame, Insert pose, Copy pose, Duplicate last frame. No automatic merging occurs on **Apply Move**, **Edit Selection**, or **Save Current Pose**.
- Creating the **first** saved pose does not flatten the source: there is no prior timeline pose to keep layered.
- Existing Slimer controls, Move Original default ON and Copy Pixels option, alpha protections, and the user-approved single Edit Selection button are unchanged.
- Pending unconfirmed Slimer layers block creating/copying poses.

## Implementation/guards

- `PetSuiteModel.merged_working_pose()` renders the source snapshot *before* adding its new asset; returns a deep-copied new pose with earlier assets hidden and one new full-canvas native RGBA image visible. The source pose is never rewritten.
- `_insert_next_working_pose()` ensures the old pose's draft identity is cleared before applying the new appended asset; this avoids accidentally saving the new composite onto the previous pose.
- GUI Asset Library rows are hidden only for merged working poses, never deleted or reindexed. Save/reopen, undo/redo and previous pose edits stay supported.
- The app preserves original GUI model API calls on ordinary non-Slimer branches, retaining legacy tests and expected behavior.

## Tests

- Headless: two layers → new one-layer composite, source-pose unchanged, re-edit, third pose, saved-project round-trip, overlap RGBA preservation and undo/redo.
- Windows GUI (pending): `tests/test_phase87_pose_merge_gui.py` checks two real Slimer moves, Place Frame merging into one visible Asset Library row, fresh Slimer select/edit on new combined image, subsequent merge into third pose, old pose independence, and non-Slimer duplication left layered.
- The full local Qt-free suite must pass before handoff. PySide6 tests are skipped locally and **must** be run on Windows. The opt-in `isolate_gui_recovery` fixture avoids invisible offscreen recovery-dialog hangs and touching real recovery files.

## Windows commands

Run inside extracted Phase 87 folder:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase87_pose_merge_gui.py tests/test_phase86_repeat_alpha_gui.py tests/test_phase85_resize_and_selection_recovery_gui.py
```

Launch:

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" .\friendly_animator.py
```

GitHub untouched; protected prior ZIPs and user's Windows project files remain unmodified.
