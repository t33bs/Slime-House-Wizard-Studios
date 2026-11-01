# Phase 15 — Cross-project timeline isolation gate

Added `tests/test_phase15_cross_project_timeline_isolation.py` with two tests:
- Repeatedly load two separately saved projects, including a historical recipe-name animation and a custom animation; assert selected animation, independent names, exact frame durations, playback boundaries, frame pixel fidelity, and project fingerprints.
- Export sprite sheets for both projects and verify metadata durations and pixel-perfect frame crops, without mutating either model.

`PYTHONPATH=. python -m pytest -q`: **346 passed, 8 skipped, 12 subtests passed**.
Windows GUI verification remains outstanding. Original safety backup and GitHub checkout untouched.
