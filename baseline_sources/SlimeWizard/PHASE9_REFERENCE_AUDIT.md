# Original roadmap Phase 9 — user reference viewer audit

Already implemented: optional user-uploaded PNG, GIF, APNG and sprite-sheet reference viewer in the right panel; play/pause, frame stepping and nearest-neighbor zoom. Preset 2D examples remain removed. No duplicate implementation made.

Deferred Windows GUI: verify PNG/sprite-sheet frame layout, GIF/APNG playback, zoom, toggle, and no inclusion in project exports. Existing viewer uses a fixed QLabel rather than a dedicated pan/scroll viewer; consider only if actual testing shows navigation problems.

Next roadmap: audit Phases 10–12 export naming, formats, and data consistency against current source before coding.
