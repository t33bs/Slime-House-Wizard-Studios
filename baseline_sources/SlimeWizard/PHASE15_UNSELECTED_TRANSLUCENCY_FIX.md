# Phase 15 — Unselected Translucency Source Mapping

## Application change
`_slimer_layered_erase_plan` previously rejected a contributing layer whenever any rendered pixel was partially transparent, even when the partially transparent pixel was outside the selection. The opacity preflight now examines only alpha at selected canvas positions. This enables safe opaque selections without weakening the protection against erasing selected fractional-alpha pixels.

## Regression
`tests/test_phase15_unselected_translucency_model.py` verifies that an opaque pixel is mappable when an unrelated pixel in the same asset has alpha 128, and that selecting the alpha-128 pixel remains rejected.

## Validation
411 passed, 17 skipped, 12 subtests passed. GUI tests skipped without PySide6; Windows GUI validation remains outstanding. GitHub repo not modified.
