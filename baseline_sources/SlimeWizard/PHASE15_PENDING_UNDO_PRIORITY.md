# Phase 15 — Pending Slimer layer Undo/Redo priority

When Edit Selection has staged a real editable layer, Undo/Redo now uses the model history instead of consuming leftover Slimer brush-selection history first. The existing `_after_history_restore` resets stale pending identity and selection after the model changes. When no layer is pending, Slimer selection undo/redo retains its previous behavior.

Regression coverage: source contract and a Qt GUI test for Undo after Edit Selection with brush history present. The Qt test is skipped in the headless development environment without PySide6 and needs Windows verification.

Validation: 401 passed, 12 skipped, 12 subtests passed. No modifications to the user's GitHub checkout.
