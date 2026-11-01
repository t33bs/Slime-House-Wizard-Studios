# Phase 5 — Confirm All Placements (2026-10-28)

Added `Confirm All Placements` button to the Slimer controls. It collects nonempty selection masks across color tabs, applies each tab's own move/scale/rotation against the original rendered canvas, and places the combined result as one independent Slimer Layer and one Undo history entry. Move Original Pixels clears the union of the source masks; Copy Pixels preserves originals. Empty selections are ignored. Existing Place Frame and Place as Layer actions remain unchanged.

**Deferred Windows GUI checks:** activate multiple color tabs, confirm independent transforms, inspect alpha/color fidelity, verify Undo/Redo, Move vs Copy, overlapping tab order, frame isolation, and whether button wording/placement is intuitive. This phase is not GUI-verified; PySide6 is unavailable in the current Linux test environment.
