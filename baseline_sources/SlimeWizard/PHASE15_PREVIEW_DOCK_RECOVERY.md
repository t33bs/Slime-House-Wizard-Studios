# Phase 15 preview dock restore and rejected-move contract

- Restoring an older saved splitter layout now reserves at least 235 pixels for the right-hand comparison dock, rather than allowing it to shrink to 100 pixels and clip both previews.
- The comparison panel also has a 235-pixel minimum width and starts visible; the user can still hide it with the existing toggle.
- A source-safety rejection in `_slimer_commit` now consistently returns `False` to callers; it does not report a successful Apply Move.
- Added static regression checks for dock visibility and explicit failure returns.
- Linux checks: Python compilation succeeded; 343 tests passed, 4 GUI-dependent tests skipped, 441 subtests passed.
- This does NOT confirm the Windows Apply Move / Place Frame source-provenance failure is resolved. Preserve existing uncommitted Windows work and do not overwrite it without a backup.
