# Phase 1 consolidated quality-of-life updates

- Added **Import Pose PNG** beside Add Pose and Copy Pose. A PNG matching the creature canvas is inserted as a new independent pose, not a replacement of an existing pose. The full-canvas PNG becomes an editable layer for that pose. Source dimensions are validated; no implicit scaling or cropping.
- Changed sprite sheet export to a **Save As** filename dialog. The matching JSON receives the same basename; the existing `_sheet` naming convention is retained.
- Changed GIF/APNG export to a **Save As** filename dialog selecting a common basename. Each animation still receives its own safe animation-name suffix, and both GIF and APNG are generated. The selected `.gif` path is a basename suggestion, not a promise of exactly that output path.
- Added a regression for imported PNG pose isolation, pixel alpha, and unique pose IDs.

## Verification

- `python -m pytest -q --disable-warnings --maxfail=1`: 218 passed, 433 subtests.
- Windows Qt GUI tests are still required for button visibility, Save As behavior, and imports.
- This package is source code, not a compiled Windows EXE.
