# Phase 15 — repeatable working-pose headless gate

Added `tests/test_phase15_working_pose_pixel_contract.py` to exercise three successive edits (arm, leg, arm again) with independent saved-frame rendering and exact RGBA preservation. This is a **model-level contract**: it does not invoke the Slimer GUI controller, and cannot establish that the GUI workflow passes.

Standardized `slimer_place_frame()` and `slimer_place_layer()` to return success/failure from their respective operations. A no-selection Place Frame returns True only after inserting a frame; a rejected selection propagates False. This makes subsequent integration tests able to assert actual completion rather than inferring success from status text.

Remaining required: run PySide6 GUI tests on Windows, especially repeatable Move Original after a saved pose switch and Undo/Redo.
