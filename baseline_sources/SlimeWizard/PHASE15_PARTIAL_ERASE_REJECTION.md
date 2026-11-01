# Phase 15 — Reject incomplete fallback source erasure

The Slimer fallback erase loop now raises an error when its remaining selection mask is nonempty after processing source layers. Apply Move catches the error and restores source buffers and edit history instead of confirming a partial move.

Validation: 404 passed, 15 skipped, 12 subtests passed in headless pytest. Windows Qt workflow remains unverified. The new test checks the fallback contract in source code; it does not substitute for a Windows GUI regression.
