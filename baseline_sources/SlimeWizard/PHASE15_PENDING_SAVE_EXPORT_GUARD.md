# Phase 15: Pending layer save/export guard

- `save_project_by_id` refuses to serialize the active project while an Edit Selection layer is awaiting Apply Move or cancellation.
- `export` refuses to generate a sprite sheet from an unfinished layer transaction.
- These checks precede pose-draft preservation, file dialogs, and output writes.
- Added source-contract regression tests.
- Automated suite: 392 passed, 10 skipped, 12 subtests passed (GUI tests require Windows/PySide6).
- Remaining: actual consecutive Apply Move Windows validation, editing-table integration, pose/project roundtrip; timeline reorder deferred.
