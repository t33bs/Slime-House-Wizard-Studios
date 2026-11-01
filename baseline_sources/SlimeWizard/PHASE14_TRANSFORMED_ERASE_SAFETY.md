# Phase 14 — transformed-layer Move Original safety

Audit confirmed that `_slimer_erase_original_layers` maps canvas pixels to source images with a plain x/y crop. This is not valid for rotated layers or images resized relative to their originals. The new preflight refuses Move Original when a visible layer has a nonzero rotation or mismatched source/image dimensions, before recording history or modifying any artwork. Copy Pixels remains available. This is a safety guard, not inverse-coordinate erasure support.

Windows verification: rotate a layer, highlight pixels, try Move Original (should refuse without altering pose); switch to Copy Pixels (should place); repeat with resized source and verify undo/redo. Follow-up implementation: inverse-mapped erasure for transformed layers.
