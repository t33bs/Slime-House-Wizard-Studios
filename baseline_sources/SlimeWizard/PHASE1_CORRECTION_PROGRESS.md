# Phase 1 correction progress (partial)

- Fixed `SlimerSelection.transform` to paste the RGBA piece without using its own alpha channel as a second paste mask. This prevents semi-transparent sprite pixels from losing opacity twice in the selection preview.
- Added three regression tests covering semi-transparent pixels, Move Original source immutability at the selection primitive level, and independent model pose snapshots.
- These tests pass. They do **not** establish that the UI's Place Frame workflow or repeated Move Original commits are repaired. Those critical integration bugs remain open.
- Next: trace `_slimer_commit`, `preserve_pose_draft`, and timeline selection signals in the GUI; test ten consecutive moves/placements with saved frames and export comparisons.

- Follow-up guard in `_slimer_commit`: preserve an edited current pose **before** importing the new Slimer layer. This prevents a pending draft from being saved with the next frame's newly added layer. Reset draft-dirty before switching to the newly inserted pose.
- This is a targeted potential frame-leak repair; the full GUI overwrite/pixel-loss bug is not yet verified fixed.
