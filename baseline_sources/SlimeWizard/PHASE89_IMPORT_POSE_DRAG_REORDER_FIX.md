# Slime Wizard Phase 89 — Import Pose PNG + timeline drag reorder safety

## User report

After importing a 128×128 Swordcat walk PNG as independent Pose 2, the user dragged Pose 1 into Pose 2's position and observed unexpected behavior in the timeline/editor. The latest uploaded screenshot of the post-drag result was not accessible to source inspection in this runtime, so that exact visual symptom remains unverified.

## Root-cause risk and correction

QListWidget with InternalMove reorders visual items first and may emit `currentRowChanged` while the model's saved pose list is still in its original order. The old handler refreshed and repopulated the QListWidget *inside* the `rowsMoved` callback, during Qt's drop handler. It also ran `preserve_pose_draft` after visual item selection had already moved, risking saving live pixels to a different pose or refreshing Qt-owned objects while they were being moved.

- Introduced `PoseTimelineList` to block selection signals temporarily during its drop processing. It refuses to reorder while a provisional Slimer destination is awaiting Apply Move/Cancel.
- `_timeline_rows_moved` now schedules `_commit_timeline_drag` on the next Qt event cycle, after `dropEvent` completes. This is the safe point for `preserve_pose_draft`, undo history, model reorder, thumbnail rebuild, and selecting the moved pose.
- Explicit `setDragDropOverwriteMode(False)` and single-row selection.
- Model `reorder_frame` remains the authoritative owner of pose snapshots, stable pose IDs and per-pose durations; no source pixel compositing during reorder.
- Fixed `Import Pose PNG` pose-draft contamination: importing a new layer temporarily changes the live parts table. Previously `load_frame()` could auto-save that temporary imported layer back onto the prior pose. The importer now clears the old pose draft key **after preserving the old pose but before loading the new pose**, ensuring Pose 1 is byte-for-byte unchanged. Import is blocked while an unconfirmed Slimer layer is staged. It continues adding a new independent pose, not overwriting an existing one.
- No changes to Slimer Move Original, Copy, resizing, safe source erasure or Cleaner in this patch.

## Tests

- New Windows PySide6 test `tests/test_phase89_timeline_drag_import_gui.py` simulates an import of a full-canvas PNG followed by a queued drag reorder and asserts that **Pose 1's source image/PNG is unchanged immediately after import**, then checks separate snapshots, draft preservation, pose durations, current pose, and Undo.
- Updated one brittle source-string UI test to accept a drag-safe `PoseTimelineList` subclass as well as the old `QListWidget`.
- Full available local suite: **497 passed, 38 skipped, 12 subtests passed**. Actual Windows drag-and-drop requires hands-on verification.

## Windows test command

```powershell
& "$env:USERPROFILE\Downloads\DocumentsSlime-Wizard-Pre-Merge-Backup\.venv\Scripts\python.exe" -m pytest -q tests/test_phase89_timeline_drag_import_gui.py tests/test_phase88_first_place_frame_gui.py
```

## Manual acceptance

1. Back up a copy of a test creature project. Import original Swordcat PNG and create/save Pose 1.
2. Click Import Pose PNG, pick a 128×128 transparent walk-pose PNG; confirm a new Pose 2 appears without changing Pose 1.
3. Drag Pose 1 to the position formerly occupied by Pose 2; confirm thumbnails swap ORDER only, each retains its own image, editability and 125ms duration or custom duration.
4. Switch between poses, edit Pose 1 and confirm Pose 2 remains unchanged. Check Ctrl+Z restores order.
5. Check Phase 88 pose-one-to-infinity Combined Artwork functionality separately; it is a separate unverified Windows feature.

## Unresolved and safety

- Slime Cleaner has a distinct report of incorrect erasure on transformed/overlapping assets. Its target semantics require a separate documented repro before modifying destructive erase code.
- The exact second screenshot of the post-drag symptom was not available in the current session. If behavior persists despite this targeted race fix, obtain the screenshot/status/error and reproduce the precise visual symptom.
- GitHub and existing archives are untouched.
