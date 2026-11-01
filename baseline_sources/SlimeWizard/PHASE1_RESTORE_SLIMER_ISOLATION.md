# Phase 1 — Restore pose / Slimer selection isolation

- After Restore Previous Pose reloads the selected saved timeline pose, reset transient Slimer selection masks, cached source pixels, drag state and transform controls.
- Keep the Slimer tool selected if active. Do not remove any persistent artwork layers or modify other timeline poses.
- This prevents a selection created against the discarded version of a pose from being applied to the recovered version.
- Two regression tests added: restore control resets Slimer *after* reloading the recovered pose; model restoration does not alter a neighboring timeline pose.
- Deferred Windows checks remain required, especially real dragging and overlay behavior. This does not establish the root cause of earlier pixel degradation.
