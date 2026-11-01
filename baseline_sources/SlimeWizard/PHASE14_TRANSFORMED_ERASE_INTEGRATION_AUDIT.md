# Phase 14 — Guarded transformed erase integration

- Added `_slimer_transformed_erase_plan` to calculate exact nearest-neighbor source indices for a single visible live-source layer.
- Rejects partial rendered footprints, multiple visible layers, and saved `source_png` pose buffers.
- `_slimer_original_erase_safe(mask)` now accepts complete transformed live-source selections.
- `_slimer_erase_original_layers(mask)` applies the planned erase to fresh image copies; existing multi-layer translation behavior remains unchanged.
- Added three headless integration tests.

## Known limitations

- `resolved_pose()` normally carries `source_png`; the new transformed erase branch deliberately does **not** mutate such poses. Pose-specific source synchronization is the next task.
- Multi-layer transformed erase remains blocked, including semitransparent overlaps.
- GUI interaction, Windows runtime, undo/redo, and end-to-end export need Windows validation.
