# Deferred Windows verification — Phase 1

These four checks are intentionally postponed until a usable Windows build:

1. Verify Slimer Pose 001/002/... labels in the Asset Library match timeline pose positions, including reordering.
2. Safely migrate old projects containing multiple legacy `Slimer pose` layers; preserve legitimate artwork.
3. Repeatedly highlight, drag, place frames, switch poses, and compare pixel-exact exports for loss or stale overlays.
4. Verify pose recovery in the UI, including save/reopen, reorder/delete, and recovery of the correct timeline pose.

## Source progress

- Added bounded (5-entry) per-pose recovery history in `PetSuiteModel` for `save_pose_at` and `edit_pose_at`.
- Recovery is currently in-memory only; no UI command or on-disk persistence has been added.
- Recovery keys currently use animation name and frame index; timeline insertion/deletion/reordering still require stable-ID handling before production use.
- No claim is made that the original pixel depreciation bug is fixed.

## Additional verification queue (October 28)
- Finish Selecting: visible movable selection and transform handles.
- Asset Library: selecting a row loads correct X/Y/width/height/rotation; active label tracks selection.
- Save/reopen: independent Slimer layers, timeline poses, pose recovery, settings and source PNGs persist.
- Export: custom Save As names, sprite-sheet JSON, PNG/GIF/APNG transparency and frame timing.
- Import Pose PNG: new independent pose, no overwrite of existing poses.
- Project save failure/interruption: confirm previous project remains recoverable; JSON atomic replace is implemented but asset PNGs are not yet transactionally saved.

## Versioned asset save / recovery (2026-10-28)
- Save a project twice with different source PNGs; close and reopen; confirm latest pixels and timeline.
- Simulate an interrupted save / crash recovery on Windows and confirm the last committed project remains intact.
- Review old versioned asset folders and decide a safe cleanup/backup-retention policy before enabling automatic pruning.

## Slimer preview timing (2026-10-28)
- While painting highlights, verify no floating selected-pixel result appears over the highlighting area or in the right-side Slimer Preview.
- Press Finish Selecting: verify the right-side selected-pixels preview appears and the floating result becomes movable on canvas.
- Press Edit Selection: verify the preview disappears again while the highlight mask remains editable.
- Confirm Place Frame / Place as Layer still use the selected pixels correctly.

## Lazy preview rendering follow-up
- Highlight rapidly on a detailed creature and confirm no preview flashes over the painting region, including after undo/redo and color changes.
- Confirm the right preview and floating selection match exactly after Finish Selecting, moving, scaling and rotating.

## Asset version management (new)
- Confirm multiple Save operations preserve the current artwork and older version folders.
- Confirm recovery can open previous snapshots before any cleanup UI is enabled.
- Review proposed old-version cleanup in the Windows UI; no automatic cleanup is enabled.
- Verify backup/recovery references across directories before exposing destructive cleanup.

## External backup cleanup safeguard
- Locate all Windows project backup/recovery directories; confirm old asset versions referenced from outside the project folder remain protected.
- No deletion UI should be enabled until backup inventory and retention policy are established.

## Read-only recovery report
- Verify active, older available, and missing referenced versions match actual Windows project and backup folders.
- Verify unreadable backup manifests and missing backup locations produce warnings; do not enable deletion.
- Decide whether/how to expose a beginner-friendly recovery report in the UI after testing.

### Missing artwork recovery (deferred Windows UI)
- Open a copied project whose active versioned PNG folder is missing: clear error must list missing files and must not open a partial creature.
- Verify original JSON and existing artwork are unchanged after failed open.
- Restore backup PNG folder and reopen successfully; verify poses, layers, and preview.
- Check long error text is readable in Windows message dialog.

## Saved-project validation (2026-10-28)
- [ ] Open a damaged JSON project: readable error, no overwrite or partial editor replacement.
- [ ] Open a project with invalid canvas dimensions, malformed pose lists, or bad frame durations: identify the problematic field.
- [ ] Confirm legacy valid projects still load, and successful project switching preserves the current workspace.

