# Phase 15 — overlay pose-switch isolation checkpoint

Added `tests/test_phase15_overlay_pose_switch_contract.py` to verify that a saved pose with two overlay edits retains exact RGBA values after repeated switches to and from an earlier pose. The earlier pose stays independent; the test checks three round trips and unchanged frame count.

This is a headless model-level test, **not** proof that the GUI Apply Move, Place Frame, or Undo/Redo workflow succeeds. The GUI tests still require PySide6/Windows verification. No existing GitHub working tree was modified.
