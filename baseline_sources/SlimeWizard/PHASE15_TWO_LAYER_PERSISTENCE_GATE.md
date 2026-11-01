# Phase 15: two-layer pose persistence gate

This checkpoint adds pixel-level, headless integration tests for two independent Slimer-style editable assets. Tests verify that per-pose position, resize, and rotation survive saving a project, loading it, and repeatedly switching poses. A second test verifies a newly added layer remains hidden in a pose that predates it, both before and after switching to a later pose.

Result: 394 passed, 10 skipped, 12 subtests passed. PySide6 GUI tests remain skipped here. These tests validate the underlying model, not the full GUI Edit Selection -> Apply Move workflow; that still requires Windows testing.

No changes made to the user's GitHub working tree. Timeline drag reordering remains deferred.