## Phase 4 — Color tabs
- Switch between Start/Middle/End and custom tabs: verify masks and X/Y/rotation/scale remain independent.
- Add enough custom tabs to require scrolling; confirm all remain reachable.
- Change the selected tab's highlight color; confirm other tabs unaffected.
- Confirm tab switching with Finish Selecting / Edit Selection and across timeline poses.

## Phase 5 — Confirm All Placements
- Confirm two or more color tabs place as a single independent layer with their own transforms.
- Confirm Undo/Redo, Move Original vs Copy Pixels, transparent RGBA, overlapping selections and frame isolation.
- Confirm preview stays hidden during highlighting, and selection tabs remain editable until confirmation.

## Phase 6 (2026-10-28)
- [ ] Edit Selection/Finish Selecting repeatedly without losing masks, transformations, or source pixels.
- [ ] Switch among color tabs and verify Undo/Redo applies only to the selected tab, including after returning from another tab.
- [ ] Verify no stale tab history after clearing Slimer or switching creatures.

## Original roadmap Phase 7/8 UI verification
- Confirm Slimer Preview stays in the right panel and remains hidden while highlighting.
- Verify updated Slime Buddy instructions match color tabs, Finish Selecting, Edit Selection, and Confirm All Placements; OFF suppresses tips.
- Check narrow window layouts and tooltip readability.

## Original roadmap Phase 9 reference viewer
- Load a PNG, GIF, APNG, and multi-frame sprite sheet; verify frame order, playback timing, frame step, nearest-neighbor zoom and hide/show.
- Confirm user references never enter creature project exports.

## Roadmap Phases 10–12 — animation export naming
- [ ] Export GIF + APNG and confirm both appear with distinct `.gif` and `.apng` extensions in Windows Explorer.
- [ ] Confirm chosen base filename, animation-name suffix, transparency, loop, and frame timing in actual Windows viewers.
- [ ] Check that older `.png` APNG files remain readable (no migration required).

## Phase 13 — End-to-end integration (2026-10-28)
- [ ] On Windows, create and save multiple independent poses with transparent pixels, reopen the project, and compare the preview against each pose.
- [ ] Export sprite sheet + JSON, GIF, and APNG; verify files open in target Windows apps and playback preserves frame order, timing, loop and alpha as supported.
- [ ] Exercise multi-color Confirm All Placements and Slimer Undo/Redo through a save/reopen cycle (GUI-dependent; not validated by headless integration test).

## PNG integrity preflight (2026-10-28)
- [ ] On Windows, open a copied project with one corrupted/truncated PNG: confirm a readable error names the artwork file and no partial creature replaces the current workspace.
- [ ] Confirm the original JSON and PNG files remain unchanged; restore a valid PNG and reopen successfully.
- [ ] Confirm older projects with `part_###.png` still load.

## Export all frames (2026-10-28)
- [ ] Click Export All Frames and choose a base filename; verify every saved pose exports as an individual transparent PNG, plus timing JSON.
- [ ] Check colliding animation labels, Windows filename behavior, frame order and playback timing in downstream tools.
- [ ] Confirm exporting does not change the current pose, selection, or artwork.

## Post-roadmap pose navigation
- [ ] Previous/Next frame buttons navigate actual saved timeline poses (not hidden recipe steps); test first/last bounds, switching animations, and unsaved edits.

## Phase 14 — Playback clock (deferred)
- [ ] Playback 0.5x/1x/2x remains accurate under load.
- [ ] Pause/resume does not count paused time or jump frames.
- [ ] Non-loop playback ends on final pose; looping playback wraps cleanly.
- [ ] Duration edits and animation switches show correct preview timing.

### Animation switching and playback (post-roadmap)
- Switch between two saved animations while playback is running; new animation should start at its first pose without a timing jump.
- Switch animations while paused; the new animation should display its first pose and remain paused.
- Change playback speed and repeat mode while running; verify timing resets deliberately and no stale clock time is inherited.
- Edit a pose duration while playing; verify the preview follows the new duration without unexpected frame changes.

