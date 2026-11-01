# Phase 1 — Persistent timeline pose recovery

- Project saves now include bounded per-pose recovery history, keyed by stable pose IDs.
- Project loads restore only histories belonging to existing pose IDs; at most five versions are retained per pose.
- Older projects without a `pose_recovery` field remain loadable.
- Recovery remains separate from rendered/exported sprite pixels.
- Automated test suite: 167 tests passing in this source snapshot.

Still outstanding: a GUI Restore Previous Pose action, Windows interface verification, safe migration of legacy duplicate Slimer layers, and full repeated drag/highlight/Place Frame pixel-loss verification. This source update does not prove the original GUI pixel-loss bug is fixed.
