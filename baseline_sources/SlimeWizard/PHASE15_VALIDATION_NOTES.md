# Phase 15 sequential editing — validation preview

This package extends the Phase 15 Slimer sequential-moves preview with regression coverage.

- `tests/test_phase15_sequential_slimer.py` exercises two consecutive copy-mode moves into one overlay without inserting a timeline frame. Requires PySide6; skipped in the current Linux environment.
- `tests/test_phase15_timeline_insertion.py` checks inserting a pose in the middle without overwriting adjacent snapshots. Passed locally.
- Local pytest: 328 passed, 2 skipped, 441 subtests passed. This does **not** establish Windows GUI success.

## Still outstanding

- Confirm the sequential Slimer GUI test passes on Windows; add Move Original and undo/redo regression scenarios.
- Pose-specific asset deletion, with stable source indexing and isolation across poses.
- GUI affordance for insertion at an arbitrary timeline position.
- Remove legacy Idle/Breathing recipe presets without removing legitimate animation selection.
- Do not test installer until user approves the full editor workflow.

Do not replace the validated green Windows build with this preview until GUI validation succeeds.
