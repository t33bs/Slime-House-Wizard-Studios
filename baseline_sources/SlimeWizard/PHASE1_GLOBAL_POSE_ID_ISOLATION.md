# Phase 1 — Cross-animation pose ID isolation

- Pose IDs must be unique across all animation timelines, not just within each timeline, because pose recovery is indexed by pose ID.
- `_sync_pose_ids` now reserves IDs already present in other animations and replaces collisions without changing pose pixels.
- Added `tests/test_phase1_global_pose_ids.py` for collision repair and recovery isolation.
- Verification: `python -m pytest -q`: 206 passed, 433 subtests passed.
- Deferred Windows GUI tests remain deferred. This patch does not establish that repeated Slimer dragging is fixed in the Windows application.
