# Slimer preview timing

The right-side Slimer Preview and the floating selected-pixel composite are now gated by the existing `slimer_transform_mode` (entered via Finish Selecting). During highlighting, only the highlight tint is shown on the canvas. Editing the selection hides the generated result again. The selection mask and existing Place Frame/Place as Layer paths are unchanged.

Windows visual checks are queued in PHASE1_DEFERRED_WINDOWS_TESTS.md.
