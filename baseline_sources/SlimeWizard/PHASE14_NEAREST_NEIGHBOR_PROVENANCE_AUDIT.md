# Phase 14: Nearest-neighbor pixel provenance

Added `studio/pixel_source_mapping.py`, a **read-only** source-pixel provenance map that follows `PetSuiteModel.render_part` operations exactly: source nearest-neighbor resize, placement on the full canvas, and Pillow nearest-neighbor rotation about the same anchor. The helper returns 1-based source labels (zero denotes empty canvas) and a unique set of source pixels touched by a selection.

Regression tests compare rendered RGBA against mapped source labels at angles 0, 45, 90, 135 and 270 degrees with nontrivial resizing, plus translation and scaled multi-pixel selections.

**Safety boundary:** This is not wired into Move Original. Rotation/resizing can map one source pixel to several rendered pixels, and deleting the source pixel for a partial canvas selection could remove unselected displayed pixels. Existing destructive-move guards stay in place until an explicit safe policy is designed and tested, including partial selection and overlapping layers.
