# Phase 14: Timeline history synchronization

- Added a pose-identity/order signature around model-level Undo and Redo.
- When timeline structure changes, reuses the existing playback restart helper.
- Ordinary pixel edits do not trigger a structural playback restart.
- Two AST regression checks added; Windows interaction checks deferred.
- Headless suite: 273 passed, 441 subtests passed, 1 GUI test skipped.
