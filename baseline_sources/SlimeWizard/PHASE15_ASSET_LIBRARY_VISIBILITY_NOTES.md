# Phase 15 — Pose asset visibility UI preview

This preview builds on the sequential Slimer and per-pose visibility changes.

## Added
- Asset library labels show `[hidden in this pose]` and dim hidden entries.
- Remove/Restore actions enable only when appropriate for the selected saved pose.
- An explanatory label indicates selected asset visibility.
- Canonical asset names are unchanged; no shared asset is deleted.

## Validation
- Python compilation passed.
- Existing pytest suite: 328 passed, 2 skipped, 441 subtests passed.
- Windows PySide6 GUI/manual verification still required; this is not a finished release.

## Still pending
- Full saved-pose asset re-edit regression tests.
- Timeline insertion UI and recipe controls cleanup.
- Windows GUI checks of sequential moves, per-pose visibility and frame isolation.
- Installer testing intentionally deferred at user's request.
