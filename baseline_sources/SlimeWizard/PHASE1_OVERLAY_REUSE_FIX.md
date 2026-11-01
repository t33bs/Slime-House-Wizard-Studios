# Phase 1: Slimer pose overlay accumulation correction

## Confirmed observation from FA v0.47.0
Each click of Place Frame with an active Slimer selection added another asset named `Slimer pose`. This can create stacked artwork layers. This patch changes the code path to create one dedicated `Slimer pose overlay` layer and reuse it on later Place Frame placements. A new frame still gets an independent per-frame source_png snapshot; previous poses should not be rewritten by subsequent placements.

## What was changed
- Reuse the dedicated Slimer overlay part rather than appending a new `Slimer pose` asset for each placement.
- Composite the new selected pixels onto the existing overlay, keeping earlier selected pixels in the active pose.
- Keep `Place as Layer` as a separate explicit operation that creates a new editable part.
- Add model and source-wiring tests for 10 consecutive placements and previous-frame pixel preservation.

## Limitations
- Not verified in the actual Windows GUI. Existing older projects may already contain multiple `Slimer pose` layers; this patch does not delete or merge those, to avoid losing artwork.
- The overlay is a combined layer; independent color selection tabs are planned for later phases.
- This does not prove that all pixel degradation is repaired. Test repeated dragging and saving in a disposable project.

## Windows verification checklist
1. Create a new disposable 128x128 creature with one PNG asset.
2. Highlight a foot, place a frame, repeat at least 5 times. Check that the Asset Library gains at most one `Slimer pose overlay` entry from these Place Frame actions.
3. Verify frame 1 retains its original foot when frame 2 is edited; repeat through frame 5.
4. Move the same selection multiple times with drag; compare pixels and opacity with the original PNG.
5. Export the sprite sheet PNG/JSON and check every intended pose is distinct and complete.
6. Save and reopen the project; check the frames and layer visibility.
