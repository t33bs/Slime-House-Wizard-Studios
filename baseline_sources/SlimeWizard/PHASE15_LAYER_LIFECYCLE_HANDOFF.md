# Phase 15 editable-layer lifecycle checkpoint

## Implemented in this pass
- Prevent highlighting a second region while a provisional Edit Selection layer is pending Apply Move or Cancel. The current pose and source mask are preserved.
- Added model-level regression for two independent editable Slimer layers, transformed independently and restored through distinct pose snapshots.
- Added a source-level check for the provisional-selection paint guard.

## Test result
386 passed, 9 skipped, 12 subtests passed in the Linux/headless test environment. PySide6 GUI tests remain skipped.

## Not yet proven
- Actual Qt GUI sequence: highlight > Edit Selection > drag/resize > Apply Move, repeated twice on the same canvas.
- Cancellation and undo/redo of provisional asset with all asset-table edits.
- Full save/reopen project integration of multi-layer poses through the Windows GUI.
- Timeline Pose 2 -> Pose 1 drag (deferred by user).

Use a fresh extracted folder, not the user's GitHub working tree. Keep the backup.
