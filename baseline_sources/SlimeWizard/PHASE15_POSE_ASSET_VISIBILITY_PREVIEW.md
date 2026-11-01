# Phase 15 source preview — pose-specific asset removal

Added **Remove asset from this pose** and **Restore asset in this pose** to the asset library. Removal is non-destructive: it sets the selected asset invisible in the selected saved pose and saves that pose only, retaining the shared asset in the library so other poses remain intact. Restore makes it visible again. Undo/Redo uses the existing history mechanism.

This is a first pass, not true physical deletion from the asset list. A later UI iteration can display removed assets separately or filter them by pose while retaining stable rig indices.

Tests in this environment: 328 passed, 2 skipped, 441 subtests passed. GUI behavior requires Windows validation. Do not replace the known-good release without testing.
