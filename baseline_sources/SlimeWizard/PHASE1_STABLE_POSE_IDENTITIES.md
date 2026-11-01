# Phase 1 — Stable timeline pose identities

Implemented in `studio/pet_suite_model.py`:
- Each timeline pose has a stable internal UUID, independent of its displayed timeline position.
- Insertion and copying create new IDs; reordering carries IDs with artwork and duration; deletion discards only the deleted pose's recovery history.
- Pose recovery is keyed by pose ID, not the mutable timeline index.
- The legacy `save_frame` path now uses the same insertion/identity handling.
- Project saves retain pose IDs; older project files receive IDs on load.
- Replacing an existing frame's PNG now records a recoverable previous snapshot.

Verification: `python -m unittest discover -s tests -q` — 164 tests passed in this source environment.

Still outstanding: GUI-level testing on Windows, persistence of per-pose recovery versions across app restarts, recovery UI integration, and legacy duplicate Slimer layer migration. These changes do not establish that the original pixel depreciation bug is fully resolved.
