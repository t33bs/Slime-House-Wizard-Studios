# Phase 2 — Windows checks (not yet verified)

Use a disposable project and keep a backup. The old pixel-loss issue remains unverified.

1. **Place Frame without edits**: import a 128x128 transparent PNG; press Place Frame immediately. Expect one new pose.
2. **Save Current Pose isolation**: make three poses, select Pose 2, change one part's X coordinate, click Save Current Pose; confirm Poses 1 and 3 are unchanged.
3. **Switch and restore**: select Pose 1, Pose 3, then Pose 2. Pose 2 must retain its saved geometry and artwork.
4. **No silent duplication**: change Pose 3's leg; select Pose 2. Pose 2 must not become Pose 3.
5. **Frame insertion at same row**: create a pose after the selected frame, switch away and back. The new pose must load its own snapshot even if the timeline previously had the same selected row index.
6. **Slimer selections**: check whether Place Frame preserves unfinished selection state. This is not yet fixed and remains part of later Slimer phases.
7. **Save/reopen**: postponed at user's request until after other fixes.

Export the sprite sheet PNG and JSON and compare all poses. Do not use original artwork for these tests.
