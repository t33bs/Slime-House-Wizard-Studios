# Phase 14 — Pose source copy-on-write audit

Added `PetSuiteModel.erase_pose_source_pixels(animation, frame_index, part_index, indices)`.

The method validates its target, decodes only the target frame's saved `source_png`, applies the existing source-pixel erase helper to a fresh image, and stores an independent replacement snapshot. Other frames and live part/original buffers are untouched. A change creates a recovery version; a no-op does not.

Four new headless tests cover frame isolation, recovery, invalid targets, and no-op handling. Full suite: 319 passed, 1 skipped, 441 subtests passed.

**Not yet wired to Slimer UI.** The caller must validate pixel provenance and selection completeness before invoking this method. Windows GUI verification remains deferred.
