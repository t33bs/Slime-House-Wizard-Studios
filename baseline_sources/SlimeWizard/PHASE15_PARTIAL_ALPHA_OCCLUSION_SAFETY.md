# Phase 51 — Partial-alpha occlusion safety

In `_slimer_layered_erase_plan`, source-footprint classification now uses `classify_contributing_source_selection` rather than treating any nonzero-alpha upper pixel as fully hiding a lower source occurrence. An enlarged source pixel remains visible through a translucent overlay; erasing that pixel based on selection of only its other occurrence would alter unselected visible artwork.

Added `tests/test_phase15_partial_alpha_occluder_footprint.py` verifying translucent occlusion rejects the destructive plan while opaque occlusion permits it.

Windows Qt GUI verification of consecutive Edit Selection → table transform → Apply Move remains outstanding. GitHub repository untouched.
