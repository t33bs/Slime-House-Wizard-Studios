# Phase 49 — occluded scaled-source footprint fix

## Actual application correction

`_slimer_layered_erase_plan()` now includes all visible layers in the topmost-ownership classifier, including layers with no selected pixels. Previously, the planner excluded an unselected upper layer from the classifier, causing a lower source pixel expanded by nearest-neighbor scaling to appear only partially selected even when its other rendered occurrence was fully hidden by that upper layer. This could incorrectly block a valid Move Original Pixels operation.

Unselected layers are used only for occlusion accounting: their source buffers are not destructively edited, and stale unrelated part buffers do not veto a valid selected-layer move. Selected contributors still undergo full provenance and opacity checks. Move Original and Copy Pixels remain intact.

Regression: `tests/test_phase15_occluder_footprint_model.py` tests a 1x1 source scaled to two pixels, with one pixel selected and the other covered by an unselected upper layer. Expected plan erases only the bottom source pixel.

Windows GUI workflow remains unverified here; do not claim that the second consecutive Edit Selection → Apply Move bug is resolved.
