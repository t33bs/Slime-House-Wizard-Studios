# Slimer preview render isolation

- During highlight painting, do not call `slimer_preview()` at all. The canvas uses the raw selection mask bounds and highlight tint only.
- After Finish Selecting, generate the transformed selection once per refresh and reuse it for both the canvas and right-side preview.
- Returning to Edit Selection hides the preview and stops generating the transformed image.
- Selection/placement logic is unchanged.
- Windows verification remains queued in `PHASE1_DEFERRED_WINDOWS_TESTS.md`.
