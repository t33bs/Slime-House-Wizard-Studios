# Phase 1 — Duplicate Pose snapshot audit

Observed in source: Duplicate Pose previously called `insert_frame` without an explicit source pose. That captured the current working canvas, not necessarily the selected saved timeline pose. It also appended rather than inserting after the selected pose.

Change: Duplicate Pose now calls `copy_frame(animation, selected_index)` after preserving pending edits, then loads the independent copied snapshot. The model assigns a new stable pose ID and preserves other poses' IDs and recovery history. Empty timelines now request Place Frame first.

Automated tests: duplicate pose model deep-copy isolation, GUI wiring contract, and full unittest suite. Windows GUI testing remains deferred.
