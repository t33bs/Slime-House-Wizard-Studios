# Phase 55 — New canvas pending Slimer guard

Creating a new creature while a Slimer Edit Selection layer is staged could switch away from an unfinished source-erasure transaction. `new_project()` now refuses to open its size dialog while `_slimer_pending_part` exists, and tells the creator to Apply Move or Cancel Unconfirmed Layer first.

Regression: `tests/test_phase15_new_canvas_pending_layer_guard.py` executes the production method in isolation and verifies that no dialog is opened and a useful status message is shown.

Validation: 422 passed, 17 skipped, 12 subtests passed. Windows PySide6 GUI interaction remains to be verified. No GitHub working tree was modified.
