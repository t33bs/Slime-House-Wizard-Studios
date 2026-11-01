# Phase 14 — Visible-footprint provenance audit

Added a read-only, topmost-layer-aware source-selection classifier. It uses each layer's exact source-index map and rendered alpha, and counts only exposed canvas pixels. Tests cover overlapping layers, partial occlusion, canvas clipping, resolved-coordinate rotation, and mismatched dimensions.

This helper deliberately does **not** authorize destructive moves: partially transparent top layers also contribute to the final composite, so topmost ownership alone is insufficient for correct removal. Actual Move Original remains guarded on rotated/resized layers. Windows visual verification remains deferred.
