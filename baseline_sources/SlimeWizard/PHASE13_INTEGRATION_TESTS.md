# Phase 13 — Integration regression coverage

Added `tests/test_phase13_export_integration.py`: builds a two-animation project with independent poses and partially transparent artwork, saves and reloads it, checks exact atlas pixels and JSON durations, checks GIF/APNG frame counts and loop, checks APNG exact frame pixels/timing, and verifies exporting does not mutate the project fingerprint.

Result: `247 passed, 1 skipped, 433 subtests passed` using `python -m pytest -q`.

Remaining GUI checks are recorded in `PHASE1_DEFERRED_WINDOWS_TESTS.md`. The skipped GUI-dependent test is not claimed as passed. No Phase 1 rework was performed.
