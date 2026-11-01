# Phase 15 — off-canvas Move Original safety checkpoint

- `_slimer_commit` now validates that the transformed selection contains at least one visible destination pixel before `remember()`, erasing source pixels, or inserting a frame. Fully off-canvas moves are rejected without mutation.
- Added `tests/test_phase15_offcanvas_move_guard.py` for this behavior (requires PySide6/GUI environment).
- Corrected the multi-region regression's selection-reset assertion to permit both an empty selection and a cleared selection object; expanded repeated-overlay regression to assert clearing after every move.
- Linux environment: `346 passed, 7 skipped, 441 subtests passed`; Python compilation passed. PySide6 cannot be installed here due to network unavailability, so GUI behavior remains unverified.
- Do not overwrite an uncommitted Windows working tree with this checkpoint. Continue Windows gate before committing.
