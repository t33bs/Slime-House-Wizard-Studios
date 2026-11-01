# Phase 14 — alpha contribution audit

Added `classify_contributing_source_selection` as a **read-only**, conservative counterpart to the existing topmost-only classifier. An upper partially transparent pixel does not fully hide a lower pixel: both layers may contribute to the composited result. Only a fully opaque upper pixel occludes lower source occurrences. The classifier requires every contributing displayed occurrence of a source pixel to be selected before marking it complete.

Four regression tests cover partial alpha, opaque occlusion, mixed selection footprint and dimension validation. This does not change Slimer destructive-edit authorization; inverse mapping and GUI verification remain pending. Alpha blending and layer effects need additional validation before destructive edits can use this policy.
