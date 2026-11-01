# Phase 50 — topmost selected opacity

The layered source planner previously checked all selected canvas coordinates against each contributing layer’s alpha, including lower pixels completely hidden by an opaque selected upper layer. This could incorrectly reject a valid multi-layer Move Original operation if the hidden lower pixel was translucent.

The planner now records the selected ownership mask per layer during its top-to-bottom pass and checks fractional alpha only on the actual selected topmost owner pixels. An exposed translucent selected pixel remains rejected. Added model regression for a selected opaque lower pixel plus selected opaque upper pixel covering a translucent lower pixel.

Windows GUI end-to-end verification is still pending. No GitHub changes.
