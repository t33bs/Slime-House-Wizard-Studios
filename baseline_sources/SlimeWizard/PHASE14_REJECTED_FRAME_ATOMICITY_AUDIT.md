# Phase 14 — Rejected frame placement atomicity

## Finding
`_slimer_commit(as_frame=True)` previously called `preserve_pose_draft()` before validating the destructive Move Original selection. An invalid selection could therefore persist a draft even though no placement occurred.

## Change
Validate `_slimer_original_erase_safe(selection.mask)` before `preserve_pose_draft()` and before `remember()`. Rejected operations now return without timeline draft persistence or undo snapshots. The accepted path still saves the prior pose before creating a new overlay/frame.

## Verification
`python -m pytest -q`: 326 passed, 1 skipped, 441 subtests passed.
`python -m compileall -q friendly_animator.py studio tests`: passed.

## Limitations
AST regression checks operation ordering; Windows GUI interaction remains unverified. Saved-pose model-level erase is not yet wired into the Slimer UI. Multi-layer transformed editing remains guarded.
