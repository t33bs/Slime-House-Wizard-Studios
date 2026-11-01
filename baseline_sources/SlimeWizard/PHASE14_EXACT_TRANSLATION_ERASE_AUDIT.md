# Phase 14 — Exact translation mapping for Move Original

The renderer draws each part at its resolved pose coordinates. The destructive Slimer erase previously used raw part coordinates, so it could not safely handle a part whose resolved x/y differs from its stored x/y. The guard blocked these translations.

This change permits a pure resolved translation when effective rotation is zero and rendered dimensions equal source dimensions. The erase operation maps the canvas selection into source coordinates using resolved x/y, preserving exact nearest-neighbor pixels without resampling. Rotation and resizing remain blocked. A regression test checks a simulated inherited position offset and the exact erased source pixel; the overlapping-layer regression fixture now supplies resolved positions.

Windows visual validation remains deferred. In particular, verify parent-attached translations, layer overlap, off-canvas placement, and Undo/Redo before release. This is not an implementation of rotation/scale inverse mapping.
