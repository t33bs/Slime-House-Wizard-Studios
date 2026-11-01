# Phase 58 — Single-source Edit Selection rendering

Edit Selection now renders the current creature once and uses that exact RGBA snapshot for both stale-selection validation and extraction into a provisional editable layer. Previously it rendered twice, wasting a full compositing pass on 512x512 and 1024x1024 projects.

New regression tests cover single-render successful staging and stale-source rejection. The Move Original/Copy Pixels policies, asset workflow, and pose navigation are unchanged.

Validation: 428 passed, 17 skipped, 12 subtests passed. Windows GUI tests still require Windows/PySide6.
