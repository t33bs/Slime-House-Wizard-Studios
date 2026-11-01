# Phase 14 — inherited transform and inverse-coordinate investigation

## Finding
Move Original erases pixels using each part's raw x/y and source-image coordinates. However render() uses resolved_pose(), which applies parent attachment transforms. A child may be rotated or repositioned by its parent while its local angle remains zero, so the previous guard could permit unsafe erasure.

## Change
The guard now checks resolved_pose() for each visible part, refusing Move Original if the effective angle is nonzero, the effective x/y differs from the editable part x/y, or the effective dimensions differ from the source image. Copy Pixels remains available. No inverse mapping or source pixel resampling is introduced.

## Why not inverse-map immediately?
The renderer uses nearest-neighbor rotation on a canvas and may map multiple destination pixels to one source pixel or leave holes. Inverse erasure must use the exact renderer mapping and a defined policy for source pixels that contribute to multiple destination pixels; naive trigonometric inverse rounding risks deleting unrelated pixels. This requires dedicated mapping tests before implementation.

## Deferred Windows checks
Rotate parent of an attached child, highlight child pixels, verify Move Original refuses without editing; Copy Pixels still places; parent translation causing resolved position offset is blocked; ordinary untransformed artwork remains movable.
