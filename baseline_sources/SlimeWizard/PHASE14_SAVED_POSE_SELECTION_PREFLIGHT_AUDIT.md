# Phase 14 — Saved-pose selection preflight

Implemented `PetSuiteModel.erase_selected_pose_pixels` as a model-level, single-visible-part workflow. It calculates nearest-neighbor source provenance from the saved pose's geometry, checks rendered alpha, requires complete source-pixel footprints, and delegates to copy-on-write `erase_pose_source_pixels` for frame isolation and recovery.

The operation refuses attached rigs, multiple visible parts, mismatched canvas masks, transparent/outside-source selections, and partially selected transformed footprints. It does not modify live buffers or other saved poses. It is not yet wired to the Slimer UI; multi-layer alpha-composited edits and rig-resolved geometry remain future work.

Verification: 323 passed, 1 skipped, 441 subtests passed; Python compilation checked. Windows GUI testing remains deferred.
