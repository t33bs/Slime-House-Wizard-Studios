# Phase 69 — Rotated destination clipping safety

Move Original Pixels now preflights the un-clipped, transformed alpha of the staged layer before source erasure. The check rotates the selected layer on a padded local image with the same nearest-neighbor rotation center as the model renderer, then verifies that every visible destination pixel fits within the canvas. Copy Pixels is unchanged. Staged edits are preserved when the check rejects a move.

New module: studio/slimer_destination.py. New tests: tests/test_phase15_rotated_destination_clipping.py.

Validation: 447 passed, 19 skipped, 12 subtests passed. GUI tests require PySide6/Windows validation. The consecutive Edit Selection / Apply Move GUI bug is not confirmed fixed.
