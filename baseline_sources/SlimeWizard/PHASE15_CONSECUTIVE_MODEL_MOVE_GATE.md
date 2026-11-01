# Phase 15 — Consecutive Move Original model regression

Added `tests/test_phase15_consecutive_model_moves.py`. This uses the real `PetSuiteModel`, extracts the production Slimer planner/eraser methods without requiring PySide6, and executes **two consecutive Move Original Pixels operations** on one canvas. Each move creates a distinct editable asset, temporarily hides the staged destination while mapping the original, erases its selected source, and restores destination visibility. The test checks source pixels are removed exactly once, the remaining original pixel survives the first move, and both moved layers remain visible and independent after the second.

This validates the source mapping and erasure logic in a headless model integration scenario. It does **not** exercise Qt event ordering, editing-table transforms, undo/redo, or the complete Windows GUI workflow; those remain unverified.
