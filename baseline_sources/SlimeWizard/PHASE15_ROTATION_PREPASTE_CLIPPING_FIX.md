# Phase 70 — rotation pre-paste clipping safety

`PetSuiteModel.render_part` pastes a layer onto the canvas **before** rotating it.
The Phase 69 destination check looked only at the final rotated footprint.
A pixel outside the canvas at paste time could therefore be lost even if its
rotated position would fit. `destination_fits_canvas` now also checks the
pre-rotation nontransparent footprint, rejecting unsafe Move Original placements.
Copy Pixels remains unaffected. A future rendering refactor could rotate on an
unclipped surface instead; until then this conservative check protects sources.
