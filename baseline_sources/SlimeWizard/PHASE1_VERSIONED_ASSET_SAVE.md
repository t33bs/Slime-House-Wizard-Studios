# Phase 1: Versioned asset save and recovery

Project saves now write PNGs to a unique sibling folder, then atomically replace the JSON manifest. Previous committed asset files are never overwritten during a new save. Failed saves remove their staged folder. The loader supports both the new `asset_dir` manifest key and legacy fixed-folder projects.

Crash-recovery publication was updated to publish the staged manifest without renaming its versioned asset folder. Recovery discard removes its currently referenced asset folder. Older unreferenced folders are intentionally retained for now, pending a safe cleanup/retention policy.

Tests: `python -m pytest -q` => 221 passed, 433 subtests passed. Windows GUI tests remain deferred.
