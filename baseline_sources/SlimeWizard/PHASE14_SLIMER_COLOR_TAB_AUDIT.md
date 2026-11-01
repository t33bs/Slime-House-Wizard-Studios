# Phase 14: Slimer color-tab transition audit

Switching from a finished color selection to another tab could leave the previous tab's floating transform mode and handles active. Tab switching now exits transform mode, clears drag/handle state, and preserves each tab's stored mask, transforms and selection history. The incoming tab can be finished again when the user wants to transform it.

Windows-only check: finish and drag a selection in color A, switch to color B, verify no A handles or drag behavior, then switch back to A and verify its mask and numeric values remain.
