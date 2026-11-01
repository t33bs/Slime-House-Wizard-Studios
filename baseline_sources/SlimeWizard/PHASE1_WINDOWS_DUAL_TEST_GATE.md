# Phase 1 Windows dual test gate

The Windows GitHub Actions workflow now runs both `unittest discover` and `pytest -q tests` before packaging. This closes a verification gap: the previous workflow ran only unittest, while the local project also tracks pytest integration coverage. Both logs upload even if the respective suite fails. Packaging is blocked on either failure.

Local Linux validation: 189 unittest tests passed; 214 pytest tests plus 433 subtests passed. Windows workflow was **not** executed here. Portable EXE and installer remain unbuilt/unverified. Deferred Windows GUI manual tests remain required before closing Phase 1.
