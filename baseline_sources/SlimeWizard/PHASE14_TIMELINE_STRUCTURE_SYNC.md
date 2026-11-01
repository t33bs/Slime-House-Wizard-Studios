# Phase 14: timeline structural edit playback synchronization

Changes: structural pose edits now call `_timeline_structure_changed`, which reuses `restart_playback` to reset elapsed preview time and rebase the monotonic clock without changing the Play/Pause toggle. Affects add, duplicate, copy, import, delete and shift. Does not change pose pixels, project format, or export logic.

Automated verification: 271 tests passed, 439 subtests passed, one GUI-dependent test skipped. Windows manual checks added to PHASE1_DEFERRED_WINDOWS_TESTS.md.
