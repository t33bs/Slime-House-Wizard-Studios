# Phase 15 — GUI destination-coordinate regression repair

The prior Windows-only consecutive editing-table test used `window.x.setValue(destination)` and asserted that a pixel originally at x=8 would appear at x=40. Slimer assets are full-canvas RGBA layers: the table X field is the layer's translation, not the final coordinate of the selected pixel. That test would fail on Windows despite a correct implementation. This checkpoint fixes the test to set `destination - source_x`, and checks the resulting pixel at the requested final coordinate.

This is a **test correction**, not a confirmed application behavior fix. The GUI test is still skipped without PySide6; run the suite on Windows before relying on it.
