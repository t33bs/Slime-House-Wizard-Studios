# Phase 53 — Transformed fallback display geometry

The single-layer transformed Move Original erase path replaced the displayed part image with the native-size source image. When a part had been resized using nearest-neighbor, this silently collapsed its displayed dimensions, making subsequent selections/transforms inconsistent.

Fix: retain the current part image width and height when regenerating the edited display buffer from the erased native source. The original source retains its native size. This matches the multi-layer erase path.

Regression: `tests/test_phase15_transformed_fallback_geometry.py` forces the transformed fallback path for a 1×1 source displayed at 3×3 and verifies native source and display dimensions after erasure.

Validation: 419 passed, 17 skipped, 12 subtests passed. GUI tests remain skipped without PySide6. GitHub checkout untouched.
