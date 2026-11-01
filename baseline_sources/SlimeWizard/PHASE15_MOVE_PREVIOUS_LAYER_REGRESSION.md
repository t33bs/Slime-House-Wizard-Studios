# Phase 15 — Move Again From Previous Slimer Layer

Added `tests/test_phase15_move_from_previous_slimer_layer.py` to cover a second Move Original Pixels operation where the selected source is not the initial imported artwork but the real editable Slimer layer created by the first operation. The test calls the production source-mapping planner and eraser against the actual PetSuiteModel, checks the prior destination is cleared and the new destination has exact RGBA pixels, and verifies no unwanted copy remains.

This is a regression-test checkpoint, not a confirmed Windows GUI fix. The GUI sequence, edit-table transforms, pose switching, and save/reopen still need Windows validation. No GitHub working tree was touched.
