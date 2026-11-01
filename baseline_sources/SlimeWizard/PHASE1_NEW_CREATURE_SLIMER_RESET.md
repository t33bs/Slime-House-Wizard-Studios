# Phase 1: New Creature / Slimer state isolation

## Reported intermittent issue
Slimer remained active while New Creature was clicked. The new creature initially appeared blank; later a full-canvas highlight unexpectedly showed artwork from an older Swordcat pose. This could not reliably be reproduced and the root cause remains unconfirmed.

## Source change
`activate_project()` now invokes `_reset_slimer_for_project_change()` immediately after switching to the destination creature model. This clears transient selection masks, undo/redo for selections, in-progress pointer drags, transform bounds, and numeric offsets. It reinitializes Slimer's selection source from the newly active model's render. The Slimer tool stays selected if it was active. Existing creature parts, frames and saved poses are not deleted.

## Verification
3 source-level contract tests passed for the New Creature path; 2 prior overlay-reuse tests passed. These tests do not simulate Windows mouse events or prove the intermittent ghost-art bug is resolved. A real GUI regression test remains necessary.

## Windows test
1. Open a Swordcat creature with visible art; activate Slimer and highlight part or all of the image.
2. Without turning Slimer off, click New Creature.
3. Confirm the new creature canvas remains blank; drag/highlight the entire blank canvas and verify no old pixels appear.
4. Switch back to the original creature; confirm its artwork and poses remain intact.
5. Repeat with an unfinished selection and after Place Frame. Verify no old overlay or selections appear in the new creature.

## Known limits
Old duplicate Slimer pose layers in existing projects are not automatically deleted. The previous overlay-reuse change is retained, but its GUI behavior is unverified.
