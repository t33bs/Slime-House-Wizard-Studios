# Phase 68 — partially clipped Move Original destination

Production fix: the existing Apply Move guard rejected a fully off-canvas destination, but accepted a partly visible destination even when some selected pixels would disappear beyond the canvas edge. For unrotated staged Move Original layers, inspect the alpha bounding box of the actual editable asset after its current resize/translation. Reject a partially clipped destination without erasing source or discarding the staged layer. Copy Pixels remains free to crop intentionally. Rotated destinations retain existing behavior pending a transform-aware clipping check.

Added a Windows/PySide6 GUI regression that first tries a partly clipped move, then repositions the same staged layer and successfully applies it. GUI verification remains pending where PySide6 is unavailable.
