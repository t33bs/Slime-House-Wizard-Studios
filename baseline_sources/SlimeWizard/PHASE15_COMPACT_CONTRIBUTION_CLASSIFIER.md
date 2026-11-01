# Phase 65 — compact multi-layer contribution classification

The Move Original source classifier previously converted every full-canvas 32-bit provenance map and 8-bit alpha image to Python integer lists, creating large temporary allocations for each layer. It now reads packed `memoryview` buffers and uses a `bytearray` for the opaque coverage mask. The classification and source-erasure policy remain unchanged.

New tests cover a sparse 1024×1024 canvas with opaque occlusion and a translucent overlay that must not hide an unselected lower-layer occurrence. GUI-only tests still require Windows/PySide6. This does not claim the consecutive Windows editing-table issue is fixed.
