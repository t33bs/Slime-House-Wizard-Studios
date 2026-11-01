# Phase 1 — Windows tests to run after the repaired portable build is ready

Use a **disposable copy** of a 128x128 Swordcat project. Do not overwrite the original. The automated Linux/headless tests do not verify Qt mouse events.

## A. Slimer drag integrity (NOT VERIFIED ON WINDOWS)
1. Import a transparent Swordcat PNG and save a test copy.
2. Highlight the right foot. Finish Selecting.
3. Drag the selected foot once. Inspect its color and opacity; undo and redo.
4. Repeat drag movements 10 times on a fresh selection, without placing a frame between drags.
5. Confirm all placements. Compare against the original; no unrelated pixels may disappear.
6. Repeat with another highlighted region and check the original remains intact until deliberate Slime Cleaner use.

PASS: no fading, transparent holes, stray clearing, or loss of unrelated pixels; Undo restores exactly.

## B. Place Frame independence (NOT VERIFIED ON WINDOWS)
1. Import a PNG and Place Frame immediately without editing.
2. Make a visibly different right-leg pose; Save Current Pose / Place Frame as appropriate.
3. Create a third distinct leg pose.
4. Switch 1 -> 2 -> 3 -> 1; verify each frame remains distinct.
5. Make 10 successive frames, checking the previous frame after each addition.
6. Export PNG sprite sheet and JSON; inspect each frame. No two different intended poses should become identical.

PASS: earlier frames never change when later frames are edited, and all intended pixels remain.

## C. Save and reopen (POSTPONED AT USER REQUEST)
1. Save a uniquely named disposable creature project containing 3 distinct poses.
2. Close and reopen the same project; check animation selection, frame order, pixels and durations.

## D. GIF/APNG comparison (NOT VERIFIED ON WINDOWS)
Export the same 3-frame animation as sprite sheet PNG, GIF and APNG. Compare all three decoded frames for intended content, alpha, order and duration.

## Recording failures
For any failure, record: frame number, tool/mode, drag count, button clicked, whether Undo restored pixels, and the matching sprite sheet PNG + JSON. A screenshot before and after helps.
