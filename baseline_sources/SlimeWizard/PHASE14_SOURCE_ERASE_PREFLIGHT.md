# Phase 14 — Source erase preflight

Added `plan_complete_source_erase` and `erase_planned_source_pixels` to `studio/pixel_source_mapping.py`.

The planner rejects a destructive source edit if even one visible occurrence of a selected source pixel remains outside the selection. It supports nearest-neighbor enlargement and rotation by consuming the renderer-matched mapping. The erase helper returns an independent RGBA image, preserves unrelated pixels and rejects invalid source indices before editing.

This is **not wired to Slimer Move Original** yet. Before that, validate per-layer alpha contribution, source_png/current buffer equivalence, inherited transforms, and overlapping selections. The current protective guard remains in place.

Headless tests: `tests/test_pixel_erase_preflight.py`. Windows GUI checks remain deferred.
