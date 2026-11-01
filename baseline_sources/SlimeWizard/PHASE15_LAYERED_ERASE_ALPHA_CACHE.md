# Phase 60 — Reuse rendered layer opacity during Slimer source preflight

The top-down ownership scan renders each visible layer to inspect opacity. The subsequent provenance scan previously rendered those same layers again. Cache the opacity images during the ownership pass, and reuse them in provenance. Layers not reached by the ownership scan are still rendered on demand, preserving occlusion classification and existing safety rules. No change to the source-erasure algorithm, selected pixels, or Move/Copy behavior.
