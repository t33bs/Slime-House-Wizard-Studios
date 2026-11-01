# Phase 15 — Occluded stale-source provenance fix

The layered Move Original Pixels preflight now walks the visible layer stack from top to bottom to identify the actual contributing layers at selected pixels. A lower layer completely hidden by a selected upper layer is not source-validated and cannot veto the safe move due to stale cached artwork.

Added `tests/test_phase15_occluded_stale_source_model.py` reproducing a stale cached lower layer covered by a valid top layer.

Validation: 408 passed, 16 skipped, 12 subtests passed. Windows GUI verification is still outstanding; this does not certify consecutive GUI Apply Move operations.

Worktree safety: separate extracted development copy; no GitHub repo modifications.
