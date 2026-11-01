# Phase 14: pose identity and recovery history audit

Audit found EditHistory.capture omitted pose_ids and pose_recovery while including animations and frame durations. Undoing deletion/copy/reordering could therefore restore pose frames without corresponding identity and recovery state.

Fix: capture both pose_ids and pose_recovery in deep-copied edit-history snapshots. The existing restore routine restores both with the rest of the editable model. No UI controls were rebuilt.

Tests: added regression cases for undo/redo after copying a pose and undoing a deleted pose with recovery data. Full suite: 275 passed, 1 skipped, 441 subtests passed.

Windows deferred checks: copy/delete/reorder pose, Undo/Redo, confirm selected pose and recovery history; switch animations during undo; ensure canvas and timeline thumbnails match after undo. No GUI validation was performed here.
