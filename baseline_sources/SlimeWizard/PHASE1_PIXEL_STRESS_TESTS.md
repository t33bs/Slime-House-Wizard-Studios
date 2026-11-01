# Phase 1 — Pixel stress regressions

Added `tests/test_phase1_pixel_stress.py`:
- 100 repeated changes to the middle of three timeline poses; verifies exact bytes of both neighboring poses after each change.
- 200 repeated renders of a translucent sprite; verifies byte-for-byte RGBA stability.

Local result: 212 passed, 433 subtests passed.

Not verified here: Windows GUI Slimer drag behavior, legacy duplicate-layer migration, actual mouse input, or Windows executable packaging.

Deferred Windows checklist remains in `PHASE1_DEFERRED_WINDOWS_TESTS.md`.
