# Phase 62 — resized Slimer layer and three-move GUI regression

- Added a production-method regression test: create a Slimer layer, resize it, apply Move Original, select the newly scaled pixels, then create and apply another Move Original layer. Checks source removal and destination integrity.
- Expanded the Windows/Qt asset-editing-table regression from two moves to three. The third move selects a pixel from the Slimer layer produced by the first move, testing real consecutive-layer ownership and table-based positioning.
- No production source logic was modified in this phase. This is a test-coverage checkpoint, not a claim that the previously observed Windows GUI bug is fixed.
- Automated suite: 437 passed, 17 skipped, 12 subtests passed. Qt GUI test skipped in this Linux environment; must run on Windows with PySide6.
