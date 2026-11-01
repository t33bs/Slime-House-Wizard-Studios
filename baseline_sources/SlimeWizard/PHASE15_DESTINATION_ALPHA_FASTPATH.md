# Phase 71 — destination alpha fast path and renderer differential checks

`destination_fits_canvas` now reads the alpha channel directly from already-RGBA staged assets rather than allocating a duplicate full RGBA image. This avoids an unnecessary 4 MB image copy for a 1024×1024 staged Slimer layer before bounds checks, while preserving conversion for non-RGBA inputs.

Added 300 deterministic randomized destination placements and rotations checked against the actual Pillow canvas-first rotation renderer, plus an RGBA fast-path regression that disallows `convert` on the staged image.

Windows GUI tests remain skipped in this environment. The user's consecutive Edit Selection / Apply Move GUI failure is not yet verified as resolved. GitHub working tree untouched.
