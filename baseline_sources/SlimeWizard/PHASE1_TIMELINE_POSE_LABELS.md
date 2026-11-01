# Phase 1 — Timeline Slimer label synchronization

- The Asset Library shows `Slimer Pose 001`, `Slimer Pose 002`, etc. for the currently selected timeline pose when that pose contains a visible Slimer overlay.
- The internal layer name remains `Slimer pose overlay` to avoid relying on display names for identity.
- For older poses where the overlay is absent/hidden, the label reads `Slimer pose overlay (not in this pose)`.
- This is a UI-label synchronization change, not a migration of legacy duplicate layers or a complete pixel-loss repair.
- Automated result: 156 unit tests passed on Linux. Windows PySide6 GUI interaction and actual dragging are not yet verified.
- The source ZIP includes previous New Creature Slimer state reset and overlay-reuse patches.
