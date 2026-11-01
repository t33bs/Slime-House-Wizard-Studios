# Phase 14 — Rotated pose and selection-mask audit

Added a 90-degree nearest-neighbor saved-pose regression test that selects the complete displayed footprint of one original source pixel. Verified the copy-on-write erase changes only the targeted saved frame and preserves the other frame.

Added explicit L-mode validation for selection masks before provenance classification and source mutation; RGB masks are rejected instead of being interpreted as truthy RGB tuples.

Full headless suite: 325 passed, 1 skipped, 441 subtests passed. Python compilation passed. Windows GUI test remains deferred. The saved-pose erase is model-level and is not yet connected to the Slimer UI.
