# Slimer clear-state audit

Found that Clear Selection reset masks and transforms but left the canvas in finished-selection transform mode, with stale bounds and drag toggle. Updated the clear path to reset these transient UI states without changing artwork or pose data.

Windows check: finish selecting, move/rotate, clear, then paint a new highlight; ensure no old handles or drag state reappear. Repeat after Confirm All Placements.
