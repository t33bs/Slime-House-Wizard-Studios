# Phase 15 — Staged source protection for asset transform shortcuts

When a Slimer editable destination layer is pending Apply Move, the existing Flip, Center and Reset Size asset commands now refuse to mutate any other asset. These commands remain usable on the staged destination. The existing editing table remains unchanged.

The guard runs before recording undo history or modifying the model. This prevents a source mutation from invalidating the pending Move Original Pixels transaction.

Validation: 400 passed, 11 skipped, 12 subtests passed in this environment. PySide6 GUI tests require Windows verification. GitHub working tree was not modified.
