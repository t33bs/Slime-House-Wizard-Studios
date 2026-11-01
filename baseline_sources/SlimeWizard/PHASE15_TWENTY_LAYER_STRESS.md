# Phase 15: twenty-layer persistence stress gate

Added `tests/test_phase15_twenty_layer_stress.py` to exercise 20 independently named assets with per-pose transforms across save/reload and repeated pose switching. The older pose intentionally predates the layers; the test verifies they remain hidden there. This is a model-level test, not 20 consecutive GUI Slimer Apply Move operations. GUI validation on Windows is still required.

Automated result: 395 passed, 10 skipped, 12 subtests passed. Timeline drag reorder remains deferred. GitHub working tree was not modified.
