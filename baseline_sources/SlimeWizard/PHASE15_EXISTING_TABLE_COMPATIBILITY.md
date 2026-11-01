# Phase 15 — existing editing table compatibility

- The existing X/Y/size editing table remains in place.
- During a staged Slimer Edit Selection transaction, edits to any other asset through X/Y/size and rotation are rejected and the controls restored to that asset's actual values. This protects the frozen source image while allowing destination-layer edits.
- Added a Windows/Qt GUI regression covering three consecutive Copy Pixels selections, X/Y and rotation edits through the existing table, source-asset edit rejection, and independent layer identities.
- Headless test result: 395 passed, 11 skipped, 12 subtests passed. Qt test is skipped in the headless environment; run it on Windows before declaring GUI integration verified.
- GitHub working tree was not modified.
