# Phase 66 — asset editing table: avoid unnecessary layer resampling

The X/Y spinboxes used to call `model.resize_part` for **every position change**, even when width and height had not changed. On large full-canvas Slimer layers, this unnecessarily regenerated the image for each step. The table now resolves aspect-lock dimensions before comparing geometry, records history only when something actually changes, and calls `resize_part` only for actual size changes. Translation preserves the image object and pixel data.

Added `tests/test_phase15_edit_table_no_resample.py` for 30 successive X edits, no-op edits, and genuine resizing. This is a production-code performance/correctness change, **not** a confirmed fix for the Windows consecutive Apply Move issue. Run GUI regression tests on Windows.
