# Phase 1 — Project activation and saved pose isolation

## Source change
- Store each creature project's selected timeline index independently.
- Block step-list selection signals during project activation.
- Load the destination animation's saved pose before reinitializing Slimer's source image.
- Hide the Slimer overlay if the destination animation has no saved pose.
- Preserve existing pose snapshots and leave Slimer as the selected tool.

## Verification
- `PYTHONPATH=. python -m pytest -q`: 202 passed, 433 subtests passed.
- Python compilation passed.
- This is NOT a Windows GUI validation or a final confirmation of the original pixel depreciation issue.

## Deferred Windows checks
1. Timeline numbering and reordering.
2. Safe handling/migration of legacy duplicate `Slimer pose` layers.
3. Repeated highlight, drag, Place Frame pixel integrity.
4. Recovery of existing timeline poses.
5. Switching projects with Slimer active, including empty animations.
