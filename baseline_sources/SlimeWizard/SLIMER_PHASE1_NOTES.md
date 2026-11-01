# Slimer Tool — Phase 1 foundation

Added `studio/slimer_tool.py` with pixel-mask painting/erasing, non-destructive copy (default), optional move-original, nearest-neighbor resize/rotation, and compositing on transparent RGBA images. Added five regression tests in `tests/test_slimer_tool.py`.

**Not yet connected to the app UI:** the Slimer selection brush, preview handles, Place Frame, Place as Layer, and their integration with Undo/Redo are still pending. Existing undo/redo works for model edits, but Slimer operations must be wired as a single recorded transaction before shipping. This is a source-code development snapshot, not a new portable EXE or installer.

Existing Windows portable/installer GitHub Actions workflow and version 0.47.0 were left unchanged.
