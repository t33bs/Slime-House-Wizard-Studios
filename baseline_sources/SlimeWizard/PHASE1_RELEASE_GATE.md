# Phase 1 release gate — 2026-10-28

Added tests/test_phase1_release_pixel_integrity.py with two tests:
- Three distinct pose images preserve exact RGBA bytes after project save/load and sprite-sheet export.
- A newly constructed creature contains no pixels or timeline frames from an older creature.

Results in this environment:
- python -m unittest discover -s tests -q: 187 tests passed.
- python -m pytest -q: 210 tests passed and 433 subtests passed.

These tests do not simulate the actual PySide6 Slimer mouse/highlight/Place Frame UI or prove the intermittent pixel depreciation is fixed. The existing Windows workflow builds the portable and installer artifacts when run in GitHub Actions; no Windows executable was built here.

Deferred Windows checks: timeline numbering/reordering, old duplicate Slimer layers, repeated Slimer drag/Place Frame pixel integrity, pose recovery, and semi-transparent pixel preservation.
