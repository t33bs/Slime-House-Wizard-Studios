# Phase 15 — repeatable multi-region Move Original gate

This checkpoint adds a source-preflight guard: destructive Slimer commits must account for every highlighted pixel using a visible editable layer. Unmapped pixels reject the commit before history, pose, or frame mutations.

Added `tests/test_phase15_multi_region_move.py` covering repeated Apply Move on two separate positions of the same source asset and a subsequent move of the first region. The GUI test verifies the selection resets, precise RGBA preservation, overlay reuse, and no implicit timeline frames. This test is skipped on this Linux environment because PySide6 is unavailable.

Added `tests/test_phase15_unmapped_selection_guard.py` as a source regression check.

Validation here: Python compileall passed; pytest: 346 passed, 6 skipped, 441 subtests passed. This does not establish that the Windows GUI defect is fixed. Do not overwrite an uncommitted working copy without backup. Windows GUI verification and original Apply Move / Place Frame issue remain outstanding.