## Phase 14 — Live duration editing (2026-10-28)
- [ ] While preview plays, change duration of current pose; confirm playback retains relative progress instead of jumping to a different pose.
- [ ] Change duration of earlier/later poses during playback, including looped playback, Slow/Fast modes, and paused preview.
- [ ] Confirm duration edit Undo/Redo and exported GIF/APNG/JSON timing remain consistent.

### Phase 14 — playback completion and resume (deferred Windows GUI)
- [ ] With Loop off, play a short animation to completion, then press Play again: starts at pose 1 and advances normally.
- [ ] Pause midway, then resume: continues from the paused position rather than restarting.
- [ ] With Loop on, playback continues seamlessly across cycle boundaries.
- [ ] Press Play on an empty animation: remains stopped, gives a helpful message, and later playback works after adding a pose.

## Phase 14 — timeline structural edits during playback (2026-10-28)
- While preview is playing and paused, add, duplicate, copy, import, delete, and shift poses; confirm the preview starts at the beginning of the updated timeline and Play/Pause state is preserved.
- Remove the final pose while playing; confirm no stale frame appears and playback stops or shows the empty-timeline prompt appropriately.
- Rapidly reorder poses during playback and confirm no timing jump, frozen preview, or overwritten pose artwork.

## Phase 14 — Timeline Undo/Redo playback synchronization
- [ ] While playing, add/copy/delete/reorder a pose; Undo and Redo; verify playback starts cleanly with restored pose order and remains in the chosen Play/Pause state.
- [ ] Undo an ordinary pixel edit while playing; verify the preview updates without an unnecessary timeline restart.
- [ ] Undo removal of the final pose and verify timeline selection and playback controls stay usable.

## Phase 14 pose identity history
- Copy a pose, Undo and Redo: confirm pose selection, pixels, timeline thumbnail, and recovery versions remain matched.
- Delete a pose with a previous saved version, Undo: confirm Restore Previous Pose still targets the original pose.
- Reorder poses, Undo/Redo and switch animations: confirm no stale selected pose or preview.

- [ ] Phase 14: Undo/Redo after deleting or reordering poses: verify highlighted timeline row, canvas artwork, and right-side preview show the same restored pose. Test when selected pose was deleted (fallback selection) and while preview is playing.

### History/Slimer synchronization audit (2026-10-28)
- With an unfinished highlighted Slimer selection, perform model Undo/Redo and verify stale highlight, preview and transform handles are cleared; saved artwork remains correct.
- Undo/Redo after switching animations; verify animation selector, timeline selection, canvas and Slimer source agree.
- Verify undoing a Slimer stroke still uses the Slimer-specific undo path and does not clear unrelated selections.

- [ ] Slimer Clear Selection after Finish Selecting clears floating handles/drag mode and permits fresh highlighting; repeat after Confirm All Placements.

- [ ] Slimer color tabs: switch A -> B after Finish Selecting; confirm A handles disappear, B highlights are editable, and returning to A preserves its mask/transform numbers.

- Phase 14 inherited-transform erase: attached child with parent rotation or inherited translation must refuse Move Original without changing artwork or Undo stack; Copy Pixels remains usable; untransformed independent layer still moves normally.

- [ ] Phase 14 exact translation mapping: Move Original on a child translated by an attached parent clears the displayed pixel's actual source coordinate, preserves overlapping layers, and Undo restores it; rotated/resized layers still refuse destructive moves.

- [ ] Phase 14: With an enlarged/rotated pixel, partially highlight its rendered footprint; Move Original must never erase unselected occurrences. Verify complete-footprint selection and overlapping layers separately when transformed erase is implemented.

- [ ] Verify Slimer Move Original behavior with overlapping translucent layers, inherited rotations, and clipped artwork before enabling transformed-layer erasure (Phase 14 topmost provenance audit).

- [ ] Verify partially transparent upper parts over lower parts when Slimer selects overlapping regions; compare previews and resulting PNG alpha against expected composites (Phase 14 alpha contribution audit).

- [ ] Phase 14: after future source-erase preflight integration, visually test fully selected enlarged/rotated pixels, partial selections, overlapping alpha layers, Undo, and saved pose isolation on Windows.
