# Phase 1: saved-project structure validation

- Added `studio/project_validation.py` with non-mutating JSON structure validation.
- Validates canvas dimensions, editable parts, pose lists, finite transform values, and positive frame durations before loading source PNGs.
- Invalid data raises `InvalidProjectDataError` with an actionable field location and confirms the project file was not changed.
- `PetSuiteModel.load_project()` validates the manifest before checking asset existence.
- Automated suite: 242 passed, 433 subtests passed.
- Deferred Windows GUI testing recorded in `PHASE1_DEFERRED_WINDOWS_TESTS.md`.
